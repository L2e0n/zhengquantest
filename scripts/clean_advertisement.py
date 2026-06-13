#!/usr/bin/env python3
"""
清理题目中的广告文字
"""

import json
import re

def clean_advertisement(text: str) -> str:
    """清理广告文字"""
    if not text:
        return text

    # 要清理的广告模式
    patterns = [
        r'慧考智学.*?专业网校课程.*?版权所有',
        r'专业网校课程、题库软件、考试用书、资讯信息全方位一体化职业考试学习平台',
        r'慧考智学官网\s*www\.huikao8\.com\s*版权所有',
        r'慧考智学',
        r'www\.huikao8\.com',
    ]

    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL)

    # 清理多余的空白
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()

    return cleaned


def clean_questions(input_file: str, output_file: str):
    """清理题目文件"""
    print(f"读取题目文件: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    print(f"总共 {len(questions)} 道题目")

    cleaned_count = 0

    for q in questions:
        original_stem = q.get('stem', '')
        original_explanation = q.get('explanation', '')

        # 清理题干
        q['stem'] = clean_advertisement(q['stem'])

        # 清理解析
        if q.get('explanation'):
            q['explanation'] = clean_advertisement(q['explanation'])

        # 清理选项文本
        for option in q.get('options', []):
            option['text'] = clean_advertisement(option['text'])

        # 统计清理数量
        if (original_stem != q['stem'] or
            original_explanation != q.get('explanation', '')):
            cleaned_count += 1

    print(f"清理了 {cleaned_count} 道题目的广告文字")

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"已保存到: {output_file}")


if __name__ == "__main__":
    input_file = "scripts/parsed_questions.json"
    output_file = "scripts/parsed_questions_cleaned.json"

    clean_questions(input_file, output_file)

    print("\n✅ 清理完成！")
    print(f"请重新导入: {output_file}")
