#!/usr/bin/env python3
"""
证券考试题库PDF解析工具 v3
正确处理多选题：①②③④作为选项，从答案组合反推选中的选项
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


def detect_question_type(text: str) -> Optional[str]:
    """检测题型"""
    if re.search(r'[①②③④⑤]', text):
        return 'multiple'
    if re.search(r'[A-D][.．]\s*\S+', text):
        return 'single'
    return None


def extract_stem(text: str) -> str:
    """提取题干（不包含选项）"""
    # 题干从开头到第一个①或A.之前
    match = re.search(r'^(.*?)(?=\n?[①A][.．])', text, re.DOTALL)
    if match:
        stem = match.group(1).strip()
        stem = re.sub(r'\s+', ' ', stem)
        return stem
    return ""


def extract_options(text: str, question_type: str) -> List[Dict]:
    """提取选项"""
    options = []

    if question_type == 'single':
        # 单选题：A. B. C. D.
        pattern = r'([A-D])[.．]\s*(.*?)(?=\n[A-D][.．]|\n?参考答案|【慧考解析】|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        for key, text_content in matches:
            clean_text = text_content.strip().replace('\n', ' ')
            clean_text = re.sub(r'\s+\d+\s*$', '', clean_text)  # 移除末尾数字
            # 移除广告
            clean_text = re.sub(r'专业网校课程.*?版权所有\s*\d*', '', clean_text)
            if clean_text:
                options.append({"key": key, "text": clean_text})

    else:  # multiple
        # 多选题：提取 ①②③④⑤ 作为选项 A/B/C/D/E
        pattern = r'([①②③④⑤])(.*?)(?=\n?[①②③④⑤A][.．]|\n?参考答案|【慧考解析】|$)'
        matches = re.findall(pattern, text, re.DOTALL)

        # 映射 ①②③④⑤ 到 A/B/C/D/E
        num_to_key = {'①': 'A', '②': 'B', '③': 'C', '④': 'D', '⑤': 'E'}

        for num, content in matches:
            clean_text = content.strip().replace('\n', ' ')
            clean_text = re.sub(r'\s+\d+\s*$', '', clean_text)
            # 移除广告
            clean_text = re.sub(r'专业网校课程.*?版权所有\s*\d*', '', clean_text)
            if clean_text:
                options.append({
                    "key": num_to_key.get(num, num),
                    "text": clean_text
                })

    return options[:5]


def extract_answer(text: str, question_type: str) -> List[str]:
    """提取答案"""
    # 改进的匹配：提取所有相关字符
    match = re.search(r'参考答案[：:]\s*([A-E①②③④⑤.．\s,，]+?)(?=\n|【)', text)
    if not match:
        return []

    answer_text = match.group(1).strip()

    if question_type == 'single':
        letters = re.findall(r'[A-D]', answer_text)
        return letters[:1]

    # 多选题
    # 提取所有字母和编号
    letters = re.findall(r'[A-E]', answer_text)
    nums = re.findall(r'[①②③④⑤]', answer_text)

    if nums:
        # 编号格式：D.①②③④ -> 转换编号为字母
        num_to_key = {'①': 'A', '②': 'B', '③': 'C', '④': 'D', '⑤': 'E'}
        result = [num_to_key[n] for n in nums if n in num_to_key]
        return result
    elif len(letters) >= 1:
        # 标准格式：ABC 或 A,B,C
        return letters
    else:
        return []


def extract_explanation(text: str) -> str:
    """提取解析"""
    match = re.search(r'【慧考解析】\s*(.*?)(?=\n\d+[.．]|$)', text, re.DOTALL)
    if match:
        explanation = match.group(1).strip()
        explanation = re.sub(r'\s+', ' ', explanation)
        explanation = re.sub(r'^考点[：:]\s*', '', explanation)
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

    options = extract_options(text, question_type)
    if not options:
        return None

    answer = extract_answer(text, question_type)
    if not answer:
        return None

    explanation = extract_explanation(text)

    content = f"{stem}{''.join([o['text'] for o in options])}"
    content_hash = hashlib.md5(content.encode()).hexdigest()

    return {
        "section": section,
        "chapter": chapter,
        "type": question_type,
        "stem": stem,
        "options": options,
        "answer": answer,
        "explanation": explanation,
        "difficulty": "medium",
        "year": year,
        "source": source,
        "tags": [],
        "contentHash": content_hash
    }


def parse_questions(text: str, section: str, chapter: str, year: int, source: str) -> List[Dict]:
    """解析题目文本"""
    questions = []
    pattern = r'\n(\d+)[.．]\s*'
    parts = re.split(pattern, text)

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


def extract_metadata_from_path(pdf_path: Path) -> tuple:
    """从文件路径提取元数据"""
    path_str = str(pdf_path)

    if '金融市场基础知识' in path_str:
        section = 'finance_basic'
    elif '证券市场基本法律法规' in path_str:
        section = 'securities_law'
    else:
        section = 'finance_basic'

    year_match = re.search(r'20\d{2}', path_str)
    year = int(year_match.group()) if year_match else 2024

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
    output_file = 'parsed_questions_v3.json'

    process_directory(base_dir, output_file)
