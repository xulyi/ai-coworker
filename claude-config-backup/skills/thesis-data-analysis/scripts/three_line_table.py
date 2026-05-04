#!/usr/bin/env python3
"""
论文三线表生成助手
生成符合学术规范的 Markdown / LaTeX 三线表
"""

import pandas as pd
import sys
from typing import Optional


def create_three_line_table(
    df: pd.DataFrame,
    caption: str = "",
    note: str = "",
    output_format: str = "markdown"
) -> str:
    """
    生成三线表

    Args:
        df: pandas DataFrame
        caption: 表格标题
        note: 表注（如统计方法说明、显著性标记说明等）
        output_format: 输出格式 ("markdown" 或 "latex")

    Returns:
        格式化后的表格字符串
    """
    if output_format == "markdown":
        return _create_markdown_table(df, caption, note)
    elif output_format == "latex":
        return _create_latex_table(df, caption, note)
    else:
        raise ValueError("output_format 必须是 'markdown' 或 'latex'")


def _create_markdown_table(df: pd.DataFrame, caption: str, note: str) -> str:
    """生成 Markdown 格式的三线表"""
    lines = []

    # 标题
    if caption:
        lines.append(f"**表 1** {caption}")
        lines.append("")

    # 表头（顶部线）
    header = " | ".join(df.columns)
    lines.append(f"| {header} |")
    separator = "|" + "|".join([" --- " for _ in df.columns]) + "|"
    lines.append(separator)

    # 数据行
    for _, row in df.iterrows():
        row_str = " | ".join([str(v) for v in row.values])
        lines.append(f"| {row_str} |")

    # 表注
    if note:
        lines.append("")
        lines.append(f"*注：{note}*")

    return "\n".join(lines)


def _create_latex_table(df: pd.DataFrame, caption: str, note: str) -> str:
    """生成 LaTeX booktabs 格式的三线表"""
    num_cols = len(df.columns)
    col_spec = "l" + "c" * (num_cols - 1)  # 第一列左对齐，其余居中

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{caption}}}",
    ]

    # 如果有表注，使用 threeparttable 包裹
    if note:
        lines.append("\\begin{threeparttable}")

    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append("\\toprule")

    # 表头
    header = " & ".join(df.columns) + " \\\\"
    lines.append(header)
    lines.append("\\midrule")

    # 数据行
    for _, row in df.iterrows():
        row_str = " & ".join([str(v) for v in row.values]) + " \\\\"
        lines.append(row_str)

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")

    if note:
        lines.append(f"\\begin{{tablenotes}}")
        lines.append(f"\\item {note}")
        lines.append("\\end{tablenotes}")
        lines.append("\\end{threeparttable}")

    lines.append("\\end{table}")

    return "\n".join(lines)


def calculate_descriptive_stats(
    df: pd.DataFrame,
    group_col: Optional[str] = None,
    value_cols: Optional[list] = None,
    decimal_places: int = 2
) -> pd.DataFrame:
    """
    计算描述性统计量，生成论文格式的三线表数据

    Args:
        df: 原始数据 DataFrame
        group_col: 分组变量列名（如组别、实验条件等）
        value_cols: 需要统计的数值变量列名列表
        decimal_places: 保留小数位数

    Returns:
        格式化后的统计结果 DataFrame
    """
    if value_cols is None:
        value_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        # 自动排除分组变量，避免被纳入统计
        if group_col and group_col in value_cols:
            value_cols.remove(group_col)

    results = []

    if group_col:
        # 按组计算统计量
        for group_name, group_df in df.groupby(group_col):
            row = {'组别': group_name}
            for col in value_cols:
                mean = group_df[col].mean()
                std = group_df[col].std()
                row[col] = f"{mean:.{decimal_places}f} ± {std:.{decimal_places}f}"
            # 将 n 放在所有统计量计算完成后赋值
            row['n'] = len(group_df)
            results.append(row)
    else:
        # 整体统计
        row = {}
        for col in value_cols:
            mean = df[col].mean()
            std = df[col].std()
            row[col] = f"{mean:.{decimal_places}f} ± {std:.{decimal_places}f}"
        row['n'] = len(df)
        results.append(row)

    return pd.DataFrame(results)


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python three_line_table.py <csv文件路径> [markdown|latex]")
        print("示例: python three_line_table.py data.csv markdown")
        print("      python three_line_table.py data.csv latex")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "markdown"

    try:
        df = pd.read_csv(csv_path)
        table = create_three_line_table(df, output_format=output_format)
        print(table)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
