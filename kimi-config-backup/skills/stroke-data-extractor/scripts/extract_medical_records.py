#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
病案数据提取工具
从Markdown格式的病案记录中提取结构化数据
"""

import re
import os
import json
import csv
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MedicalRecord:
    """病案记录数据结构"""
    # 基本信息
    case_id: str = ""
    name: str = ""
    gender: str = ""
    age: int = 0
    admission_number: str = ""  # 第几次入院

    # 病程信息
    duration_value: float = 0.0
    duration_unit: str = ""  # 天/月/年
    duration_days: float = 0.0  # 转换为天数

    # 体格检查
    temperature: float = 0.0
    pulse: int = 0
    blood_pressure_systolic: int = 0
    blood_pressure_diastolic: int = 0
    respiratory_rate: int = 0

    # 专科检查
    brunnstrom_arm: str = ""
    brunnstrom_hand: str = ""
    brunnstrom_leg: str = ""
    ashworth_arm: str = ""
    ashworth_leg: str = ""
    adl_score: int = 0
    sitting_balance: str = ""
    standing_balance: str = ""

    # 诊断
    stroke_diagnoses: List[str] = None  # 脑卒中相关诊断
    all_diagnoses: List[str] = None  # 所有诊断

    # 营养信息
    height_cm: float = 0.0
    weight_kg: float = 0.0
    bmi: float = 0.0

    # 评估内容
    assessments: List[Dict[str, str]] = None  # 评估记录列表

    # 其他
    is_pre_admission: bool = False  # 是否为预住院
    file_path: str = ""  # 源文件路径

    def __post_init__(self):
        if self.stroke_diagnoses is None:
            self.stroke_diagnoses = []
        if self.all_diagnoses is None:
            self.all_diagnoses = []
        if self.assessments is None:
            self.assessments = []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，便于序列化"""
        return {
            "病案号": self.case_id,
            "姓名": self.name,
            "性别": self.gender,
            "年龄": self.age,
            "入院次数": self.admission_number,
            "病程数值": self.duration_value,
            "病程单位": self.duration_unit,
            "病程天数": self.duration_days,
            "体温": self.temperature,
            "脉搏": self.pulse,
            "血压收缩压": self.blood_pressure_systolic,
            "血压舒张压": self.blood_pressure_diastolic,
            "呼吸频率": self.respiratory_rate,
            "Brunnstrom_上肢": self.brunnstrom_arm,
            "Brunnstrom_手": self.brunnstrom_hand,
            "Brunnstrom_下肢": self.brunnstrom_leg,
            "改良Ashworth_上肢": self.ashworth_arm,
            "改良Ashworth_下肢": self.ashworth_leg,
            "ADL评分": self.adl_score,
            "坐位平衡": self.sitting_balance,
            "站位平衡": self.standing_balance,
            "脑卒中诊断": ";".join(self.stroke_diagnoses),
            "所有诊断": ";".join(self.all_diagnoses),
            "身高_cm": self.height_cm,
            "体重_kg": self.weight_kg,
            "BMI": self.bmi,
            "是否为预住院": "是" if self.is_pre_admission else "否",
            "评估记录数": len(self.assessments),
            "评估记录": self.assessments,
            "源文件": self.file_path
        }


class MedicalRecordParser:
    """病案记录解析器"""

    # 脑卒中相关诊断关键词
    STROKE_KEYWORDS = [
        '脑出血', '脑梗塞', '脑梗死', '卒中', '中风',
        '脑血管意外', '脑血栓', '脑栓塞', '蛛网膜下腔出血',
        '脑干出血', '小脑出血', '基底节出血', '丘脑出血',
        '脑室出血', '颅内出血', '缺血性脑卒中', '出血性脑卒中'
    ]

    def __init__(self):
        # 编译常用正则表达式
        self.patterns = {
            # 基本信息 - 修复姓名提取，限制在一行内
            'case_info': re.compile(r'#\s*病案号：(\S+)\s*\|\s*姓名：([^\n]+?)\s*(?:\n|$)'),
            'general_info': re.compile(r'^([^ ,\n]+?)\s*[,，]?\s*(男|女)\s*[,，]?\s*(\d+)岁', re.MULTILINE),
            'pre_admission': re.compile(r'是否为预住院：.*?([是√])'),

            # 病程信息 - 支持 "3月余"、"3月"、"半月" 等格式
            'duration': re.compile(r'([\d.]+|半)\s*([月天年])(?:余|)'),

            # 生命体征 - 支持更多格式变体
            'temperature': re.compile(r'(?:^|[\s,，])(?:T|体温)\s*[:：]?\s*([\d.]+)\s*[℃°C]'),
            'pulse': re.compile(r'(?:^|[\s,，])(?:P|脉搏)\s*[:：]?\s*([\d.]+)\s*次?/分'),
            'blood_pressure': re.compile(r'(?:^|[\s,，])(?:BP|血压)\s*[:：]?\s*([\d.]+)\s*/\s*([\d.]+)\s*(?:mmHg|mmhg)?'),
            'respiratory_rate': re.compile(r'(?:^|[\s,，])(?:R|呼吸)\s*[:：]?\s*([\d.]+)\s*次?/分'),

            # 专科检查 - 支持更多格式变体
            # Brunnstrom - 支持标准格式和特殊格式（包括罗马数字）
            # 标准格式: 上肢X期，手X期，下肢X期
            # 特殊格式: 右上肢X期，X手期，下肢X期 (如黄安海)
            # 特殊格式2: 手 X期（有空格）
            # 特殊格式3: 右上肢X期，右手X期，右下肢X期 (如周胜聪)
            'brunnstrom': re.compile(r'Brunnstrom运动功能分期[:：]?\s*(?:左|右)?(?:侧)?(?:上肢)?\s*[:：]?\s*((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期?[,，\-\s]*(?:左|右)?(?:手)?\s*((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期?[,，\-\s]*(?:左|右)?(?:侧)?(?:下肢)?\s*[:：]?\s*((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期?', re.IGNORECASE),
            'brunnstrom_alt': re.compile(r'Brunnstrom运动功能分期[:：]\s*(?:左|右)?(?:侧)?(?:上肢)?\s*[:：]?\s*((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期[,，\-\s]*((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)手?\s*期[,，\-\s]*(?:下肢)?\s*[:：]?\s*((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期', re.IGNORECASE),
            'brunnstrom_single': re.compile(r'Brunnstrom运动功能分期[:：]\s*(欠配合|NT|TN)', re.IGNORECASE),
            # 特殊格式4: Brunnstrom运动功能分期: 上肢1期-手1期-下肢1期 (如朱冬兰，用横线连接)
            'brunnstrom_dash': re.compile(
                r'Brunnstrom运动功能分期[:：]?\s*'
                r'(?:右|左)?(?:侧)?(?:上肢)?\s*[:：]?\s*'
                r'((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期?'
                r'\s*-\s*(?:手)?\s*'
                r'((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期?'
                r'\s*-\s*(?:下肢)?\s*[:：]?\s*'
                r'((?:\d+|欠配合|NT|TN|I{1,3}|IV|V|VI|[ⅠⅡⅢⅣⅤⅥ])\+?)\s*期?',
                re.IGNORECASE),
            # Ashworth - 支持多种格式变体
            # 标准格式: 改良Ashworth肌痉挛评分：上肢：X级，下肢：X级
            # 变体1: 右上肢：X级，下肢：X级 (翁筱波 - 有"右"前缀，无逗号)
            # 变体2: 右上肢X级，下肢X级 (无冒号)
            'ashworth': re.compile(r'改良ashworth肌痉挛评分[：:]\s*(?:右|左)?上肢[：:]?\s*(\d+\+?\s*级?)[,，]?\s*(?:右|左)?下肢[：:]?\s*(\d+\+?\s*级?)', re.IGNORECASE),
            'ashworth_alt': re.compile(r'改良ashworth肌痉挛评分[：:]\s*(?:右|左)?上肢[:：]?(\d+\+?)\s*级?[,，]?\s*(?:右|左)?下肢[:：]?(\d+\+?)\s*级?', re.IGNORECASE),
            # 变体3: Ashworth肌张力评定（无"改良"前缀）
            'ashworth_simple': re.compile(r'(?:改良)?[Aa]shworth肌张力评定[：:]\s*(?:右|左)?上肢[：:]?\s*(\d+\+?)\s*级?[,，]?\s*(?:右|左)?下肢[：:]?\s*(\d+\+?)\s*级?', re.IGNORECASE),
            'adl': re.compile(r'ADL评定[：:\s]*(\d+)\s*分'),
            'balance': re.compile(r'坐位平衡[：:]\s*(\d+\+?\s*级)[,，]?\s*站位平衡[：:]\s*(\d+\+?\s*级)'),
            # 支持非标准格式：他动态平衡、自动态平衡、静态平衡、NT级
            'balance_nonstandard': re.compile(r'坐位平衡[：:]\s*(他动态平衡|自动态平衡|静态平衡|NT级?)[,，]?\s*站位平衡[：:]\s*(他动态平衡|自动态平衡|静态平衡|NT级?)'),
            # 组合格式：坐站位平衡NT级、坐、站位平衡粗测0级
            'balance_combined': re.compile(r'坐[、]?站位平衡[:：]?\s*(?:粗测)?\s*(NT|TN|欠配合|\d+)\s*级?', re.IGNORECASE),
            # 组合格式分离：坐、站位平衡：坐位X级，站位X级
            'balance_combined_sep': re.compile(r'坐[、]?站位平衡.*?坐位[:：]?(\d+|NT|TN|欠配合).*?站位[:：]?(\d+|NT|TN|欠配合)', re.IGNORECASE),

            # 营养信息
            'height': re.compile(r'身高[：:]\s*([\d.]+)\s*cm'),
            'weight': re.compile(r'体重[：:]\s*([\d.]+)\s*kg'),
            'bmi': re.compile(r'BMI[：:]\s*([\d.]+)'),

            # 评估记录行
            'assessment_line': re.compile(r'^\s*(\d+)\s+(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})\s+([^\s]+)\s+([^\d]+)\s+(\d+)\s+删除'),
        }

    def parse_file(self, file_path: str) -> MedicalRecord:
        """解析单个病案文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        record = MedicalRecord()
        record.file_path = file_path

        # 提取基本信息
        self._extract_basic_info(content, record)

        # 提取病程信息
        self._extract_duration(content, record)

        # 提取体格检查信息
        self._extract_physical_exam(content, record)

        # 提取诊断信息
        self._extract_diagnoses(content, record)

        # 提取营养信息
        self._extract_nutrition(content, record)

        # 提取评估内容
        self._extract_assessments(content, record)

        # 提取预住院信息
        self._extract_pre_admission(content, record)

        return record

    def _extract_basic_info(self, content: str, record: MedicalRecord):
        """提取基本信息"""
        # 病案号和姓名
        match = self.patterns['case_info'].search(content)
        if match:
            record.case_id = match.group(1)
            # 清理姓名，去除可能的Markdown标记和空白
            name = match.group(2).strip()
            name = re.sub(r'[#\s]+$', '', name)  # 去除末尾的#和空白
            # 分离姓名中的"第x次"（如果存在）
            admission_match = re.search(r'(.+?)\s+第(\d+)次', name)
            if admission_match:
                name = admission_match.group(1).strip()
                record.admission_number = admission_match.group(2)
            record.name = name

            # 从文件名提取入院次数
            file_name = Path(record.file_path).stem
            if '_第' in file_name and '次' in file_name:
                adm_match = re.search(r'_第(\d+)次', file_name)
                if adm_match:
                    record.admission_number = adm_match.group(1)

        # 一般情况
        match = self.patterns['general_info'].search(content)
        if match:
            # 姓名已在病例号中提取，这里主要提取性别年龄
            record.gender = match.group(2)
            record.age = int(match.group(3))

    def _extract_duration(self, content: str, record: MedicalRecord):
        """提取病程信息"""
        # 查找简要病史部分
        history_section = self._find_section(content, '简要病史')
        if history_section:
            match = self.patterns['duration'].search(history_section)
            if match:
                value_str = match.group(1)
                record.duration_unit = match.group(2)

                # 处理"半"字
                if value_str == '半':
                    record.duration_value = 0.5
                else:
                    record.duration_value = float(value_str)

                # 转换为天数
                if record.duration_unit == '月':
                    record.duration_days = record.duration_value * 30
                elif record.duration_unit == '年':
                    record.duration_days = record.duration_value * 365
                elif record.duration_unit == '天':
                    record.duration_days = record.duration_value

    def _extract_physical_exam(self, content: str, record: MedicalRecord):
        """提取体格检查信息"""
        # 优先从体格检查章节提取生命体征
        exam_section = self._find_section(content, '体格检查')
        search_content = exam_section if exam_section else content

        # 生命体征
        match = self.patterns['temperature'].search(search_content)
        if match:
            record.temperature = float(match.group(1))

        match = self.patterns['pulse'].search(search_content)
        if match:
            record.pulse = int(float(match.group(1)))

        match = self.patterns['blood_pressure'].search(search_content)
        if match:
            record.blood_pressure_systolic = int(float(match.group(1)))
            record.blood_pressure_diastolic = int(float(match.group(2)))

        match = self.patterns['respiratory_rate'].search(search_content)
        if match:
            record.respiratory_rate = int(float(match.group(1)))

        # 专科检查 - 如果体格检查章节没有，尝试从全文搜索
        # 合并体格检查章节和专科检查章节（如果存在）
        specialty_section = self._find_section(content, '专科检查')
        combined_content = search_content
        if specialty_section:
            combined_content = search_content + '\n' + specialty_section

        match = self.patterns['brunnstrom'].search(combined_content)
        if not match and 'brunnstrom_alt' in self.patterns:
            match = self.patterns['brunnstrom_alt'].search(combined_content)
        if not match and 'brunnstrom_dash' in self.patterns:
            match = self.patterns['brunnstrom_dash'].search(combined_content)
        if match:
            val1 = match.group(1).strip()
            val2 = match.group(2).strip()
            val3 = match.group(3).strip()
            # 处理"欠配合"、"NT"、"TN"等特殊值
            if val1 in ['欠配合', 'NT', 'TN']:
                record.brunnstrom_arm = val1
                record.brunnstrom_hand = val1
                record.brunnstrom_leg = val1
            else:
                record.brunnstrom_arm = val1 + "期" if not val1.endswith('期') else val1
                record.brunnstrom_hand = val2 + "期" if not val2.endswith('期') else val2
                record.brunnstrom_leg = val3 + "期" if not val3.endswith('期') else val3
        # 处理单值情况（如"Brunnstrom: 欠配合"）
        elif 'brunnstrom_single' in self.patterns:
            match_single = self.patterns['brunnstrom_single'].search(combined_content)
            if match_single:
                val = match_single.group(1).strip()
                record.brunnstrom_arm = val
                record.brunnstrom_hand = val
                record.brunnstrom_leg = val

        match = self.patterns['ashworth'].search(combined_content)
        if not match and 'ashworth_alt' in self.patterns:
            match = self.patterns['ashworth_alt'].search(combined_content)
        if not match and 'ashworth_simple' in self.patterns:
            match = self.patterns['ashworth_simple'].search(combined_content)
        if match:
            record.ashworth_arm = match.group(1).strip() + ('级' if not match.group(1).strip().endswith('级') else '')
            record.ashworth_leg = match.group(2).strip() + ('级' if not match.group(2).strip().endswith('级') else '')

        match = self.patterns['adl'].search(combined_content)
        if match:
            record.adl_score = int(match.group(1))

        match = self.patterns['balance'].search(combined_content)
        if match:
            record.sitting_balance = match.group(1).strip()
            record.standing_balance = match.group(2).strip()
        else:
            # 尝试匹配非标准格式
            match = self.patterns['balance_nonstandard'].search(combined_content)
            if match:
                record.sitting_balance = match.group(1).strip()
                record.standing_balance = match.group(2).strip()
            else:
                # 尝试匹配组合格式分离（如"坐、站位平衡：坐位X级，站位X级"）
                if 'balance_combined_sep' in self.patterns:
                    match = self.patterns['balance_combined_sep'].search(combined_content)
                    if match:
                        sit_val = match.group(1).strip()
                        stand_val = match.group(2).strip()
                        record.sitting_balance = sit_val + ('级' if sit_val.isdigit() else '')
                        record.standing_balance = stand_val + ('级' if stand_val.isdigit() else '')
                # 尝试匹配组合格式（如"坐站位平衡NT级"、"坐、站位平衡粗测0级"）
                if not record.sitting_balance and 'balance_combined' in self.patterns:
                    match = self.patterns['balance_combined'].search(combined_content)
                    if match:
                        val = match.group(1).strip()
                        val_with_unit = val + ('级' if val.isdigit() else '')
                        record.sitting_balance = val_with_unit
                        record.standing_balance = val_with_unit

    def _extract_diagnoses(self, content: str, record: MedicalRecord):
        """提取诊断信息"""
        # 查找初步诊断部分
        lines = content.split('\n')
        in_diagnosis_section = False

        for i, line in enumerate(lines):
            if '三.初步诊断' in line or '三、初步诊断' in line:
                in_diagnosis_section = True
                continue

            if in_diagnosis_section:
                # 诊断部分结束条件：下一个章节、评估内容、空行后的标记等
                stripped = line.strip()
                if (stripped.startswith('四.') or stripped.startswith('四、') or
                    stripped.startswith('##') or
                    stripped.startswith('评估内容') or
                    stripped.startswith('未获取到评估内容') or
                    self.patterns['assessment_line'].match(stripped)):
                    break

                # 提取诊断行（非空行且不是标题，且不是评估记录）
                if stripped and not stripped.startswith('#') and not stripped.startswith('未获取到'):
                    # 跳过看起来像评估记录的行（包含日期时间格式）
                    if re.search(r'\d{4}/\d{1,2}/\d{1,2}', stripped) and '删除' in stripped:
                        continue
                    # 跳过纯数字开头且有"删除"字样的行
                    if re.match(r'^\s*\d+\s+\d{4}/', stripped):
                        continue
                    # 跳过评估记录的行
                    if '删除' in stripped and (re.search(r'\d{4}/\d{1,2}/\d{1,2}', stripped) or
                                               re.match(r'^\s*\d+\s+', stripped)):
                        continue

                    diagnosis = stripped
                    record.all_diagnoses.append(diagnosis)

                    # 检查是否为脑卒中相关诊断
                    if self._is_stroke_diagnosis(diagnosis):
                        record.stroke_diagnoses.append(diagnosis)

    def _extract_nutrition(self, content: str, record: MedicalRecord):
        """提取营养信息"""
        nutrition_section = self._find_section(content, '营养内容')
        if not nutrition_section or '未获取到' in nutrition_section:
            return

        match = self.patterns['height'].search(nutrition_section)
        if match:
            record.height_cm = float(match.group(1))

        match = self.patterns['weight'].search(nutrition_section)
        if match:
            record.weight_kg = float(match.group(1))

        match = self.patterns['bmi'].search(nutrition_section)
        if match:
            record.bmi = float(match.group(1))

    def _extract_assessments(self, content: str, record: MedicalRecord):
        """提取评估内容"""
        assessment_section = self._find_section(content, '评估内容')
        if not assessment_section or '未获取到' in assessment_section:
            return

        lines = assessment_section.split('\n')
        for line in lines:
            match = self.patterns['assessment_line'].match(line.strip())
            if match:
                assessment = {
                    '序号': match.group(1),
                    '时间': match.group(2),
                    '评估者': match.group(3),
                    '评估项目': match.group(4).strip(),
                    '分数': f"{match.group(5)} 分",
                    '原始行': line.strip()
                }
                record.assessments.append(assessment)

    def _extract_pre_admission(self, content: str, record: MedicalRecord):
        """提取预住院信息"""
        match = self.patterns['pre_admission'].search(content)
        if match:
            record.is_pre_admission = True

    def _find_section(self, content: str, section_name: str) -> Optional[str]:
        """查找指定章节内容"""
        lines = content.split('\n')
        in_section = False
        section_lines = []

        for line in lines:
            if f'## {section_name}' in line or f'{section_name}' in line:
                in_section = True
                continue

            if in_section:
                # 如果遇到下一个章节标题，结束
                if line.strip().startswith('##'):
                    break

                section_lines.append(line)

        return '\n'.join(section_lines) if section_lines else None

    def _is_stroke_diagnosis(self, diagnosis: str) -> bool:
        """判断是否为脑卒中相关诊断"""
        diagnosis_lower = diagnosis.lower()
        for keyword in self.STROKE_KEYWORDS:
            if keyword in diagnosis:
                return True
        return False


def process_directory(directory_path: str, output_csv: str = None, output_json: str = None) -> List[MedicalRecord]:
    """处理目录下的所有病案文件"""
    parser = MedicalRecordParser()
    records = []

    directory = Path(directory_path)
    if not directory.exists():
        print(f"目录不存在: {directory_path}")
        return records

    # 查找所有.md文件
    md_files = list(directory.glob("*.md"))
    print(f"找到 {len(md_files)} 个病案文件")

    for i, md_file in enumerate(md_files, 1):
        print(f"处理文件 {i}/{len(md_files)}: {md_file.name}")
        try:
            record = parser.parse_file(str(md_file))
            records.append(record)
        except Exception as e:
            print(f"  处理失败: {e}")

    # 保存结果
    if output_csv:
        _save_to_csv(records, output_csv)

    if output_json:
        _save_to_json(records, output_json)

    return records


def _save_to_csv(records: List[MedicalRecord], output_path: str):
    """保存为CSV文件"""
    if not records:
        print("没有数据可保存")
        return

    # 准备数据行
    data_rows = []
    for record in records:
        record_dict = record.to_dict()

        # 处理评估记录（保存为JSON字符串）
        assessments = record_dict.pop('评估记录')
        record_dict['评估记录'] = json.dumps(assessments, ensure_ascii=False)

        data_rows.append(record_dict)

    # 获取所有字段
    fieldnames = list(data_rows[0].keys())

    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_rows)

    print(f"CSV文件已保存: {output_path}")


def _save_to_json(records: List[MedicalRecord], output_path: str):
    """保存为JSON文件"""
    data = [record.to_dict() for record in records]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"JSON文件已保存: {output_path}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='从病案Markdown文件中提取结构化数据')

    # 互斥参数：要么处理目录，要么处理单个文件
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dir', help='包含病案文件的目录路径')
    group.add_argument('--single', help='处理单个文件')

    parser.add_argument('--csv', help='输出CSV文件路径')
    parser.add_argument('--json', help='输出JSON文件路径')

    args = parser.parse_args()

    if args.single:
        # 处理单个文件
        parser_obj = MedicalRecordParser()
        record = parser_obj.parse_file(args.single)

        # 打印结果
        print("\n" + "="*60)
        print("提取结果:")
        print("="*60)
        for key, value in record.to_dict().items():
            if key != '评估记录':
                print(f"{key}: {value}")

        # 打印评估记录
        if record.assessments:
            print("\n评估记录:")
            for assessment in record.assessments:
                print(f"  {assessment['时间']} {assessment['评估者']} {assessment['评估项目']} {assessment['分数']}")

        # 保存结果
        if args.csv:
            _save_to_csv([record], args.csv)
        if args.json:
            _save_to_json([record], args.json)
    elif args.dir:
        # 处理目录
        process_directory(args.dir, args.csv, args.json)
    else:
        print("请指定 --dir 或 --single 参数")
        parser.print_help()


if __name__ == '__main__':
    main()