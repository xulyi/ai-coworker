#!/usr/bin/env node
/**
 * Codex ↔ Kimi 协议适配层
 *
 * 把 OpenAI Responses API (/v1/responses) 请求翻译为 Kimi Chat Completions API，
 * 再将响应转回 Responses API 格式，供 Codex CLI 使用。
 *
 * 用法:
 *   export KIMI_API_KEY="sk-..."
 *   export KIMI_BASE_URL="https://api.kimi.com/coding/v1"  # 可选，默认 Kimi For Coding
 *   node codex-kimi-adapter.js
 *
 * 然后让 Codex 指向本代理:
 *   export OPENAI_BASE_URL="http://localhost:3456"
 *   codex
 */

const http = require("http");
const https = require("https");
const { URL } = require("url");

const PORT = process.env.PORT || 3456;

// 自动清洗：去掉全角引号、零宽字符、换行符等常见复制污染
function sanitizeKey(raw) {
  return (raw || "")
    .replace(/[\u2018\u2019\u201C\u201D\u201E\u201F\u2032\u2033\u2035\u2036]/g, "") // 各类引号
    .replace(/[\u200B-\u200F\uFEFF]/g, "") // 零宽字符
    .replace(/[\n\r\t]/g, "") // 换行/制表符
    .trim();
}

const KIMI_API_KEY = sanitizeKey(process.env.KIMI_API_KEY);
const KIMI_BASE_URL = process.env.KIMI_BASE_URL || "https://api.kimi.com/coding/v1";
const TARGET_CHAT_URL = `${KIMI_BASE_URL}/chat/completions`;

if (!KIMI_API_KEY) {
  console.error("错误: 请设置环境变量 KIMI_API_KEY");
  process.exit(1);
}

// 校验：只允许 ASCII 可打印字符（0x21-0x7E）
function validateApiKey(key) {
  const illegal = [];
  for (let i = 0; i < key.length; i++) {
    const code = key.charCodeAt(i);
    if (code < 0x21 || code > 0x7E) {
      illegal.push({
        pos: i,
        display: key[i],
        hex: code.toString(16).padStart(4, "0"),
      });
    }
  }
  if (illegal.length > 0) {
    console.error(`[错误] KIMI_API_KEY 清洗后仍包含 ${illegal.length} 个非法字符：`);
    illegal.forEach(({ pos, display, hex }) => {
      console.error(`  位置 ${pos}: '${display}' (U+${hex})`);
    });
    console.error("建议：重新复制 key，不要从富文本编辑器粘贴。");
    process.exit(1);
  }
}
validateApiKey(KIMI_API_KEY);
console.log(`[调试] KIMI_API_KEY 校验通过，长度=${KIMI_API_KEY.length}`);

// ---------- 工具函数 ----------

function generateId(prefix) {
  return `${prefix}_${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`;
}

function nowSeconds() {
  return Math.floor(Date.now() / 1000);
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      try {
        const raw = Buffer.concat(chunks).toString("utf-8");
        resolve(raw ? JSON.parse(raw) : {});
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

function forwardRequest(url, body, apiKey) {
  const parsed = new URL(url);
  const mod = parsed.protocol === "https:" ? https : http;
  const postData = JSON.stringify(body);

  return new Promise((resolve, reject) => {
    const request = mod.request(
      {
        hostname: parsed.hostname,
        port: parsed.port || (parsed.protocol === "https:" ? 443 : 80),
        path: parsed.pathname + parsed.search,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
          "Content-Length": Buffer.byteLength(postData),
          Accept: body.stream ? "text/event-stream" : "application/json",
          "User-Agent": "Kimi-CLI/1.0",
        },
      },
      (response) => {
        resolve(response);
      }
    );
    request.on("error", reject);
    request.write(postData);
    request.end();
  });
}

// ---------- 请求转换 ----------

/**
 * 将 Responses API 请求体转换为 Chat Completions 请求体
 */
function responsesToChat(reqBody) {
  const chatBody = {
    model: reqBody.model,
    messages: [],
    stream: true, // 强制流式：避免非流式等待全量生成，体感延迟大幅降低
  };

  // 透传常见参数
  [
    "temperature",
    "top_p",
    "max_tokens",
    "max_completion_tokens",
    "stop",
    "presence_penalty",
    "frequency_penalty",
    "seed",
  ].forEach((key) => {
    if (reqBody[key] !== undefined) chatBody[key] = reqBody[key];
  });

  // 转换 input → messages
  const input = reqBody.input;
  if (typeof input === "string") {
    chatBody.messages.push({ role: "user", content: input });
  } else if (Array.isArray(input)) {
    chatBody.messages = input.map((item) => {
      if (typeof item === "string") return { role: "user", content: item };
      // Responses API 的 input item 格式与 message 高度相似，直接透传
      return {
        role: item.role || "user",
        content: item.content,
        name: item.name,
        tool_calls: item.tool_calls,
        tool_call_id: item.tool_call_id,
      };
    });
  }

  // 转换 tools / tool_choice
  if (reqBody.tools) {
    chatBody.tools = reqBody.tools;
  }
  if (reqBody.tool_choice) {
    chatBody.tool_choice = reqBody.tool_choice;
  }

  return chatBody;
}

// ---------- 响应转换（非流式） ----------

/**
 * 将 Chat Completions 响应转换为 Responses API 响应
 */
function chatToResponses(chatResp, model) {
  const choice = chatResp.choices?.[0];
  const message = choice?.message;
  const usage = chatResp.usage || {};

  const outputItems = [];

  // assistant message
  if (message) {
    const contentBlocks = [];
    if (message.content) {
      contentBlocks.push({
        type: "output_text",
        text: message.content,
        annotations: [],
      });
    }
    if (message.tool_calls) {
      message.tool_calls.forEach((tc) => {
        contentBlocks.push({
          type: "tool_call",
          id: tc.id,
          call_id: tc.id,
          name: tc.function?.name,
          arguments: tc.function?.arguments,
        });
      });
    }

    outputItems.push({
      type: "message",
      id: generateId("msg"),
      status: "completed",
      role: message.role || "assistant",
      content: contentBlocks,
    });
  }

  return {
    id: generateId("resp"),
    object: "response",
    created_at: nowSeconds(),
    status: "completed",
    error: null,
    incomplete_details: null,
    instructions: null,
    max_output_tokens: null,
    model: model || chatResp.model,
    output: outputItems,
    usage: {
      input_tokens: usage.prompt_tokens || 0,
      output_tokens: usage.completion_tokens || 0,
      total_tokens: usage.total_tokens || 0,
    },
  };
}

// ---------- 流式响应转换 ----------

/**
 * 将 Kimi 的 SSE 行转换为 Responses API 的 SSE 行
 */
function* transformStreamLine(line, ctx) {
  if (!line.startsWith("data:")) return;
  const dataStr = line.slice(5).trim();
  if (dataStr === "[DONE]") {
    // Responses API 没有 [DONE]，用 completed 事件收尾
    yield `event: response.completed`;
    yield `data: ${JSON.stringify({
      type: "response.completed",
      response: {
        id: ctx.responseId,
        object: "response",
        status: "completed",
        output: ctx.outputItems,
      },
    })}`;
    return;
  }

  let data;
  try {
    data = JSON.parse(dataStr);
  } catch {
    return;
  }

  const choice = data.choices?.[0];
  if (!choice) return;

  const delta = choice.delta;
  if (!delta) return;

  // 首次输出事件
  if (!ctx.started) {
    ctx.started = true;
    yield `event: response.created`;
    yield `data: ${JSON.stringify({
      type: "response.created",
      response: {
        id: ctx.responseId,
        object: "response",
        status: "in_progress",
        model: ctx.model,
        output: [],
      },
    })}`;

    yield `event: response.output_item.added`;
    yield `data: ${JSON.stringify({
      type: "response.output_item.added",
      output_index: 0,
      item: {
        type: "message",
        id: ctx.messageId,
        status: "in_progress",
        role: "assistant",
        content: [],
      },
    })}`;
  }

  // content delta
  if (delta.content) {
    yield `event: response.content_part.added`;
    yield `data: ${JSON.stringify({
      type: "response.content_part.added",
      item_id: ctx.messageId,
      output_index: 0,
      content_index: 0,
      part: {
        type: "output_text",
        text: delta.content,
        annotations: [],
      },
    })}`;

    yield `event: response.output_text.delta`;
    yield `data: ${JSON.stringify({
      type: ".response.output_text.delta",
      item_id: ctx.messageId,
      output_index: 0,
      content_index: 0,
      delta: delta.content,
    })}`;
  }

  // tool_calls delta
  if (delta.tool_calls) {
    delta.tool_calls.forEach((tc, idx) => {
      yield `event: response.tool_call.delta`;
      yield `data: ${JSON.stringify({
        type: "response.tool_call.delta",
        item_id: ctx.messageId,
        output_index: 0,
        content_index: idx,
        delta: {
          function: {
            name: tc.function?.name,
            arguments: tc.function?.arguments,
          },
        },
      })}`;
    });
  }
}

// ---------- HTTP 服务器 ----------

const server = http.createServer(async (req, res) => {
  // CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  // 健康检查
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
    return;
  }

  // 处理 /v1/responses（Codex CLI 原生）或 /responses（cc-switch 转发路径）
  if (req.method !== "POST" || (req.url !== "/v1/responses" && req.url !== "/responses")) {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Not Found", message: "仅支持 POST /v1/responses 或 POST /responses" }));
    return;
  }

  let reqBody;
  try {
    reqBody = await parseBody(req);
  } catch (e) {
    res.writeHead(400, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Invalid JSON", message: e.message }));
    return;
  }

  const chatBody = responsesToChat(reqBody);
  console.log(`[→ Kimi] model=${chatBody.model} stream=${chatBody.stream}`);

  let targetResp;
  try {
    targetResp = await forwardRequest(TARGET_CHAT_URL, chatBody, KIMI_API_KEY);
  } catch (err) {
    console.error("[转发错误]", err.message);
    res.writeHead(502, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Bad Gateway", message: err.message }));
    return;
  }

  // 流式响应
  if (chatBody.stream) {
    res.writeHead(200, {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    });

    const ctx = {
      responseId: generateId("resp"),
      messageId: generateId("msg"),
      model: reqBody.model,
      started: false,
      outputItems: [],
    };

    let buffer = "";
    targetResp.on("data", (chunk) => {
      buffer += chunk.toString("utf-8");
      const lines = buffer.split("\n");
      buffer = lines.pop(); // 保留不完整的最后一行

      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line) continue;
        for (const outLine of transformStreamLine(line, ctx)) {
          res.write(outLine + "\n\n");
        }
      }
    });

    targetResp.on("end", () => {
      if (buffer.trim()) {
        for (const outLine of transformStreamLine(buffer.trim(), ctx)) {
          res.write(outLine + "\n\n");
        }
      }
      res.end();
    });

    targetResp.on("error", (err) => {
      console.error("[流式错误]", err.message);
      res.end();
    });
    return;
  }

  // 非流式响应
  let targetBody = "";
  targetResp.on("data", (c) => (targetBody += c));
  targetResp.on("end", () => {
    try {
      const chatResp = JSON.parse(targetBody);
      const respBody = chatToResponses(chatResp, reqBody.model);
      res.writeHead(targetResp.statusCode || 200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(respBody));
    } catch (e) {
      console.error("[解析错误]", e.message);
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Parse Error", message: e.message, raw: targetBody.slice(0, 500) }));
    }
  });
});

server.listen(PORT, () => {
  console.log(`Codex ↔ Kimi 适配层已启动: http://localhost:${PORT}`);
  console.log(`目标上游: ${TARGET_CHAT_URL}`);
  console.log("设置环境变量后运行: OPENAI_BASE_URL=http://localhost:${PORT} codex");
});
