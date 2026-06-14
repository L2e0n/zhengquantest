#!/usr/bin/env python3
"""
证券考试题库PDF解析工具 v2
修正多选题答案和选项解析逻辑
"""

import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """提取PDF全文"""
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_questions(text: str, section: str, chapter: str, year: int, source: str) -> List[Dict]:
    """解析题目文本"""
    questions = []

    # 分割题目（按题号分割）
    pattern = r'\n(\d+)[.．]\s*'
    parts = re.split(pattern, text)

    # parts[0]是标题等前置内容，从parts[1]开始是题号和题目交替出现
    i = 1
    while i < len(parts) - 1:
        question_num = parts[i]
        question_text = parts[i + 1]

        try:
            q = parse_single_question(question_text, section, chapter, year, source)
            if q:
                questions.append(q)
        except Exception as e:
            print(f"  解析题目 {question_num} 失败: {e}")

        i += 2

    return questions


def detect_question_type(text: str) -> Optional[str]:
    """检测题型"""
    # 多选题特征：包含①②③④的选项
    if re.search(r'[①②③④⑤]', text):
        return 'multiple'

    # 单选题特征：A. B. C. D.
    if re.search(r'[A-D][.．]\s*\S+', text):
        return 'single'

    return None


def extract_stem(text: str) -> str:
    """提取题干"""
    # 题干从开头到第一个选项之前
    match = re.search(r'^(.*?)(?=\n[A-D①][.．]|[A-D①][.．])', text, re.DOTALL)
    if match:
        stem = match.group(1).strip()
        # 清理
        stem = re.sub(r'\s+', ' ', stem)
        return stem
    return ""


def extract_options_and_mapping(text: str, question_type: str) -> tuple:
    """
    提取选项，返回 (options, content_mapping)

    对于多选题，content_mapping 存储 ① -> "内容" 的映射
    对于单选题，content_mapping 为空
    """
    options = []
    content_mapping = {}

    if question_type == 'single':
        # 单选题：A. B. C. D.
        pattern = r'([A-D])[.．]\s*(.*?)(?=\n[A-D][.．]|\n参考答案|参考答案|【慧考解析】|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        for key, text_content in matches:
            clean_text = text_content.strip().replace('\n', ' ')
            # 移除末尾可能的数字
            clean_text = re.sub(r'\s+\d+\s*$', '', clean_text)
            if clean_text:
                options.append({
                    "key": key,
                    "text": clean_text
                })

    else:  # multiple
        # 多选题分两步：
        # 1. 先提取①②③④的内容
        content_pattern = r'([①②③④⑤])(.*?)(?=\n[①②③④⑤]|\n[A-D][.．]|[A-D][.．])'
        content_matches = re.findall(content_pattern, text, re.DOTALL)

        for num, content in content_matches:
            clean_content = content.strip().replace('\n', ' ')
            # 移除末尾数字
            clean_content = re.sub(r'\s+\d+\s*$', '', clean_content)
            content_mapping[num] = clean_content

        # 2. 再提取A/B/C/D选项（每个选项包含的①②③④组合）
        option_pattern = r'([A-D])[.．]\s*([①②③④⑤\s]+?)(?=\n[A-D][.．]|\n参考答案|参考答案|【慧考解析】|$)'
        option_matches = re.findall(option_pattern, text, re.DOTALL)

        for key, nums in option_matches:
            # 提取这个选项包含的所有①②③④
            included_nums = re.findall(r'[①②③④⑤]', nums)
            # 组合成选项文本
            texts = [content_mapping.get(n, '') for n in included_nums if n in content_mapping]
            if texts:
                combined_text = '；'.join(texts)
                options.append({
                    "key": key,
                    "text": combined_text,
                    "nums": included_nums  # 保存编号用于答案匹配
                })

    return options[:4], content_mapping  # 最多4个选项


def extract_answer(text: str, question_type: str, options: List[Dict]) -> List[str]:
    """提取答案"""
    # 查找 "参考答案：" 后面的内容
    match = re.search(r'参考答案[：:]\s*([A-D][.．]?[①②③④⑤\s,，]*|[A-D\s,，]+)', text)
    if not match:
        return []

    answer_text = match.group(1).strip()

    if question_type == 'multiple':
        # 多选题可能的格式：
        # 1. "D.①②③④" - 单个答案
        # 2. "D" - 单个字母
        # 3. "A, B, D" - 多个字母

        # 先提取字母
        answer_letters = re.findall(r'[A-D]', answer_text)

        # 如果答案是 "D.①②③④" 格式，只有一个字母，那就是选D
        if len(answer_letters) == 1 and re.search(r'[A-D][.．][①②③④⑤]+', answer_text):
            return answer_letters

        # 如果有多个字母（如 A, B, D），返回所有字母
        if len(answer_letters) > 1:
            return answer_letters

        # 只有一个字母
        return answer_letters[:1] if answer_letters else []

    else:  # single
        letters = re.findall(r'[A-D]', answer_text)
        return letters[:1]


def extract_explanation(text: str) -> str:
    """提取解析"""
    match = re.search(r'【慧考解析】\s*(.*?)(?=\n\d+[.．]|$)', text, re.DOTALL)
    if match:
        explanation = match.group(1).strip()
        explanation = re.sub(r'\s+', ' ', explanation)
        explanation = re.sub(r'^考点[：:]\s*', '', explanation)
        # 清除慧考智学广告
        explanation = re.sub(r'专业网校课程.*?版权所有\s*\d*', '', explanation)
        return explanation
    return ""


def parse_single_question(text: str, section: str, chapter: str, year: int, source: str) -> Optional[Dict]:
    """解析单个题目"""

    question_type = detect_question_type(text)
    if not question_type:
        return None

    stem = extract_stem(text)
    if not stem:
        return None

    options, content_mapping = extract_options_and_mapping(text, question_type)
    if not options:
        return None

    answer = extract_answer(text, question_type, options)
    if not answer:
        return None

    explanation = extract_explanation(text)

    # 生成内容hash
    content = f"{stem}{''.join([o['text'] for o in options])}"
    content_hash = hashlib.md5(content.encode()).hexdigest()

    # 清理options，移除临时字段
    clean_options = []
    for opt in options:
        clean_options.append({
            "key": opt["key"],
            "text": opt["text"]
        })

    return {
        "section": section,
        "chapter": chapter,
        "type": question_type,
        "stem": stem,
        "options": clean_options,
        "answer": answer,
        "explanation": explanation,
        "difficulty": "medium",
        "year": year,
        "source": source,
        "tags": [],
        "contentHash": content_hash
    }


def extract_metadata_from_path(pdf_path: Path) -> tuple:
    """从文件路径提取元数据"""
    path_str = str(pdf_path)

    # 判断科目
    if '金融市场基础知识' in path_str:
        section = 'finance_basic'
    elif '证券市场基本法律法规' in path_str:
        section = 'securities_law'
    else:
        section = 'finance_basic'  # 默认

    # 提取年份
    year_match = re.search(r'20\d{2}', path_str)
    year = int(year_match.group()) if year_match else 2024

    # 提取章节
    chapter_match = re.search(r'第[一二三四五六七八]章', path_str)
    if chapter_match:
        chapter = chapter_match.group()
    elif '考前点题' in path_str:
        chapter = '考前点题'
    elif '真题' in path_str:
        chapter = f'{year}年真题'
    else:
        chapter = ''

    return section, chapter, year


def process_directory(base_dir: str, output_file: str):
    """处理整个目录"""
    base_path = Path(base_dir)
    all_questions = []

    pdf_files = list(base_path.rglob("*.pdf"))
    print(f"找到 {len(pdf_files)} 个PDF文件\n")

    for pdf_file in pdf_files:
        print(f"处理: {pdf_file.relative_to(base_path)}")

        try:
            section, chapter, year = extract_metadata_from_path(pdf_file)
            source = pdf_file.stem

            text = extract_text_from_pdf(str(pdf_file))
            questions = parse_questions(text, section, chapter, year, source)

            print(f"  提取 {len(questions)} 道题目")
            all_questions.extend(questions)

        except Exception as e:
            print(f"  错误: {e}")

    print(f"\n总计提取 {len(all_questions)} 道题目")

    # 去重
    seen_hashes = set()
    unique_questions = []
    for q in all_questions:
        if q['contentHash'] not in seen_hashes:
            seen_hashes.add(q['contentHash'])
            unique_questions.append(q)

    print(f"去重后剩余 {len(unique_questions)} 道题目")

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_questions, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 保存到 {output_file}")


if __name__ == '__main__':
    base_dir = '/Users/zhh/Downloads/2.送文档题库'
    output_file = 'parsed_questions_v2.json'

    process_directory(base_dir, output_file)
