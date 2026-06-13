#!/usr/bin/env python3
"""
证券考试题库PDF解析工具 v4
完整支持三种多选题格式：
1. 标准格式：A.文本 B.文本，答案ABC
2. 圆圈编号：题干含①②③④，选项A.①③，答案D.①②③④
3. 罗马数字：题干含ⅠⅡⅢⅣ，选项A.ⅠⅡ，答案需转换
"""

import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
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
    if re.search(r'[①②③④⑤ⅠⅢⅣⅤ]', text):
        return 'multiple'
    if re.search(r'[A-D][.．]\s*\S+', text):
        return 'single'
    return None


def clean_option_text(text: str) -> str:
    """清理选项文本"""
    # 移除末尾数字
    text = re.sub(r'\s+\d+\s*$', '', text)
    # 移除广告
    text = re.sub(r'专业网校课程.*?版权所有\s*\d*', '', text)
    # 移除"故本题选X"等解析内容
    text = re.sub(r'[。；]?\s*故本题选[A-D].*$', '', text)
    text = re.sub(r'[。；]?\s*[ⅠⅡⅢⅣ①②③④⑤、]+项?正确.*$', '', text)
    # 移除参考答案
    text = re.sub(r'参考答案.*$', '', text)
    return text.strip()


def extract_stem(text: str) -> str:
    """提取题干"""
    # 题干从开头到第一个选项标记之前
    match = re.search(r'^(.*?)(?=\n?[①ⅠAⅡ][.．])', text, re.DOTALL)
    if match:
        stem = match.group(1).strip()
        stem = re.sub(r'\s+', ' ', stem)
        return stem
    return ""


def detect_multi_choice_format(text: str) -> str:
    """
    检测多选题格式
    返回: 'standard' / 'circle' / 'roman'
    """
    # 检查题干中是否包含编号
    if re.search(r'[①②③④⑤]', text):
        return 'circle'  # 圆圈编号格式
    elif re.search(r'[ⅠⅡⅢⅣⅤ]', text):
        return 'roman'   # 罗马数字格式
    else:
        return 'standard' # 标准格式


def extract_options(text: str, question_type: str) -> Tuple[List[Dict], str]:
    """
    提取选项
    返回: (options列表, 多选题格式)
    """
    options = []
    multi_format = 'standard'

    if question_type == 'single':
        # 单选题
        pattern = r'([A-D])[.．]\s*(.*?)(?=\n[A-D][.．]|\n?参考答案|【慧考解析】|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        for key, content in matches:
            clean_text = clean_option_text(content.replace('\n', ' '))
            if clean_text:
                options.append({"key": key, "text": clean_text})

    else:  # multiple
        multi_format = detect_multi_choice_format(text)

        if multi_format == 'standard':
            # 标准格式：A.文本 B.文本
            pattern = r'([A-D])[.．]\s*(.*?)(?=\n[A-D][.．]|\n?参考答案|【慧考解析】|$)'
            matches = re.findall(pattern, text, re.DOTALL)
            for key, content in matches:
                clean_text = clean_option_text(content.replace('\n', ' '))
                if clean_text:
                    options.append({"key": key, "text": clean_text})

        elif multi_format == 'circle':
            # 圆圈编号格式：①内容 ②内容，然后 A.①③
            # 先找到第一个A.的位置，之前的是内容定义
            a_match = re.search(r'\n[A][.．]', text)
            if a_match:
                content_section = text[:a_match.start()]

                # 在内容区提取编号
                content_map = {}
                content_pattern = r'([①②③④⑤])(.*?)(?=\n?[①②③④⑤]|\n?[A][.．]|$)'
                content_matches = re.findall(content_pattern, content_section, re.DOTALL)

                for num, content in content_matches:
                    clean_text = clean_option_text(content.replace('\n', ' '))
                    content_map[num] = clean_text

                # 提取选项（使用编号内容）
                num_to_key = {'①': 'A', '②': 'B', '③': 'C', '④': 'D', '⑤': 'E'}
                for num in ['①', '②', '③', '④', '⑤']:
                    if num in content_map and content_map[num]:
                        options.append({
                            "key": num_to_key[num],
                            "text": content_map[num]
                        })

        elif multi_format == 'roman':
            # 罗马数字格式：Ⅰ.内容 Ⅱ.内容，然后 A.ⅠⅡ
            # 先找到第一个A.的位置
            a_match = re.search(r'\n[A][.．]', text)
            if a_match:
                content_section = text[:a_match.start()]

                # 在内容区提取罗马数字
                content_map = {}
                content_pattern = r'([ⅠⅡⅢⅣⅤ])[.．。、]?\s*(.*?)(?=\n?[ⅠⅡⅢⅣⅤ][.．。、]|\n?[A][.．]|$)'
                content_matches = re.findall(content_pattern, content_section, re.DOTALL)

                for num, content in content_matches:
                    clean_text = clean_option_text(content.replace('\n', ' '))
                    if clean_text:
                        content_map[num] = clean_text

                # 提取选项
                num_to_key = {'Ⅰ': 'A', 'Ⅱ': 'B', 'Ⅲ': 'C', 'Ⅳ': 'D', 'Ⅴ': 'E'}
                for num in ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ']:
                    if num in content_map and content_map[num]:
                        options.append({
                            "key": num_to_key[num],
                            "text": content_map[num]
                        })

    return options[:5], multi_format


def extract_answer(text: str, question_type: str, multi_format: str = 'standard') -> List[str]:
    """提取答案"""
    # 提取答案区域的所有字符
    match = re.search(r'参考答案[：:]\s*([A-E①②③④⑤ⅠⅡⅢⅣⅤ.．\s,，]+?)(?=\n|【)', text)
    if not match:
        return []

    answer_text = match.group(1).strip()

    if question_type == 'single':
        letters = re.findall(r'[A-D]', answer_text)
        return letters[:1]

    # 多选题 - 根据格式处理
    if multi_format == 'standard':
        # 标准格式：ABC 或 A,B,C - 直接返回字母
        letters = re.findall(r'[A-E]', answer_text)
        return letters if letters else []

    elif multi_format in ['circle', 'roman']:
        # 编号格式（圆圈或罗马数字）：
        # 答案是单个字母（如D），需要从选项定义中查找该选项包含的编号
        # 然后将编号转换为对应的字母

        # 先提取答案字母
        answer_letters = re.findall(r'[A-E]', answer_text)
        if not answer_letters:
            return []

        answer_letter = answer_letters[0]  # 答案字母（如D）

        # 在文本中查找该选项的定义（如 D.①②③④ 或 A.Ⅱ.Ⅲ.Ⅳ）
        if multi_format == 'circle':
            # 查找 D.①②③④
            option_pattern = rf'{answer_letter}[.．]\s*([①②③④⑤\s、]+)'
            option_match = re.search(option_pattern, text)
            if option_match:
                option_content = option_match.group(1)
                nums = re.findall(r'[①②③④⑤]', option_content)
                if nums:
                    # 转换编号为字母
                    num_to_key = {'①': 'A', '②': 'B', '③': 'C', '④': 'D', '⑤': 'E'}
                    return [num_to_key[n] for n in nums if n in num_to_key]

        elif multi_format == 'roman':
            # 查找 A.Ⅱ.Ⅲ.Ⅳ 或 A.ⅡⅢⅣ
            option_pattern = rf'{answer_letter}[.．]\s*([ⅠⅡⅢⅣⅤ\s.．、]+)'
            option_match = re.search(option_pattern, text)
            if option_match:
                option_content = option_match.group(1)
                nums = re.findall(r'[ⅠⅡⅢⅣⅤ]', option_content)
                if nums:
                    # 转换罗马数字为字母
                    num_to_key = {'Ⅰ': 'A', 'Ⅱ': 'B', 'Ⅲ': 'C', 'Ⅳ': 'D', 'Ⅴ': 'E'}
                    return [num_to_key[n] for n in nums if n in num_to_key]

        # 如果无法从选项中提取，返回答案字母本身
        return [answer_letter]

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

    options, multi_format = extract_options(text, question_type)
    if not options:
        return None

    answer = extract_answer(text, question_type, multi_format)
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

    print("\n多选题答案数量分布:")
    for length in sorted(multi_ans_dist.keys()):
        print(f"  {length} 个答案: {multi_ans_dist[length]} 道")

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_questions, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 保存到 {output_file}")


if __name__ == '__main__':
    base_dir = '/Users/zhh/Downloads/2.送文档题库'
    output_file = 'parsed_questions_final.json'

    process_directory(base_dir, output_file)
