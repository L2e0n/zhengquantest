#!/usr/bin/env python3
"""
证券考试题库PDF解析工具
从PDF中提取题目、选项、答案、解析，转换为系统JSON格式
"""

import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import pymupdf  # PyMuPDF


def extract_text_from_pdf(pdf_path: str) -> str:
    """提取PDF全文"""
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_questions(text: str, section: str, chapter: str, source: str) -> List[Dict]:
    """解析题目文本"""
    questions = []

    # 分割题目（按题号分割）
    # 匹配格式：1. 题干内容 或 1.题干内容
    pattern = r'\n(\d+)[.．]\s*'
    parts = re.split(pattern, text)

    # parts[0]是标题等前置内容，从parts[1]开始是题号和题目交替出现
    i = 1
    while i < len(parts) - 1:
        question_num = parts[i]
        question_text = parts[i + 1]

        try:
            q = parse_single_question(question_text, section, chapter, source)
            if q:
                questions.append(q)
        except Exception as e:
            print(f"解析题目 {question_num} 失败: {e}")

        i += 2

    return questions


def parse_single_question(text: str, section: str, chapter: str, source: str) -> Optional[Dict]:
    """解析单个题目"""

    # 判断题型
    question_type = detect_question_type(text)
    if not question_type:
        return None

    # 提取题干
    stem = extract_stem(text)
    if not stem:
        return None

    # 提取选项
    options = extract_options(text, question_type)
    if not options:
        return None

    # 提取答案
    answer = extract_answer(text, question_type)
    if not answer:
        return None

    # 提取解析
    explanation = extract_explanation(text)

    # 生成内容hash用于去重
    content = f"{stem}{''.join([o['text'] for o in options])}"
    content_hash = hashlib.md5(content.encode()).hexdigest()

    return {
        "section": section,
        "chapter": chapter,
        "type": question_type,
        "stem": stem.strip(),
        "options": options,
        "answer": answer,
        "explanation": explanation.strip() if explanation else "",
        "source": source,
        "tags": [],
        "contentHash": content_hash
    }


def detect_question_type(text: str) -> Optional[str]:
    """检测题型"""
    # 单选题特征：A. B. C. D.
    if re.search(r'[A-D][.．]\s*\S+', text):
        # 多选题答案格式：A.①②③ 或包含"以下"/"下列"等多选关键词
        if re.search(r'[A-D][.．]\s*[①②③④]{2,}', text):
            return "multiple"
        return "single"

    # 判断题特征（较少见）
    if re.search(r'[对错正误]', text) and len(re.findall(r'[A-D][.．]', text)) <= 2:
        return "true_false"

    return "single"  # 默认单选


def extract_stem(text: str) -> str:
    """提取题干"""
    # 题干在第一个选项之前
    match = re.search(r'^(.*?)(?=[A-D①][.．]|\n[①②③④])', text, re.DOTALL)
    if match:
        stem = match.group(1).strip()
        # 清理题干
        stem = re.sub(r'\s+', ' ', stem)
        stem = re.sub(r'^\d+[.．]\s*', '', stem)  # 移除题号
        return stem
    return ""


def extract_options(text: str, question_type: str) -> List[Dict]:
    """提取选项"""
    options = []

    if question_type in ["single", "true_false"]:
        # 单选/判断题：A. B. C. D.
        # 从题干之后到参考答案之前提取
        pattern = r'([A-D])[.．]\s*(.*?)(?=\n[A-D][.．]|\n参考答案|参考答案|【慧考解析】)'
        matches = re.findall(pattern, text, re.DOTALL)
        for key, text_content in matches:
            clean_text = text_content.strip().replace('\n', ' ')
            # 移除选项文本中可能包含的下一个选项标记
            clean_text = re.sub(r'\s+[A-D][.．].*$', '', clean_text)
            if clean_text:
                options.append({
                    "key": key,
                    "text": clean_text
                })
    else:
        # 多选题：①②③④
        pattern = r'([①②③④])(.*?)(?=\n[①②③④]|\n[A-D][.．]|[A-D][.．]|参考答案|【慧考解析】)'
        matches = re.findall(pattern, text, re.DOTALL)
        for num, text_content in matches:
            clean_text = text_content.strip().replace('\n', ' ')
            # 移除可能包含的选项标记
            clean_text = re.sub(r'\s+[①②③④].*$', '', clean_text)
            if clean_text:
                # 转换为字母 A/B/C/D
                key_map = {'①': 'A', '②': 'B', '③': 'C', '④': 'D'}
                options.append({
                    "key": key_map.get(num, num),
                    "text": clean_text
                })

    return options[:4]  # 最多4个选项


def extract_answer(text: str, question_type: str) -> List[str]:
    """提取答案"""
    # 查找 "参考答案：" 后面的内容
    match = re.search(r'参考答案[：:]\s*([A-D①②③④\s,，]+)', text)
    if not match:
        return []

    answer_text = match.group(1).strip()

    if question_type == "multiple":
        # 多选题：提取所有字母
        # 如果是 A.①②③ 格式，先查找A之前是否有[.．]
        if re.search(r'[A-D][.．]', answer_text):
            # 提取 A.①②③ 中的字母序列（可能是单个，也可能多个如 A、B、D）
            letters = re.findall(r'[A-D](?=[.．])', answer_text)
        else:
            # 直接是字母 A, B, C 或 ABC
            letters = re.findall(r'[A-D]', answer_text)
        return letters
    else:
        # 单选/判断题
        letters = re.findall(r'[A-D]', answer_text)
        return letters[:1]  # 单选只取第一个


def extract_explanation(text: str) -> str:
    """提取解析"""
    # 查找【慧考解析】后面的内容
    match = re.search(r'【慧考解析】\s*(.*?)(?=\n\d+[.．]|$)', text, re.DOTALL)
    if match:
        explanation = match.group(1).strip()
        # 清理
        explanation = re.sub(r'\s+', ' ', explanation)
        explanation = re.sub(r'^考点[：:]\s*', '', explanation)
        return explanation
    return ""


def process_directory(base_dir: str, output_file: str):
    """处理整个目录"""
    base_path = Path(base_dir)
    all_questions = []

    # 遍历所有PDF文件
    pdf_files = list(base_path.rglob("*.pdf"))
    print(f"找到 {len(pdf_files)} 个PDF文件")

    for pdf_file in pdf_files:
        print(f"\n处理: {pdf_file.relative_to(base_path)}")

        try:
            # 提取文本
            text = extract_text_from_pdf(str(pdf_file))

            # 从路径提取章节信息
            parts = pdf_file.relative_to(base_path).parts

            # 判断科目（更智能地检测）
            section = "finance_basic"  # 默认金融基础知识
            file_content_lower = str(pdf_file).lower()
            if any(keyword in file_content_lower for keyword in ["法律法规", "证券法律", "法规"]):
                section = "securities_law"

            # 也从PDF内容中检测
            text_snippet = text[:500] if text else ""
            if "法律法规" in text_snippet or "证券市场基本法律法规" in text_snippet:
                section = "securities_law"

            # 提取章节
            chapter = ""
            if len(parts) > 1 and parts[0] == "1.章节练习":
                # 提取完整章节路径，如 "第一章 金融市场体系/第一节 金融市场概述"
                if len(parts) > 2:
                    chapter = f"{parts[1]}/{parts[2].replace('.pdf', '')}"
                elif len(parts) > 1:
                    chapter = parts[1]
            elif parts[0] == "2.考前点题":
                chapter = "考前点题"
            elif parts[0] == "3.历年真题":
                # 从文件名提取年份和月份
                year_match = re.search(r'(\d{4})年(\d+)?月?', pdf_file.name)
                if year_match:
                    year = year_match.group(1)
                    month = year_match.group(2) if year_match.group(2) else ""
                    chapter = f"{year}年{month + '月' if month else ''}真题"
                else:
                    chapter = "历年真题"

            # 解析题目
            questions = parse_questions(text, section, chapter, pdf_file.name)

            print(f"  解析出 {len(questions)} 道题目")
            all_questions.extend(questions)

        except Exception as e:
            print(f"  错误: {e}")
            continue

    # 保存JSON
    print(f"\n总计 {len(all_questions)} 道题目")
    print(f"保存到: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)

    print("完成！")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python parse_pdf_questions.py <题库目录> [输出文件]")
        print("示例: python parse_pdf_questions.py '/Users/zhh/Downloads/2.送文档题库' questions.json")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "questions.json"

    process_directory(input_dir, output_file)
