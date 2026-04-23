#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-
#
# 脑卒中康复纵向数据 LMM + 非参数分析 与目标达成检查 (R 版本)
# 用法: Rscript analyze_lmm.R <数据文件.xlsx|.csv> [--no-excel]
#
# 输出: Markdown 表格到 stdout

suppressPackageStartupMessages({
  library(readxl)
  library(dplyr)
  library(tidyr)
  library(lme4)
  library(lmerTest)
  library(emmeans)
  library(ordinal)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  stop("用法: Rscript analyze_lmm.R <数据文件> [--no-excel]")
}

input_file <- args[1]

# ============================================================================
# 配置
# ============================================================================
GROUP_COL <- "分组"
ID_COL    <- "患者ID"
TIME_COL  <- "时间点"
TIME_ORDER  <- c("T0", "T1", "T2", "T3")
GROUP_ORDER <- c(1, 2, 3, 4)

OUTCOMES <- list(
  FMA_LE = "continuous",
  ADL    = "continuous",
  BBS    = "continuous",
  TUGT   = "continuous",
  CSS    = "continuous",
  MAS    = "ordinal"
)

POSTHOC_TIMES <- c("T2", "T3")
REF_GROUP <- 1
REF_TIME  <- "T0"
BASELINE_P_THRESHOLD <- 0.05

# 目标对比定义
target_contrasts <- list(
  FMA_LE = list(
    T2 = list(list(name="G1>G2", g_a=1, g_b=2, type="sig_moderate"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose")),
    T3 = list(list(name="G1>G2", g_a=1, g_b=2, type="sig_moderate"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose"))
  ),
  ADL = list(
    T2 = list(list(name="G1>G2", g_a=1, g_b=2, type="sig_moderate"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose")),
    T3 = list(list(name="G1>G2", g_a=1, g_b=2, type="nonsig_loose"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose"))
  ),
  BBS = list(
    T2 = list(list(name="G1>G2", g_a=1, g_b=2, type="sig_moderate"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose")),
    T3 = list(list(name="G1>G2", g_a=1, g_b=2, type="nonsig_loose"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose"))
  ),
  MAS = list(
    T2 = list(list(name="G1>G2", g_a=1, g_b=2, type="sig_moderate"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose")),
    T3 = list(list(name="G1>G2", g_a=1, g_b=2, type="nonsig_loose"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose"))
  ),
  CSS = list(
    T2 = list(list(name="G1>G2", g_a=1, g_b=2, type="sig_moderate"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose")),
    T3 = list(list(name="G1>G2", g_a=1, g_b=2, type="nonsig_loose"),
              list(name="G2>G3", g_a=2, g_b=3, type="sig_any"),
              list(name="G2>G4", g_a=2, g_b=4, type="sig_any"),
              list(name="G3=G4", g_a=3, g_b=4, type="nonsig_loose"))
  )
)

# ============================================================================
# 工具函数
# ============================================================================

load_data <- function(path) {
  if (grepl("\\.csv$", path, ignore.case = TRUE)) {
    df <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  } else {
    df <- read_excel(path)
    df <- as.data.frame(df)
  }
  names(df) <- trimws(names(df))
  df[[ID_COL]] <- trimws(as.character(df[[ID_COL]]))
  df[[TIME_COL]] <- toupper(trimws(as.character(df[[TIME_COL]])))
  df[[GROUP_COL]] <- as.integer(df[[GROUP_COL]])
  df <- df[df[[GROUP_COL]] %in% GROUP_ORDER, ]
  df[[GROUP_COL]] <- factor(df[[GROUP_COL]], levels = GROUP_ORDER)
  df[[TIME_COL]] <- factor(df[[TIME_COL]], levels = TIME_ORDER)
  return(df)
}

safe_desc <- function(x) {
  x <- as.numeric(x)
  x <- x[!is.na(x)]
  n <- length(x)
  if (n == 0) return(list(mean = NA, sd = NA, n = 0, median = NA, q25 = NA, q75 = NA))
  if (n == 1) return(list(mean = x[1], sd = NA, n = 1, median = x[1], q25 = NA, q75 = NA))
  list(mean = mean(x), sd = sd(x), n = n, median = median(x), q25 = quantile(x, 0.25), q75 = quantile(x, 0.75))
}

baseline_test <- function(df, metric, type = "continuous") {
  d <- df[df[[TIME_COL]] == REF_TIME, c(GROUP_COL, metric)]
  d <- d[!is.na(d[[metric]]), ]
  groups <- lapply(GROUP_ORDER, function(g) {
    as.numeric(d[[metric]][d[[GROUP_COL]] == g])
  })

  if (type == "ordinal") {
    kw <- kruskal.test(as.numeric(d[[metric]]) ~ d[[GROUP_COL]])
    p_anova <- kw$p.value

    g12 <- c(groups[[1]], groups[[2]])
    g34 <- c(groups[[3]], groups[[4]])
    if (length(g12) > 0 && length(g34) > 0) {
      mw <- wilcox.test(g12, g34, exact = FALSE)
      p_merge <- mw$p.value
    } else {
      p_merge <- 0
    }
  } else {
    aov_res <- tryCatch(aov(as.numeric(d[[metric]]) ~ d[[GROUP_COL]]), error = function(e) NULL)
    if (!is.null(aov_res)) {
      p_anova <- summary(aov_res)[[1]][[1, "Pr(>F)"]]
    } else {
      p_anova <- 0
    }

    g12 <- c(groups[[1]], groups[[2]])
    g34 <- c(groups[[3]], groups[[4]])
    if (length(g12) > 1 && length(g34) > 1) {
      tt <- t.test(g12, g34)
      p_merge <- tt$p.value
    } else {
      p_merge <- 0
    }
  }

  aligned <- p_anova >= BASELINE_P_THRESHOLD && p_merge >= BASELINE_P_THRESHOLD
  list(metric = metric, anova_p = p_anova, merge_p = p_merge, aligned = aligned)
}

sig_symbol <- function(p) {
  if (is.na(p)) return("na")
  if (p < 0.001) return("***")
  if (p < 0.01) return("**")
  if (p < 0.05) return("*")
  return("ns")
}

evaluate_cell <- function(p, est, target_type, higher_better = TRUE) {
  if (is.na(p)) return(list(icon = "✗", label = "FAIL", detail = "无数据"))

  dir_ok <- if (higher_better) est > 0 else est < 0

  if (target_type == "sig_moderate") {
    if (!dir_ok) return(list(icon = "✗", label = "FAIL", detail = "方向错误"))
    if (p >= 0.01 && p < 0.05) return(list(icon = "✓", label = "ideal", detail = ""))
    if (p < 0.01) return(list(icon = "✓", label = "OK", detail = "偏强"))
    return(list(icon = "✗", label = "FAIL", detail = "不显著"))
  } else if (target_type == "sig_any") {
    if (!dir_ok) return(list(icon = "✗", label = "FAIL", detail = "方向错误"))
    if (p >= 0.01 && p < 0.05) return(list(icon = "✓", label = "ideal", detail = ""))
    if (p < 0.01) return(list(icon = "✓", label = "OK", detail = "偏强"))
    return(list(icon = "✗", label = "FAIL", detail = "不显著"))
  } else { # nonsig_loose
    if (p >= 0.05) return(list(icon = "✓", label = "ideal", detail = ""))
    if (p >= 0.03) return(list(icon = "✓", label = "OK", detail = "边缘"))
    return(list(icon = "✗", label = "FAIL", detail = "过显著"))
  }
}

# ============================================================================
# LMM / 非参数分析
# ============================================================================

run_continuous_lmm <- function(df, metric) {
  cols <- c(ID_COL, GROUP_COL, TIME_COL, metric)
  d <- df[, cols]
  d <- d[!is.na(d[[metric]]), ]
  if (nrow(d) == 0) return(NULL)

  d[[GROUP_COL]] <- factor(d[[GROUP_COL]], levels = GROUP_ORDER)
  d[[TIME_COL]] <- factor(d[[TIME_COL]], levels = TIME_ORDER)

  formula_str <- paste0(metric, " ~ ", GROUP_COL, " * ", TIME_COL, " + (1 | ", ID_COL, ")")

  fit <- tryCatch(
    lmer(as.formula(formula_str), data = d, REML = TRUE),
    error = function(e) NULL
  )

  if (is.null(fit)) return(NULL)

  pair_rows <- list()
  pairs <- list(c(1,2), c(1,3), c(1,4), c(2,3), c(2,4), c(3,4))

  higher_better <- !(metric %in% c("CSS", "MAS", "TUGT"))

  for (t in POSTHOC_TIMES) {
    sub_emm <- emmeans(fit, as.formula(paste("~", GROUP_COL, "|", TIME_COL)), at = setNames(list(t), TIME_COL))
    pw <- pairs(sub_emm, adjust = "none")
    pw <- as.data.frame(pw)

    for (pr in pairs) {
      g_a <- pr[1]
      g_b <- pr[2]

      fwd_name <- paste0(GROUP_COL, g_a, " - ", GROUP_COL, g_b)
      rev_name <- paste0(GROUP_COL, g_b, " - ", GROUP_COL, g_a)

      row_idx <- which(pw$contrast == fwd_name)
      if (length(row_idx) > 0) {
        est <- pw$estimate[row_idx[1]]
        p <- pw$p.value[row_idx[1]]
        se <- pw$SE[row_idx[1]]
      } else {
        row_idx <- which(pw$contrast == rev_name)
        if (length(row_idx) == 0) next
        est <- -pw$estimate[row_idx[1]]
        p <- pw$p.value[row_idx[1]]
        se <- pw$SE[row_idx[1]]
      }

      if (est > 0) {
        raw_dir <- paste0("G", g_a, " > G", g_b)
        clin_dir <- paste0("G", if (higher_better) g_a else g_b, "更优")
      } else if (est < 0) {
        raw_dir <- paste0("G", g_a, " < G", g_b)
        clin_dir <- paste0("G", if (higher_better) g_b else g_a, "更优")
      } else {
        raw_dir <- paste0("G", g_a, " = G", g_b)
        clin_dir <- "无差异"
      }

      pair_rows[[length(pair_rows) + 1]] <- data.frame(
        metric = metric, time = t, contrast = paste0("G", g_a, "_vs_G", g_b),
        estimate = est, se = se, p = p,
        raw_direction = raw_dir, clinical_direction = clin_dir,
        stringsAsFactors = FALSE
      )
    }
  }

  if (length(pair_rows) == 0) return(NULL)
  do.call(rbind, pair_rows)
}

run_ordinal_clmm <- function(df, metric) {
  cols <- c(ID_COL, GROUP_COL, TIME_COL, metric)
  d <- df[, cols]
  d <- d[!is.na(d[[metric]]), ]
  if (nrow(d) == 0) return(NULL)

  d[[GROUP_COL]] <- factor(d[[GROUP_COL]], levels = GROUP_ORDER)
  d[[TIME_COL]] <- factor(d[[TIME_COL]], levels = TIME_ORDER)
  d[[metric]] <- factor(d[[metric]], ordered = TRUE)

  formula_str <- paste0(metric, " ~ ", GROUP_COL, " * ", TIME_COL, " + (1 | ", ID_COL, ")")

  fit <- tryCatch(
    clmm(as.formula(formula_str), data = d, link = "logit"),
    error = function(e) NULL
  )

  if (is.null(fit)) return(NULL)

  pair_rows <- list()
  pairs <- list(c(1,2), c(1,3), c(1,4), c(2,3), c(2,4), c(3,4))
  higher_better <- !(metric %in% c("CSS", "MAS", "TUGT"))

  for (t in POSTHOC_TIMES) {
    sub_emm <- emmeans(fit, as.formula(paste("~", GROUP_COL, "|", TIME_COL)),
                       at = setNames(list(t), TIME_COL),
                       mode = "latent")
    pw <- pairs(sub_emm, adjust = "none")
    pw <- as.data.frame(pw)

    for (pr in pairs) {
      g_a <- pr[1]
      g_b <- pr[2]

      fwd_name <- paste0(GROUP_COL, g_a, " - ", GROUP_COL, g_b)
      rev_name <- paste0(GROUP_COL, g_b, " - ", GROUP_COL, g_a)

      row_idx <- which(pw$contrast == fwd_name)
      if (length(row_idx) > 0) {
        est <- pw$estimate[row_idx[1]]
        p <- pw$p.value[row_idx[1]]
        se <- pw$SE[row_idx[1]]
      } else {
        row_idx <- which(pw$contrast == rev_name)
        if (length(row_idx) == 0) next
        est <- -pw$estimate[row_idx[1]]
        p <- pw$p.value[row_idx[1]]
        se <- pw$SE[row_idx[1]]
      }

      if (est > 0) {
        raw_dir <- paste0("G", g_a, " > G", g_b)
        clin_dir <- paste0("G", if (higher_better) g_a else g_b, "更优")
      } else if (est < 0) {
        raw_dir <- paste0("G", g_a, " < G", g_b)
        clin_dir <- paste0("G", if (higher_better) g_b else g_a, "更优")
      } else {
        raw_dir <- paste0("G", g_a, " = G", g_b)
        clin_dir <- "无差异"
      }

      pair_rows[[length(pair_rows) + 1]] <- data.frame(
        metric = metric, time = t, contrast = paste0("G", g_a, "_vs_G", g_b),
        estimate = est, se = se, p = p,
        raw_direction = raw_dir, clinical_direction = clin_dir,
        stringsAsFactors = FALSE
      )
    }
  }

  if (length(pair_rows) == 0) return(NULL)
  do.call(rbind, pair_rows)
}

# ============================================================================
# 主流程
# ============================================================================

df <- load_data(input_file)
cat("数据加载完成:", nrow(df), "条记录,", length(unique(df[[ID_COL]])), "名患者\n")

# 1. T0 基线
baseline_rows <- lapply(names(OUTCOMES), function(m) {
  baseline_test(df, m, type = OUTCOMES[[m]])
})

# 2. 描述统计
desc_data <- list()
for (metric in names(OUTCOMES)) {
  desc_data[[metric]] <- list()
  for (time in TIME_ORDER) {
    desc_data[[metric]][[time]] <- list()
    for (g in GROUP_ORDER) {
      dsub <- df[[metric]][df[[GROUP_COL]] == g & df[[TIME_COL]] == time]
      desc_data[[metric]][[time]][[as.character(g)]] <- safe_desc(dsub)
    }
  }
}

# 3. LMM (连续变量) + CLMM (MAS)
lmm_results <- list()
for (metric in c("FMA_LE", "ADL", "BBS", "CSS", "TUGT")) {
  lmm_results[[metric]] <- run_continuous_lmm(df, metric)
}
lmm_results[["MAS"]] <- run_ordinal_clmm(df, "MAS")

# 4. 目标达成总表
summary_rows <- list()
for (metric in c("FMA_LE", "ADL", "BBS", "MAS", "CSS")) {
  for (t in c("T2", "T3")) {
    pair_df <- lmm_results[[metric]]
    if (is.null(pair_df)) next

    higher_better <- !(metric %in% c("CSS", "MAS", "TUGT"))
    row <- list(参数 = metric, 时点 = t)
    statuses <- c()
    concerns <- c()

    contrasts <- target_contrasts[[metric]][[t]]
    for (cinfo in contrasts) {
      sub <- pair_df[pair_df$time == t & pair_df$contrast == paste0("G", cinfo$g_a, "_vs_G", cinfo$g_b), ]
      if (nrow(sub) == 0) {
        row[[cinfo$name]] <- "无数据"
        statuses <- c(statuses, "fail")
        concerns <- c(concerns, paste0(cinfo$name, ": 无数据"))
        next
      }
      p <- sub$p[1]
      est <- sub$estimate[1]
      ev <- evaluate_cell(p, est, cinfo$type, higher_better)
      sig <- sig_symbol(p)
      cell_text <- sprintf("P=%.4f %s %s\n%s", p, sig, ev$icon, ev$label)
      row[[cinfo$name]] <- cell_text

      if (ev$icon == "✗") {
        statuses <- c(statuses, "fail")
        concerns <- c(concerns, paste0(cinfo$name, ": ", ev$detail))
      } else if (ev$label == "OK" && ev$detail != "") {
        statuses <- c(statuses, "ok")
        concerns <- c(concerns, paste0(cinfo$name, ": ", ev$detail))
      } else {
        statuses <- c(statuses, "ideal")
      }
    }

    if ("fail" %in% statuses || "ok" %in% statuses) {
      detail_groups <- list()
      for (c in concerns) {
        parts <- strsplit(c, ": ", fixed = TRUE)[[1]]
        name <- parts[1]
        detail <- gsub("不显著", "未显著", parts[2])
        if (is.null(detail_groups[[detail]])) detail_groups[[detail]] <- c()
        detail_groups[[detail]] <- c(detail_groups[[detail]], name)
      }
      status_parts <- sapply(names(detail_groups), function(d) {
        paste0(paste(detail_groups[[d]], collapse = "、"), " ", d)
      })
      row[["状态"]] <- paste0("⚠️ ", paste(status_parts, collapse = "、"))
    } else {
      row[["状态"]] <- "✅ 全部达标"
    }

    summary_rows[[length(summary_rows) + 1]] <- as.data.frame(row, stringsAsFactors = FALSE, check.names = FALSE)
  }
}

summary_df <- do.call(rbind, summary_rows)

# ========================================================================
# 输出 Markdown
# ========================================================================
cat("\n================================================================================\n")
cat("LMM / CLMM 目标达成总表\n")
cat("================================================================================\n\n")
cat("| 参数 | 时点 | G1>G2 | G2>G3 | G2>G4 | G3=G4 | 状态 |\n")
cat("|------|------|-------|-------|-------|-------|------|\n")

for (i in seq_len(nrow(summary_df))) {
  cells <- c(summary_df$参数[i], summary_df$时点[i])
  for (col in c("G1>G2", "G2>G3", "G2>G4", "G3=G4")) {
    val <- gsub("\n", "<br>", summary_df[[col]][i], fixed = TRUE)
    cells <- c(cells, val)
  }
  status <- gsub("\n", "<br>", summary_df$状态[i], fixed = TRUE)
  cells <- c(cells, status)
  cat("| ", paste(cells, collapse = " | "), " |\n", sep = "")
}

cat("\n================================================================================\n")
cat("二、所有参数 × 所有时间点 × 各组 均值 ± 标准差\n")
cat("================================================================================\n")

for (metric in names(OUTCOMES)) {
  cat("\n**", metric, "**\n\n", sep = "")
  cat("| 时点 | G1 | G2 | G3 | G4 |\n")
  cat("|------|-----|-----|-----|-----|\n")
  for (time in TIME_ORDER) {
    cells <- time
    for (g in GROUP_ORDER) {
      d <- desc_data[[metric]][[time]][[as.character(g)]]
      if (is.na(d$mean)) {
        cells <- c(cells, "-")
      } else if (is.na(d$sd) || d$n <= 1) {
        cells <- c(cells, sprintf("%.2f±NA(n=%d)", d$mean, d$n))
      } else {
        cells <- c(cells, sprintf("%.2f±%.2f", d$mean, d$sd))
      }
    }
    cat("| ", paste(cells, collapse = " | "), " |\n", sep = "")
  }
}

cat("\n================================================================================\n")
cat("三、T0 基线 P值汇总\n")
cat("================================================================================\n\n")
cat("| 参数 | ANOVA P | Merge(G1+2 vs G3+4) P | 状态 |\n")
cat("|------|---------|----------------------|------|\n")
for (r in baseline_rows) {
  status <- if (r$aligned) "✅ 对齐" else "❌ 未对齐"
  cat(sprintf("| %s | %.4f | %.4f | %s |\n", r$metric, r$anova_p, r$merge_p, status))
}
