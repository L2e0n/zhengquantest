#!/usr/bin/env python3
"""
修复题目选项末尾的多余数字
例如: "D. 40％ 9" -> "D. 40％"
"""

import json
import re

def fix_trailing_numbers(text):
    """删除选项文本末尾的孤立数字"""
    return re.sub(r'\s+\d+\s*$', '', text)

def main():
    input_file = '../public/questions.json'
    output_file = '../public/questions.json'

    print('读取题库文件...')
    with open(input_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    fixed_count = 0

    print('开始修复...')
    for q in questions:
        for opt in q.get('options', []):
            original_text = opt.get('text', '')
            fixed_text = fix_trailing_numbers(original_text)

            if original_text != fixed_text:
                opt['text'] = fixed_text
                fixed_count += 1
                print(f"修复: {opt['key']}: {original_text} -> {fixed_text}")

    print(f'\n共修复 {fixed_count} 个选项')

    print('保存修复后的题库...')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print('✅ 完成！')

if __name__ == '__main__':
    main()
