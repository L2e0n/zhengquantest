#!/usr/bin/env python3
"""
证券考试题库PDF解析工具 v5
正确识别单选题和多选题：根据参考答案中字母数量判断
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


def clean_text(text: str) -> str:
    """清理文本"""
    # 移除末尾数字
    text = re.sub(r'\s+\d+\s*$', '', text)
    # 移除广告
    text = re.sub(r'专业网校课程.*?版权所有\s*\d*', '', text)
    return text.strip()


def extract_stem(text: str) -> str:
    """提取题干（从开头到第一个选项A.之前）"""
    match = re.search(r'^(.*?)(?=\n?[A][.．])', text, re.DOTALL)
    if match:
        stem = match.group(1).strip()
        stem = re.sub(r'\s+', ' ', stem)
        # 清理广告
        stem = re.sub(r'专业网校课程.*?版权所有\s*\d*', '', stem)
        stem = stem.strip()
        return stem
    return ""


def extract_options(text: str) -> List[Dict]:
    """提取选项 A. B. C. D."""
    options = []
    pattern = r'([A-D])[.．]\s*(.*?)(?=\n[A-D][.．]|\n?参考答案|【慧考解析】|$)'
    matches = re.findall(pattern, text, re.DOTALL)

    for key, content in matches:
        clean_content = content.strip().replace('\n', ' ')
        clean_content = clean_text(clean_content)
        if clean_content:
            options.append({"key": key, "text": clean_content})

    return options[:4]


def extract_answer(text: str) -> List[str]:
    """提取答案（一个或多个字母）"""
    match = re.search(r'参考答案[：:]\s*([A-D]+)', text)
    if not match:
        return []

    answer_text = match.group(1).strip()
    letters = list(answer_text)  # "AB" -> ['A', 'B']

    return letters


def extract_explanation(text: str) -> str:
    """提取解析"""
    match = re.search(r'【慧考解析】\s*(.*?)(?=\n\d+[.．]|$)', text, re.DOTALL)
    if match:
        explanation = match.group(1).strip()
        explanation = re.sub(r'\s+', ' ', explanation)
        explanation = re.sub(r'^考点[：:]\s*', '', explanation)
        explanation = clean_text(explanation)
        return explanation
    return ""


def parse_single_question(text: str, section: str, chapter: str, year: int, source: str) -> Optional[Dict]:
    """解析单个题目"""
    stem = extract_stem(text)
    if not stem:
        return None

    options = extract_options(text)
    if not options:
        return None

    answer = extract_answer(text)
    if not answer:
        return None

    # 根据答案数量判断题型
    question_type = 'multiple' if len(answer) > 1 else 'single'

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

    # 提取章节信息
    chapter_match = re.search(r'第[一二三四五六七八]章[^/]*', path_str)
    section_match = re.search(r'第[一二三四五六七八九十]+节[^/\.]*', path_str)

    if chapter_match and section_match:
        # 章节练习：第X章/第X节 格式
        chapter = f"{chapter_match.group()}/{section_match.group()}"
    elif chapter_match:
        # 只有章，没有节
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

    # 统计
    single_count = sum(1 for q in unique_questions if q['type'] == 'single')
    multi_count = sum(1 for q in unique_questions if q['type'] == 'multiple')
    print(f"\n单选题: {single_count} 道")
    print(f"多选题: {multi_count} 道")

    # 多选题答案统计
    multi_ans_dist = {}
    for q in unique_questions:
        if q['type'] == 'multiple':
            ans_len = len(q['answer'])
            multi_ans_dist[ans_len] = multi_ans_dist.get(ans_len, 0) + 1

    if multi_ans_dist:
        print("\n多选题答案数量分布:")
        for length in sorted(multi_ans_dist.keys()):
            print(f"  {length} 个答案: {multi_ans_dist[length]} 道")

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_questions, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 保存到 {output_file}")


if __name__ == '__main__':
    base_dir = '/Users/zhh/Downloads/2.送文档题库'
    output_file = 'parsed_questions_v5.json'

    process_directory(base_dir, output_file)
