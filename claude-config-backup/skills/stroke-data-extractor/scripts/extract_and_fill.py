#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脑卒中论文数据提取与补全脚本
整合Python提取和AI语义理解补全的完整流程
"""

import re
import json
import csv
import os
import sys
from pathlib import Path


def load_json(filepath):
    """加载JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, filepath):
    """保存JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_csv(data, filepath):
    """保存CSV文件"""
    if not data:
        return
    fieldnames = list(data[0].keys())
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def semantic_fill_brunnstrom(record, content):
    """语义理解补全Brunnstrom"""
    if record.get('Brunnstrom_上肢') and record['Brunnstrom_上肢']:
        return

    patterns = [
        # 标准格式
        r'Brunnstrom运动功能分期[:：]\s*(?:左|右)?(?:侧)?(?:上肢)?\s*[:：]?\s*((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期?[,，\-\s]*(?:左|右)?(?:手)?\s*((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期?[,，\-\s]*(?:左|右)?(?:侧)?(?:下肢)?\s*[:：]?\s*((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期?',
        # 单值
        r'Brunnstrom运动功能分期[:：]\s*(欠配合|NT|TN)',
        # 无冒号格式
        r'Brunnstrom运动功能分期\s*(?:左|右)?(?:侧)?(?:上肢)?\s*([ⅠⅡⅢⅣⅤⅥ\d])\s*期',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 1:
                # 单值（欠配合/NT）
                val = groups[0].strip()
                record['Brunnstrom_上肢'] = val
                record['Brunnstrom_手'] = val
                record['Brunnstrom_下肢'] = val
            else:
                # 三值
                record['Brunnstrom_上肢'] = groups[0].strip() + ('期' if not groups[0].strip().endswith('期') else '')
                record['Brunnstrom_手'] = groups[1].strip() + ('期' if not groups[1].strip().endswith('期') else '')
                record['Brunnstrom_下肢'] = groups[2].strip() + ('期' if not groups[2].strip().endswith('期') else '')
            return


def semantic_fill_ashworth(record, content):
    """语义理解补全Ashworth"""
    if record.get('改良Ashworth_上肢') and record['改良Ashworth_上肢']:
        return

    patterns = [
        (r'[Aa]shworth肌(?:张力|痉挛)评定[：:]\s*上肢[:：]?\s*(欠配合|下降|降低|NT|TN|[\d\+]+)\s*级?', 'special'),
        (r'[Aa]shworth肌(?:张力|痉挛)评定[：:]\s*(欠配合|下降|降低)', 'single'),
        (r'[Aa]shworth肌(?:张力|痉挛)评定[：:]\s*左?上肢[:：]?\s*(\d+)', 'normal'),
        (r'[Aa]shworth肌(?:张力|痉挛)评定[：:]\s*右?上肢[:：]\s*(\d+)', 'normal'),
        (r'改良ashworth肌痉挛评分[：:]\s*上肢[：:](\d+)', 'normal'),
    ]

    for pattern, ptype in patterns:
        match = re.search(pattern, content)
        if match:
            val = match.group(1).strip()
            if ptype in ['special', 'single'] and val in ['欠配合', '下降', '降低', 'NT', 'TN']:
                record['改良Ashworth_上肢'] = val
                record['改良Ashworth_下肢'] = val
            else:
                record['改良Ashworth_上肢'] = val + '级' if not val.endswith('级') else val
                # 查找下肢
                leg_match = re.search(r'下肢[:：]?\s*(欠配合|下降|降低|NT|TN|[\d\+]+)\s*级?', content)
                if leg_match:
                    leg_val = leg_match.group(1)
                    if leg_val in ['欠配合', '下降', '降低', 'NT', 'TN']:
                        record['改良Ashworth_下肢'] = leg_val
                    else:
                        record['改良Ashworth_下肢'] = leg_val + '级'
            return


def semantic_fill_balance(record, content):
    """语义理解补全坐位/站位平衡"""
    # 坐位平衡
    if not record.get('坐位平衡') or record['坐位平衡'] == '':
        patterns = [
            r'坐[:：]?位平衡[:：]?\s*(欠配合|NT|TN|\d+)\s*级?',
            r'坐[:：]?位平衡[:：]\s*(\d+)',
            r'坐、站位平衡.*?坐位[:：]?(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                val = match.group(1)
                if val in ['欠配合', 'NT', 'TN']:
                    record['坐位平衡'] = val
                else:
                    record['坐位平衡'] = val + '级'
                break

    # 站位平衡
    if not record.get('站位平衡') or record['站位平衡'] == '':
        patterns = [
            r'站[:：]?位平衡[:：]?\s*(欠配合|NT|TN|\d+)\s*级?',
            r'站[:：]?位平衡[:：]\s*(\d+)',
            r'站[:：]?位平衡[:：]\s*([\d]+)\s*级',
            r'坐、站位平衡.*?站位[:：]?(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                val = match.group(1)
                if val in ['欠配合', 'NT', 'TN']:
                    record['站位平衡'] = val
                else:
                    record['站位平衡'] = val + '级'
                break


def semantic_fill_adl(record, content):
    """语义理解补全ADL评分"""
    if record.get('ADL评分') and record['ADL评分'] > 0:
        return

    patterns = [
        r'ADL评定[:：]?\s*(\d+)\s*分',
        r'ADL[:：]?\s*(\d+)',
        r'日常生活能力.*?([\d\.]+)\s*分',
        r'ADL评分[:：]\s*(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            try:
                record['ADL评分'] = int(float(match.group(1)))
            except:
                pass
            return


def semantic_fill_duration(record, content):
    """语义理解补全病程"""
    if record.get('病程天数') and record['病程天数'] > 0:
        return

    patterns = [
        r'(?:发病|病程|入院).*?(\d+)\s*(月|天|年|周)',
        r'(\d+)\s*(月|天|年|周).*?(?:入院|病程)',
        r'病程(\d+)\s*(月|天|年|周)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            try:
                val = float(match.group(1))
                unit = match.group(2)
                record['病程数值'] = val
                record['病程单位'] = unit
                if unit == '月':
                    record['病程天数'] = val * 30
                elif unit == '年':
                    record['病程天数'] = val * 365
                elif unit == '天':
                    record['病程天数'] = val
                elif unit == '周':
                    record['病程天数'] = val * 7
            except:
                pass
            return


def fill_missing_data(data, source_dir):
    """遍历所有记录，使用语义理解补全缺失数据"""
    filled_count = {
        'Brunnstrom': 0,
        'Ashworth': 0,
        '坐位平衡': 0,
        '站位平衡': 0,
        'ADL': 0,
        '病程': 0,
    }

    for record in data:
        if not record.get('源文件'):
            continue

        filepath = record['源文件']
        if not os.path.exists(filepath):
            # 尝试从文件名重建路径
            filename = Path(filepath).name
            filepath = os.path.join(source_dir, filename)
            if not os.path.exists(filepath):
                continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 各项补全
        if not record.get('Brunnstrom_上肢') or record['Brunnstrom_上肢'] == '':
            semantic_fill_brunnstrom(record, content)
            if record.get('Brunnstrom_上肢') and record['Brunnstrom_上肢'] != '':
                filled_count['Brunnstrom'] += 1

        if not record.get('改良Ashworth_上肢') or record['改良Ashworth_上肢'] == '':
            semantic_fill_ashworth(record, content)
            if record.get('改良Ashworth_上肢') and record['改良Ashworth_上肢'] != '':
                filled_count['Ashworth'] += 1

        if not record.get('坐位平衡') or record['坐位平衡'] == '':
            semantic_fill_balance(record, content)
            if record.get('坐位平衡') and record['坐位平衡'] != '':
                filled_count['坐位平衡'] += 1

        if not record.get('ADL评分') or record['ADL评分'] == 0:
            semantic_fill_adl(record, content)
            if record.get('ADL评分') and record['ADL评分'] > 0:
                filled_count['ADL'] += 1

        if not record.get('病程天数') or record['病程天数'] == 0:
            semantic_fill_duration(record, content)
            if record.get('病程天数') and record['病程天数'] > 0:
                filled_count['病程'] += 1

    return filled_count


def print_statistics(data):
    """打印统计信息"""
    print("\n" + "=" * 70)
    print("病案数据提取报告 - 补全后")
    print("=" * 70)
    print(f"处理文件总数: {len(data)}")

    # 性别统计
    male = sum(1 for r in data if r.get('性别') == '男')
    female = sum(1 for r in data if r.get('性别') == '女')
    print(f"\n性别分布: 男 {male}人, 女 {female}人")

    # 年龄统计
    ages = [r['年龄'] for r in data if r.get('年龄', 0) > 0]
    if ages:
        print(f"年龄范围: {min(ages)}-{max(ages)}岁, 平均 {sum(ages)/len(ages):.1f}岁")

    # 各字段完整度
    print("\n字段完整度统计:")
    print("-" * 50)
    fields = [
        ('病案号/姓名', '病案号', lambda x: x and x != ''),
        ('性别', '性别', lambda x: x and x != ''),
        ('年龄', '年龄', lambda x: x and x != 0),
        ('病程记录', '病程天数', lambda x: x and x != 0),
        ('Brunnstrom评估', 'Brunnstrom_上肢', lambda x: x and x != ''),
        ('Ashworth评估', '改良Ashworth_上肢', lambda x: x and x != ''),
        ('ADL评分', 'ADL评分', lambda x: x and x != 0),
        ('坐位平衡', '坐位平衡', lambda x: x and x != ''),
        ('站位平衡', '站位平衡', lambda x: x and x != ''),
    ]

    for label, field, check in fields:
        filled = sum(1 for r in data if check(r.get(field)))
        pct = filled / len(data) * 100
        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
        print(f"{label:15} | {bar} | {filled:3}/{len(data)} ({pct:5.1f}%)")


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python extract_and_fill.py <input_dir> <output_prefix>")
        print("示例: python extract_and_fill.py '/path/to/records' 'report'")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_prefix = sys.argv[2]

    # 第一步：运行主提取脚本
    print("步骤1: 运行主提取脚本...")
    import subprocess

    csv_path = f"{output_prefix}.csv"
    json_path = f"{output_prefix}.json"

    # 优先使用skill目录下的脚本，回退到用户目录
    script_path = os.path.join(os.path.dirname(__file__), "extract_medical_records.py")
    if not os.path.exists(script_path):
        script_path = "/Users/leyixu/extract_medical_records.py"
    if not os.path.exists(script_path):
        print(f"错误: 找不到主提取脚本 {script_path}")
        print("请确保脚本路径正确")
        sys.exit(1)

    result = subprocess.run([
        'python3', script_path,
        '--dir', input_dir,
        '--csv', csv_path,
        '--json', json_path
    ], capture_output=True, text=True)

    print(result.stdout)
    if result.returncode != 0:
        print(f"提取失败: {result.stderr}")
        sys.exit(1)

    # 第二步：加载JSON数据
    print("\n步骤2: 加载提取结果...")
    data = load_json(json_path)

    # 第三步：语义理解补全
    print("\n步骤3: AI语义理解补全缺失数据...")
    filled_count = fill_missing_data(data, input_dir)

    print(f"  补全Brunnstrom: {filled_count['Brunnstrom']}条")
    print(f"  补全Ashworth: {filled_count['Ashworth']}条")
    print(f"  补全坐位平衡: {filled_count['坐位平衡']}条")
    print(f"  补全站位平衡: {filled_count['站位平衡']}条")
    print(f"  补全ADL: {filled_count['ADL']}条")
    print(f"  补全病程: {filled_count['病程']}条")

    # 第四步：保存补全后的结果
    print("\n步骤4: 保存补全后的结果...")
    filled_csv = f"{output_prefix}_filled.csv"
    filled_json = f"{output_prefix}_filled.json"

    save_json(data, filled_json)
    save_csv(data, filled_csv)

    print(f"  CSV: {filled_csv}")
    print(f"  JSON: {filled_json}")

    # 第五步：打印统计
    print_statistics(data)

    print("\n" + "=" * 70)
    print("处理完成!")
    print("=" * 70)


if __name__ == '__main__':
    main()
