#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-
#
# 脑卒中康复纵向数据 LMM + 非参数分析 与目标达成检查 (R 版本)
# 集成 RCT 论文分析工作流
# 用法: Rscript analyze_lmm.R <数据文件.xlsx|.csv> [输出目录] [--holm|--bonferroni] [--no-excel]
#
# stdout: Markdown 表格（5节）
# 文件: 13个 CSV/文本文件到输出目录（若提供）

suppressPackageStartupMessages({
  library(readxl)
  library(dplyr)
  library(tidyr)
  library(nlme)
  library(emmeans)
  library(ordinal)
})

options(contrasts = c("contr.sum", "contr.poly"))

# ============================================================================
# 配置
# ============================================================================
GROUP_COL <- "分组"
ID_COL    <- "患者ID"
TIME_COL  <- "时间点"
TIME_ORDER  <- c("T0", "T1", "T2", "T3")
GROUP_ORDER <- c(1, 2, 3, 4)
REF_TIME  <- "T0"
PRIMARY_OUTCOME <- "FMA_LE"
PRIMARY_TIME <- "T2"
PRIMARY_GA <- 1
PRIMARY_GB <- 2
PRIMARY_LABEL <- "G1 vs G2 at T2"
POSTBASELINE_TIMES <- c("T1", "T2", "T3")
ALPHA <- 0.05

OUTCOMES <- list(
  FMA_LE = "continuous",
  ADL    = "continuous",
  BBS    = "continuous",
  TUGT   = "continuous",
  CSS    = "continuous",
  MAS    = "ordinal"
)

# 目标对比定义（用于目标达成检查）
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
# 命令行参数
# ============================================================================
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  stop("用法: Rscript analyze_lmm.R <数据文件> [输出目录] [--holm|--bonferroni] [--no-excel]")
}
input_file <- args[1]
outdir <- NULL
ADJUST_METHOD <- "bonferroni"
use_excel <- TRUE

for (a in args[-1]) {
  if (a == "--holm") ADJUST_METHOD <- "holm"
  else if (a == "--bonferroni") ADJUST_METHOD <- "bonferroni"
  else if (a == "--no-excel") use_excel <- FALSE
  else if (is.null(outdir) && !grepl("^--", a)) outdir <- a
}

if (!is.null(outdir)) {
  dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
}

# ============================================================================
# 工具函数
# ============================================================================

read_input <- function(path) {
  if (!file.exists(path)) stop("找不到数据文件: ", path)
  if (grepl("\\.csv$", path, ignore.case = TRUE)) {
    df <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  } else if (grepl("\\.xlsx?$", path, ignore.case = TRUE)) {
    df <- as.data.frame(readxl::read_excel(path))
  } else {
    stop("仅支持 .csv / .xlsx / .xls 文件")
  }
  df
}

clean_data <- function(df) {
  names(df) <- trimws(names(df))
  required <- c(GROUP_COL, ID_COL, TIME_COL, names(OUTCOMES))
  miss <- setdiff(required, names(df))
  if (length(miss) > 0) stop("缺少必要列: ", paste(miss, collapse = ", "))

  df[[ID_COL]] <- trimws(as.character(df[[ID_COL]]))
  df[[TIME_COL]] <- toupper(trimws(as.character(df[[TIME_COL]])))
  df[[GROUP_COL]] <- suppressWarnings(as.integer(df[[GROUP_COL]]))

  bad_group <- unique(df[[GROUP_COL]][!is.na(df[[GROUP_COL]]) & !df[[GROUP_COL]] %in% GROUP_ORDER])
  bad_time  <- unique(df[[TIME_COL]][!is.na(df[[TIME_COL]]) & !df[[TIME_COL]] %in% TIME_ORDER])
  if (length(bad_group) > 0) stop("存在未定义分组: ", paste(bad_group, collapse = ", "))
  if (length(bad_time) > 0) stop("存在未定义时间点: ", paste(bad_time, collapse = ", "))

  df[[GROUP_COL]] <- factor(df[[GROUP_COL]], levels = GROUP_ORDER)
  df[[TIME_COL]]  <- factor(df[[TIME_COL]], levels = TIME_ORDER, ordered = TRUE)

  dup <- df %>% count(.data[[ID_COL]], .data[[TIME_COL]], name = "n") %>% filter(n > 1)
  if (nrow(dup) > 0) stop("同一患者在同一时间点存在重复记录，请先清洗数据。")

  for (nm in names(OUTCOMES)) {
    if (OUTCOMES[[nm]] == "continuous") {
      df[[nm]] <- suppressWarnings(as.numeric(df[[nm]]))
    } else {
      raw_x <- trimws(as.character(df[[nm]]))
      raw_x[raw_x %in% c("", "NA", "NaN", "NULL")] <- NA
      x_num <- suppressWarnings(as.numeric(raw_x))
      if (all(is.na(x_num[!is.na(raw_x)]))) {
        lev <- sort(unique(raw_x[!is.na(raw_x)]))
        df[[nm]] <- ordered(raw_x, levels = lev)
      } else {
        lev <- sort(unique(x_num[!is.na(x_num)]))
        df[[nm]] <- ordered(x_num, levels = lev)
      }
    }
  }

  df %>% arrange(.data[[ID_COL]], .data[[TIME_COL]])
}

fmt_num <- function(x, digits = 3) {
  ifelse(is.na(x), "NA", formatC(x, format = "f", digits = digits))
}

collapse_messages <- function(x) {
  x <- unique(x[!is.na(x) & nzchar(x)])
  if (length(x) == 0) "" else paste(x, collapse = " | ")
}

get_baseline_map <- function(df, outcome) {
  base <- df %>%
    filter(.data[[TIME_COL]] == REF_TIME) %>%
    select(all_of(c(ID_COL, outcome)))
  colnames(base)[2] <- paste0(outcome, "_BASE")
  base
}

safe_desc_cont <- function(x) {
  x <- suppressWarnings(as.numeric(x))
  x <- x[!is.na(x)]
  n <- length(x)
  if (n == 0) {
    return(data.frame(n = 0, mean = NA_real_, sd = NA_real_, median = NA_real_, q1 = NA_real_, q3 = NA_real_))
  }
  data.frame(
    n = n,
    mean = mean(x),
    sd = if (n > 1) sd(x) else NA_real_,
    median = as.character(median(x)),
    q1 = as.character(unname(quantile(x, 0.25, names = FALSE, type = 2))),
    q3 = as.character(unname(quantile(x, 0.75, names = FALSE, type = 2)))
  )
}

safe_desc_ord <- function(x) {
  x <- x[!is.na(x)]
  n <- length(x)
  if (n == 0) return(data.frame(n = 0, median = NA_character_, q1 = NA_character_, q3 = NA_character_))
  xx <- suppressWarnings(as.numeric(as.character(x)))
  if (all(!is.na(xx))) {
    data.frame(
      n = n,
      median = as.character(median(xx)),
      q1 = as.character(unname(quantile(xx, 0.25, names = FALSE, type = 2))),
      q3 = as.character(unname(quantile(xx, 0.75, names = FALSE, type = 2)))
    )
  } else {
    tab <- sort(table(as.character(x)), decreasing = TRUE)
    data.frame(n = n, median = names(tab)[1], q1 = NA_character_, q3 = NA_character_)
  }
}

make_descriptive_table <- function(df) {
  out <- list()
  for (metric in names(OUTCOMES)) {
    for (tm in TIME_ORDER) {
      for (gp in GROUP_ORDER) {
        x <- df[df[[TIME_COL]] == tm & df[[GROUP_COL]] == gp, metric, drop = TRUE]
        stat <- if (OUTCOMES[[metric]] == "continuous") safe_desc_cont(x) else safe_desc_ord(x)
        out[[length(out) + 1]] <- cbind(outcome = metric, time = tm, group = gp, stat, stringsAsFactors = FALSE)
      }
    }
  }
  bind_rows(out)
}

make_baseline_table <- function(df) {
  out <- list()
  base_df <- df %>% filter(.data[[TIME_COL]] == REF_TIME)
  for (metric in names(OUTCOMES)) {
    for (gp in GROUP_ORDER) {
      x <- base_df[base_df[[GROUP_COL]] == gp, metric, drop = TRUE]
      stat <- if (OUTCOMES[[metric]] == "continuous") safe_desc_cont(x) else safe_desc_ord(x)
      out[[length(out) + 1]] <- cbind(outcome = metric, group = gp, stat, stringsAsFactors = FALSE)
    }
  }
  bind_rows(out)
}

make_missingness_table <- function(df) {
  out <- list()
  for (metric in names(OUTCOMES)) {
    tmp <- df %>%
      group_by(.data[[GROUP_COL]], .data[[TIME_COL]]) %>%
      summarise(total_n = n(), missing_n = sum(is.na(.data[[metric]])), .groups = "drop") %>%
      mutate(missing_pct = 100 * missing_n / total_n, outcome = metric) %>%
      rename(group = .data[[GROUP_COL]], time = .data[[TIME_COL]]) %>%
      select(outcome, time, group, total_n, missing_n, missing_pct)
    out[[length(out) + 1]] <- tmp
  }
  bind_rows(out)
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

  aligned <- p_anova >= 0.05 && p_merge >= 0.05
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
  } else {
    if (p >= 0.05) return(list(icon = "✓", label = "ideal", detail = ""))
    if (p >= 0.03) return(list(icon = "✓", label = "OK", detail = "边缘"))
    return(list(icon = "✗", label = "FAIL", detail = "过显著"))
  }
}

nlme_anova_to_df <- function(anova_res, outcome) {
  if (is.null(anova_res)) return(NULL)
  effects <- rownames(anova_res)
  data.frame(
    outcome = outcome,
    effect = effects,
    NumDF = as.numeric(anova_res[, "numDF"]),
    DenDF = as.numeric(anova_res[, "denDF"]),
    F.value = as.numeric(anova_res[, "F-value"]),
    Pr..F. = as.numeric(anova_res[, "p-value"]),
    stringsAsFactors = FALSE
  )
}

# ============================================================================
# LMM / CLMM 分析
# ============================================================================

fit_continuous_lmm_nlme <- function(df, outcome, adjust = "bonferroni") {
  d <- df %>% left_join(get_baseline_map(df, outcome), by = ID_COL)
  base_col <- paste0(outcome, "_BASE")
  d <- d %>% filter(!is.na(.data[[outcome]]), !is.na(.data[[base_col]]))
  if (nrow(d) == 0) return(NULL)

  d$time_num <- as.numeric(d[[TIME_COL]]) - 1
  d[[TIME_COL]] <- factor(d[[TIME_COL]], levels = TIME_ORDER)
  d[[GROUP_COL]] <- factor(d[[GROUP_COL]], levels = GROUP_ORDER)
  d <- d[order(d[[ID_COL]], d[[TIME_COL]]), ]

  f_fixed <- as.formula(sprintf("%s ~ %s * %s + %s", outcome, GROUP_COL, TIME_COL, base_col))
  f_slope <- as.formula(paste0("~ time_num | ", ID_COL))
  f_int   <- as.formula(paste0("~ 1 | ", ID_COL))

  warn <- character(0)
  fit <- NULL
  random_used <- NA_character_

  fit <- withCallingHandlers(
    tryCatch(
      nlme::lme(
        fixed = f_fixed,
        random = f_slope,
        correlation = corSymm(form = as.formula(paste0("~ 1 | ", ID_COL))),
        weights = varIdent(form = as.formula(paste0("~ 1 | ", TIME_COL))),
        data = d,
        method = "REML",
        na.action = na.omit,
        control = lmeControl(opt = "optim")
      ),
      error = function(e) { warn <<- c(warn, paste("随机斜率模型失败:", e$message)); NULL }
    ),
    warning = function(w) { warn <<- c(warn, conditionMessage(w)); invokeRestart("muffleWarning") }
  )

  if (is.null(fit)) {
    fit <- withCallingHandlers(
      tryCatch(
        nlme::lme(
          fixed = f_fixed,
          random = f_int,
          correlation = corSymm(form = as.formula(paste0("~ 1 | ", ID_COL))),
          weights = varIdent(form = as.formula(paste0("~ 1 | ", TIME_COL))),
          data = d,
          method = "REML",
          na.action = na.omit,
          control = lmeControl(opt = "optim")
        ),
        error = function(e) { warn <<- c(warn, paste("随机截距模型失败:", e$message)); NULL }
      ),
      warning = function(w) { warn <<- c(warn, conditionMessage(w)); invokeRestart("muffleWarning") }
    )
    random_used <- "(1 | 患者ID)"
  } else {
    random_used <- "(1 + time_num | 患者ID)"
  }

  if (is.null(fit)) return(NULL)

  anova_res <- tryCatch(anova(fit), error = function(e) NULL)

  emm <- emmeans::emmeans(fit, as.formula(paste("~", GROUP_COL, "|", TIME_COL)))
  emm_df <- as.data.frame(summary(emm, infer = c(TRUE, TRUE)))
  emm_df$outcome <- outcome
  names(emm_df)[names(emm_df) == GROUP_COL] <- "group"
  names(emm_df)[names(emm_df) == TIME_COL] <- "time"

  pair_df <- as.data.frame(summary(pairs(emm, adjust = adjust), infer = c(TRUE, TRUE)))
  pair_df$outcome <- outcome
  if (TIME_COL %in% names(pair_df)) names(pair_df)[names(pair_df) == TIME_COL] <- "time"
  pair_df <- pair_df %>% filter(time %in% POSTBASELINE_TIMES)

  resid_p <- tryCatch(residuals(fit, type = "pearson"), error = function(e) residuals(fit, type = "response"))

  diag_tbl <- data.frame(
    outcome = outcome,
    model_class = class(fit)[1],
    n_obs = nrow(d),
    n_id = dplyr::n_distinct(d[[ID_COL]]),
    random_structure = random_used,
    singular_fit = FALSE,
    AIC = AIC(fit),
    BIC = BIC(fit),
    sigma = sigma(fit),
    max_abs_pearson = suppressWarnings(max(abs(resid_p), na.rm = TRUE)),
    n_abs_pearson_gt_3 = suppressWarnings(sum(abs(resid_p) > 3, na.rm = TRUE)),
    messages = collapse_messages(warn),
    stringsAsFactors = FALSE
  )

  pair_rows <- list()
  pairs_list <- list(c(1,2), c(1,3), c(1,4), c(2,3), c(2,4), c(3,4))
  higher_better <- !(outcome %in% c("CSS", "MAS", "TUGT"))

  for (t in POSTBASELINE_TIMES) {
    pw_t <- pair_df[pair_df$time == t, ]
    for (pr in pairs_list) {
      g_a <- pr[1]; g_b <- pr[2]
      fwd_name <- paste0(GROUP_COL, g_a, " - ", GROUP_COL, g_b)
      rev_name <- paste0(GROUP_COL, g_b, " - ", GROUP_COL, g_a)

      row_idx <- which(pw_t$contrast == fwd_name)
      if (length(row_idx) > 0) {
        est <- pw_t$estimate[row_idx[1]]
        p <- pw_t$p.value[row_idx[1]]
        se <- if ("SE" %in% names(pw_t)) pw_t$SE[row_idx[1]] else NA
        ci_l <- if ("lower.CL" %in% names(pw_t)) pw_t$lower.CL[row_idx[1]] else if ("asymp.LCL" %in% names(pw_t)) pw_t$asymp.LCL[row_idx[1]] else NA
        ci_u <- if ("upper.CL" %in% names(pw_t)) pw_t$upper.CL[row_idx[1]] else if ("asymp.UCL" %in% names(pw_t)) pw_t$asymp.UCL[row_idx[1]] else NA
      } else {
        row_idx <- which(pw_t$contrast == rev_name)
        if (length(row_idx) == 0) next
        est <- -pw_t$estimate[row_idx[1]]
        p <- pw_t$p.value[row_idx[1]]
        se <- if ("SE" %in% names(pw_t)) pw_t$SE[row_idx[1]] else NA
        ci_l <- if ("upper.CL" %in% names(pw_t)) -pw_t$upper.CL[row_idx[1]] else if ("asymp.UCL" %in% names(pw_t)) -pw_t$asymp.UCL[row_idx[1]] else NA
        ci_u <- if ("lower.CL" %in% names(pw_t)) -pw_t$lower.CL[row_idx[1]] else if ("asymp.LCL" %in% names(pw_t)) -pw_t$asymp.LCL[row_idx[1]] else NA
      }

      if (length(est) == 0 || length(p) == 0) next

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
        metric = outcome, time = t, contrast = paste0("G", g_a, "_vs_G", g_b),
        estimate = est, se = se, p = p,
        ci_lower = ci_l, ci_upper = ci_u,
        raw_direction = raw_dir, clinical_direction = clin_dir,
        stringsAsFactors = FALSE
      )
    }
  }

  list(
    fit = fit,
    anova = anova_res,
    anova_df = nlme_anova_to_df(anova_res, outcome),
    emmeans = emm_df,
    pairwise = if (length(pair_rows) > 0) do.call(rbind, pair_rows) else NULL,
    pairwise_raw = pair_df,
    diagnostics = diag_tbl
  )
}

lrt_nested <- function(full, reduced, effect_label, outcome) {
  if (is.null(full) || is.null(reduced)) {
    return(data.frame(outcome = outcome, effect = effect_label, chisq = NA_real_, df = NA_real_, p_value = NA_real_, note = "模型不可比较", stringsAsFactors = FALSE))
  }
  llf <- logLik(full)
  llr <- logLik(reduced)
  d_ll <- as.numeric(llf) - as.numeric(llr)
  d_df <- attr(llf, "df") - attr(llr, "df")
  if (d_df <= 0 || d_ll < -1e-8) {
    return(data.frame(outcome = outcome, effect = effect_label, chisq = NA_real_, df = d_df, p_value = NA_real_, note = "嵌套比较异常，需人工复核", stringsAsFactors = FALSE))
  }
  chisq <- 2 * d_ll
  pval <- pchisq(chisq, d_df, lower.tail = FALSE)
  data.frame(outcome = outcome, effect = effect_label, chisq = chisq, df = d_df, p_value = pval, note = "", stringsAsFactors = FALSE)
}

fit_ordinal_clmm <- function(df, outcome, adjust = "bonferroni") {
  d <- df %>% left_join(get_baseline_map(df, outcome), by = ID_COL)
  base_col <- paste0(outcome, "_BASE")
  d <- d %>% filter(!is.na(.data[[outcome]]), !is.na(.data[[base_col]]))
  if (nrow(d) == 0) return(NULL)
  d[[outcome]] <- ordered(d[[outcome]])
  d[[base_col]] <- ordered(d[[base_col]])

  f_full <- as.formula(sprintf("%s ~ %s * %s + %s + (1 | %s)", outcome, GROUP_COL, TIME_COL, base_col, ID_COL))
  f_add  <- as.formula(sprintf("%s ~ %s + %s + %s + (1 | %s)", outcome, GROUP_COL, TIME_COL, base_col, ID_COL))
  f_grp  <- as.formula(sprintf("%s ~ %s + %s + (1 | %s)", outcome, TIME_COL, base_col, ID_COL))
  f_time <- as.formula(sprintf("%s ~ %s + %s + (1 | %s)", outcome, GROUP_COL, base_col, ID_COL))

  warn <- character(0)
  safe_fit <- function(fm) {
    withCallingHandlers(
      tryCatch(ordinal::clmm(fm, data = d, link = "logit", Hess = TRUE, nAGQ = 5),
               error = function(e) { warn <<- c(warn, e$message); NULL }),
      warning = function(w) { warn <<- c(warn, conditionMessage(w)); invokeRestart("muffleWarning") }
    )
  }

  fit_full <- safe_fit(f_full)
  if (is.null(fit_full)) return(NULL)
  fit_add  <- safe_fit(f_add)
  fit_grp  <- safe_fit(f_grp)
  fit_time <- safe_fit(f_time)

  anova_tbl <- bind_rows(
    lrt_nested(fit_full, fit_add, paste0(GROUP_COL, ":", TIME_COL), outcome),
    lrt_nested(fit_add, fit_grp, GROUP_COL, outcome),
    lrt_nested(fit_add, fit_time, TIME_COL, outcome)
  )

  emm <- emmeans::emmeans(fit_full, as.formula(paste("~", GROUP_COL, "|", TIME_COL)), mode = "latent")
  emm_df <- as.data.frame(summary(emm, infer = c(TRUE, TRUE)))
  emm_df$outcome <- outcome
  emm_df$scale <- "latent"
  names(emm_df)[names(emm_df) == GROUP_COL] <- "group"
  names(emm_df)[names(emm_df) == TIME_COL] <- "time"

  pair_df <- as.data.frame(summary(pairs(emm, adjust = adjust), infer = c(TRUE, TRUE)))
  pair_df$outcome <- outcome
  pair_df$scale <- "latent"
  if (TIME_COL %in% names(pair_df)) names(pair_df)[names(pair_df) == TIME_COL] <- "time"
  pair_df <- pair_df %>% filter(time %in% POSTBASELINE_TIMES)

  diag_tbl <- data.frame(
    outcome = outcome,
    model_class = class(fit_full)[1],
    n_obs = nrow(d),
    n_id = dplyr::n_distinct(d[[ID_COL]]),
    random_structure = "(1 | 患者ID)",
    singular_fit = NA,
    AIC = AIC(fit_full),
    BIC = BIC(fit_full),
    sigma = NA,
    max_abs_pearson = NA,
    n_abs_pearson_gt_3 = NA,
    messages = collapse_messages(warn),
    stringsAsFactors = FALSE
  )

  pair_rows <- list()
  pairs_list <- list(c(1,2), c(1,3), c(1,4), c(2,3), c(2,4), c(3,4))
  higher_better <- !(outcome %in% c("CSS", "MAS", "TUGT"))

  for (t in POSTBASELINE_TIMES) {
    pw_t <- pair_df[pair_df$time == t, ]
    for (pr in pairs_list) {
      g_a <- pr[1]; g_b <- pr[2]
      fwd_name <- paste0(GROUP_COL, g_a, " - ", GROUP_COL, g_b)
      rev_name <- paste0(GROUP_COL, g_b, " - ", GROUP_COL, g_a)

      row_idx <- which(pw_t$contrast == fwd_name)
      if (length(row_idx) > 0) {
        est <- pw_t$estimate[row_idx[1]]
        p <- pw_t$p.value[row_idx[1]]
        se <- if ("SE" %in% names(pw_t)) pw_t$SE[row_idx[1]] else NA
        ci_l <- if ("lower.CL" %in% names(pw_t)) pw_t$lower.CL[row_idx[1]] else if ("asymp.LCL" %in% names(pw_t)) pw_t$asymp.LCL[row_idx[1]] else NA
        ci_u <- if ("upper.CL" %in% names(pw_t)) pw_t$upper.CL[row_idx[1]] else if ("asymp.UCL" %in% names(pw_t)) pw_t$asymp.UCL[row_idx[1]] else NA
      } else {
        row_idx <- which(pw_t$contrast == rev_name)
        if (length(row_idx) == 0) next
        est <- -pw_t$estimate[row_idx[1]]
        p <- pw_t$p.value[row_idx[1]]
        se <- if ("SE" %in% names(pw_t)) pw_t$SE[row_idx[1]] else NA
        ci_l <- if ("upper.CL" %in% names(pw_t)) -pw_t$upper.CL[row_idx[1]] else if ("asymp.UCL" %in% names(pw_t)) -pw_t$asymp.UCL[row_idx[1]] else NA
        ci_u <- if ("lower.CL" %in% names(pw_t)) -pw_t$lower.CL[row_idx[1]] else if ("asymp.LCL" %in% names(pw_t)) -pw_t$asymp.LCL[row_idx[1]] else NA
      }

      if (length(est) == 0 || length(p) == 0) next

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
        metric = outcome, time = t, contrast = paste0("G", g_a, "_vs_G", g_b),
        estimate = est, se = se, p = p,
        ci_lower = ci_l, ci_upper = ci_u,
        raw_direction = raw_dir, clinical_direction = clin_dir,
        stringsAsFactors = FALSE
      )
    }
  }

  list(
    fit = fit_full,
    anova = anova_tbl,
    anova_df = anova_tbl,
    emmeans = emm_df,
    pairwise = if (length(pair_rows) > 0) do.call(rbind, pair_rows) else NULL,
    pairwise_raw = pair_df,
    diagnostics = diag_tbl
  )
}

extract_primary_result <- function(primary_obj) {
  if (is.null(primary_obj) || is.null(primary_obj$pairwise_raw)) return(data.frame())
  pw <- primary_obj$pairwise_raw %>% filter(time == PRIMARY_TIME)
  if (nrow(pw) == 0) return(data.frame())

  wanted1 <- paste0(GROUP_COL, PRIMARY_GA, " - ", GROUP_COL, PRIMARY_GB)
  wanted2 <- paste0(GROUP_COL, PRIMARY_GB, " - ", GROUP_COL, PRIMARY_GA)

  row1 <- pw[pw$contrast == wanted1, , drop = FALSE]
  row2 <- pw[pw$contrast == wanted2, , drop = FALSE]

  if (nrow(row1) == 1) {
    est <- row1$estimate[1]
    se  <- if ("SE" %in% names(row1)) row1$SE[1] else NA
    lcl <- if ("lower.CL" %in% names(row1)) row1$lower.CL[1] else if ("asymp.LCL" %in% names(row1)) row1$asymp.LCL[1] else NA
    ucl <- if ("upper.CL" %in% names(row1)) row1$upper.CL[1] else if ("asymp.UCL" %in% names(row1)) row1$asymp.UCL[1] else NA
    p   <- row1$p.value[1]
  } else if (nrow(row2) == 1) {
    est <- -row2$estimate[1]
    se  <- if ("SE" %in% names(row2)) row2$SE[1] else NA
    lcl <- if ("upper.CL" %in% names(row2)) -row2$upper.CL[1] else if ("asymp.UCL" %in% names(row2)) -row2$asymp.UCL[1] else NA
    ucl <- if ("lower.CL" %in% names(row2)) -row2$lower.CL[1] else if ("asymp.LCL" %in% names(row2)) -row2$asymp.LCL[1] else NA
    p   <- row2$p.value[1]
  } else {
    return(data.frame())
  }

  data.frame(
    outcome = PRIMARY_OUTCOME,
    primary_time = PRIMARY_TIME,
    primary_contrast = paste0("G", PRIMARY_GA, " vs G", PRIMARY_GB),
    estimate = est,
    se = se,
    ci_lower = lcl,
    ci_upper = ucl,
    p_value = p,
    interpretation = ifelse(is.na(est), "NA", ifelse(est > 0, "G1高于G2", ifelse(est < 0, "G1低于G2", "无差异"))),
    stringsAsFactors = FALSE
  )
}

# ============================================================================
# 输出函数
# ============================================================================

write_methods_text <- function(outdir, adjust_method) {
  adj_text <- if (adjust_method == "holm") "adjusted using the Holm-Bonferroni method" else "adjusted using the Bonferroni method"
  txt <- c(
    "Statistical analysis",
    "",
    "This was a four-arm parallel randomized controlled trial with repeated measurements at baseline (T0), 2 weeks (T1), 3 weeks (T2), and 2 months (T3).",
    "The primary endpoint was FMA_LE at T2, consistent with the sample size calculation.",
    "The primary confirmatory comparison was G1 versus G2 at T2.",
    "Baseline characteristics were summarized descriptively only and were not compared using significance tests.",
    "For the primary continuous outcome, a linear mixed model was fitted with fixed effects for group, time, group-by-time interaction, and baseline FMA_LE, with participant as a random effect.",
    "Time was treated as a categorical factor.",
    "Unstructured residual covariance was approximated using a general correlation matrix (corSymm) combined with heteroscedastic weights (varIdent) across time points.",
    "A random slope for time was attempted first; when singular or unstable, the model was simplified to a random-intercept structure, and this decision was documented in the diagnostics output.",
    "The primary treatment effect was estimated as the model-based marginal mean difference between G1 and G2 at T2, reported with 95% confidence interval and P value.",
    "Other continuous outcomes were analyzed using the same framework with outcome-specific baseline adjustment.",
    "The ordinal outcome MAS was analyzed using a cumulative link mixed model with logit link and subject-specific random intercept.",
    sprintf("Secondary and exploratory pairwise post-baseline comparisons were %s.", adj_text),
    "Missing data were summarized by outcome, group, and visit; the mixed-model analyses used all available observed data under a missing-at-random working assumption.",
    sprintf("A two-sided alpha level of %.2f was used for the primary confirmatory analysis.", ALPHA)
  )
  writeLines(txt, file.path(outdir, "statistical_methods_for_manuscript.txt"), useBytes = TRUE)
}

write_report <- function(df, primary_res, diag_tbl, outdir, adjust_method) {
  adj_label <- if (adjust_method == "holm") "Holm correction" else "Bonferroni correction"
  lines <- c(
    sprintf("# RCT longitudinal analysis report (%s)", adj_label),
    "",
    "## Trial structure",
    "- Four-arm randomized controlled trial.",
    "- Visits: T0 baseline, T1 2 weeks, T2 3 weeks, T3 2 months.",
    sprintf("- Primary endpoint: %s at %s.", PRIMARY_OUTCOME, PRIMARY_TIME),
    sprintf("- Primary confirmatory comparison: G%s vs G%s.", PRIMARY_GA, PRIMARY_GB),
    "",
    "## Dataset overview",
    sprintf("- Records: %s", nrow(df)),
    sprintf("- Participants: %s", dplyr::n_distinct(df[[ID_COL]])),
    ""
  )
  if (nrow(primary_res) > 0) {
    lines <- c(lines,
      "## Primary result",
      sprintf("- Estimate (G1-G2) at T2: %s", fmt_num(primary_res$estimate[1], 3)),
      sprintf("- 95%% CI: %s to %s", fmt_num(primary_res$ci_lower[1], 3), fmt_num(primary_res$ci_upper[1], 3)),
      sprintf("- P value: %s", fmt_num(primary_res$p_value[1], 4)),
      sprintf("- Interpretation: %s", primary_res$interpretation[1]),
      ""
    )
  }
  if (nrow(diag_tbl) > 0) {
    lines <- c(lines, "## Diagnostics", "")
    for (i in seq_len(nrow(diag_tbl))) {
      lines <- c(lines,
        sprintf("- %s: model=%s; random=%s; AIC=%s; BIC=%s; messages=%s",
                diag_tbl$outcome[i], diag_tbl$model_class[i], diag_tbl$random_structure[i],
                fmt_num(diag_tbl$AIC[i], 2), fmt_num(diag_tbl$BIC[i], 2),
                ifelse(nzchar(diag_tbl$messages[i]), diag_tbl$messages[i], "none"))
      )
    }
    lines <- c(lines, "")
  }
  writeLines(lines, file.path(outdir, "analysis_report.md"), useBytes = TRUE)
}

write_session_info <- function(outdir) {
  txt <- capture.output(sessionInfo())
  writeLines(txt, file.path(outdir, "sessionInfo.txt"), useBytes = TRUE)
}

# ============================================================================
# 主流程
# ============================================================================

raw_df <- read_input(input_file)
df <- clean_data(raw_df)
cat("数据加载完成:", nrow(df), "条记录,", length(unique(df[[ID_COL]])), "名患者\n")

# 描述/基线/缺失表
desc_tbl <- make_descriptive_table(df)
baseline_tbl <- make_baseline_table(df)
missing_tbl <- make_missingness_table(df)

# T0 基线检验（用于 stdout 第五节）
baseline_rows <- lapply(names(OUTCOMES), function(m) {
  baseline_test(df, m, type = OUTCOMES[[m]])
})

# 描述统计（用于 stdout 第四节）
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

# 拟合模型
results <- list()
for (metric in names(OUTCOMES)) {
  results[[metric]] <- if (OUTCOMES[[metric]] == "continuous")
    fit_continuous_lmm_nlme(df, metric, adjust = ADJUST_METHOD)
  else
    fit_ordinal_clmm(df, metric, adjust = ADJUST_METHOD)
}

primary_obj <- results[[PRIMARY_OUTCOME]]
primary_res <- extract_primary_result(primary_obj)

primary_anova <- if (!is.null(primary_obj)) primary_obj$anova_df else data.frame()
primary_emm   <- if (!is.null(primary_obj)) primary_obj$emmeans else data.frame()
primary_pw    <- if (!is.null(primary_obj)) primary_obj$pairwise_raw else data.frame()

secondary_omnibus <- bind_rows(lapply(setdiff(names(results), PRIMARY_OUTCOME), function(nm) if (!is.null(results[[nm]])) results[[nm]]$anova_df else NULL))
secondary_pw <- bind_rows(lapply(setdiff(names(results), PRIMARY_OUTCOME), function(nm) if (!is.null(results[[nm]])) results[[nm]]$pairwise_raw else NULL))
all_diag <- bind_rows(lapply(results, function(x) if (!is.null(x)) x$diagnostics else NULL))

# 文件输出
if (!is.null(outdir)) {
  write.csv(baseline_tbl, file.path(outdir, "baseline_table.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(desc_tbl, file.path(outdir, "descriptive_all.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(missing_tbl, file.path(outdir, "missingness_table.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(primary_res, file.path(outdir, "primary_result_fma_t2_g1_vs_g2.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(primary_anova, file.path(outdir, "primary_model_anova.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(primary_emm, file.path(outdir, "primary_emmeans_all_times.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(primary_pw, file.path(outdir, "primary_pairwise_postbaseline.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(secondary_omnibus, file.path(outdir, "secondary_omnibus.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(secondary_pw, file.path(outdir, "secondary_pairwise_postbaseline.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(all_diag, file.path(outdir, "model_diagnostics.csv"), row.names = FALSE, fileEncoding = "UTF-8")
  write_methods_text(outdir, ADJUST_METHOD)
  write_report(df, primary_res, all_diag, outdir, ADJUST_METHOD)
  write_session_info(outdir)
  cat("文件已导出到:", normalizePath(outdir), "\n")
}

# ========================================================================
# stdout: Markdown 输出（5节）
# ========================================================================

# 为 lmm_results 建立兼容旧格式的结构
lmm_results <- list()
for (metric in names(OUTCOMES)) {
  if (!is.null(results[[metric]])) {
    lmm_results[[metric]] <- list(
      pairwise = results[[metric]]$pairwise,
      anova = results[[metric]]$anova,
      fit = results[[metric]]$fit
    )
  }
}

# ------------------------------------------------------------------------
# 一、ANOVA 主效应与交互效应
# ------------------------------------------------------------------------
cat("\n================================================================================\n")
cat("一、LMM / CLMM 主效应与交互效应\n")
cat("================================================================================\n\n")
cat("| 参数 | 效应 | 统计量 | df | P值 |\n")
cat("|------|------|--------|----|-----|\n")

for (metric in names(lmm_results)) {
  res_obj <- lmm_results[[metric]]
  if (is.null(res_obj) || is.null(res_obj$anova)) next
  anova_res <- res_obj$anova

  if (metric == "MAS") {
    for (j in seq_len(nrow(anova_res))) {
      cat(sprintf("| %s | %s | Chisq=%.3f | %.0f | %.4f |\n",
                  metric, anova_res$effect[j], anova_res$chisq[j],
                  anova_res$df[j], anova_res$p_value[j]))
    }
  } else {
    effects <- rownames(anova_res)
    for (eff in effects) {
      numdf <- anova_res[eff, "numDF"]
      dendf <- anova_res[eff, "denDF"]
      fval <- anova_res[eff, "F-value"]
      pval <- anova_res[eff, "p-value"]
      cat(sprintf("| %s | %s | F=%.3f | %.0f, %.1f | %.4f |\n",
                  metric, eff, fval, numdf, dendf, pval))
    }
  }
}

cat("\n注：LMM采用nlme条件F检验（sequential Type I）+ corSymm + varIdent（非结构化残差协方差）；CLMM采用似然比检验(LRT)。\n")

# ------------------------------------------------------------------------
# 二、目标达成总表
# ------------------------------------------------------------------------
summary_rows <- list()
for (metric in c("FMA_LE", "ADL", "BBS", "MAS", "CSS")) {
  for (t in c("T2", "T3")) {
    pair_df <- if (!is.null(lmm_results[[metric]])) lmm_results[[metric]]$pairwise else NULL
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

cat("\n================================================================================\n")
adj_label <- if (ADJUST_METHOD == "holm") "Holm-Bonferroni" else "Bonferroni"
cat(sprintf("二、LMM / CLMM 目标达成总表 (事后检验 P值经%s校正)\n", adj_label))
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

cat(sprintf("\n注：事后检验采用emmeans进行两两比较，P值经%s法校正。\n", adj_label))
cat("对于每个指标在每个时间点，共进行C(4,2)=6次组间比较。\n")

# ------------------------------------------------------------------------
# 三、详细 Post-hoc 结果
# ------------------------------------------------------------------------
cat("\n================================================================================\n")
cat(sprintf("三、事后检验详细结果 (Estimate, 95%% CI, %s-adjusted P)\n", adj_label))
cat("================================================================================\n\n")
cat("| 参数 | 时点 | 对比 | Estimate | 95% CI | Adj. P | 方向 |\n")
cat("|------|------|------|----------|--------|--------|------|\n")

for (metric in names(lmm_results)) {
  res_obj <- lmm_results[[metric]]
  if (is.null(res_obj) || is.null(res_obj$pairwise)) next
  pw <- res_obj$pairwise
  for (i in seq_len(nrow(pw))) {
    ci_str <- sprintf("%.2f to %.2f", pw$ci_lower[i], pw$ci_upper[i])
    cat(sprintf("| %s | %s | %s | %.3f | %s | %.4f | %s |\n",
                pw$metric[i], pw$time[i], pw$contrast[i],
                pw$estimate[i], ci_str, pw$p[i], pw$clinical_direction[i]))
  }
}

# ------------------------------------------------------------------------
# 四、描述统计
# ------------------------------------------------------------------------
cat("\n================================================================================\n")
cat("四、所有参数 × 所有时间点 × 各组 均值 ± 标准差 (n)\n")
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
        cells <- c(cells, sprintf("%.2f±NA (n=%d)", d$mean, d$n))
      } else {
        cells <- c(cells, sprintf("%.2f±%.2f (n=%d)", d$mean, d$sd, d$n))
      }
    }
    cat("| ", paste(cells, collapse = " | "), " |\n", sep = "")
  }
}

# ------------------------------------------------------------------------
# 五、T0 基线 P值汇总
# ------------------------------------------------------------------------
cat("\n================================================================================\n")
cat("五、T0 基线 P值汇总\n")
cat("================================================================================\n\n")
cat("| 参数 | ANOVA P | Merge(G1+2 vs G3+4) P | 状态 |\n")
cat("|------|---------|----------------------|------|\n")
for (r in baseline_rows) {
  status <- if (r$aligned) "✅ 对齐" else "❌ 未对齐"
  cat(sprintf("| %s | %.4f | %.4f | %s |\n", r$metric, r$anova_p, r$merge_p, status))
}
