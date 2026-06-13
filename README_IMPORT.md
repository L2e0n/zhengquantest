# 证券考试题库导入指南

## 📦 已完成的工作

已成功从 `/Users/zhh/Downloads/2.送文档题库` 解析出 **3320 道题目**：

### 题库统计
- **总题数**: 3320 题
- **金融基础知识**: 3223 题
- **证券法律法规**: 97 题
- **单选题**: 2931 题
- **多选题**: 389 题

### 题目来源
- 📘 章节练习（按8章分类）
- 📝 考前点题卷（3套）
- 📅 历年真题（2019-2024年）

### 解析文件
已生成标准JSON格式：`scripts/parsed_questions.json`

---

## 🚀 导入到系统

### 方法一：浏览器批量导入（推荐）

1. **启动开发服务器**
   ```bash
   npm run dev
   ```

2. **访问导入页面**
   ```
   http://localhost:5173/import-batch.html
   ```

3. **选择JSON文件**
   - 点击"选择JSON文件"
   - 选择 `scripts/parsed_questions.json`
   - 预览题目统计信息
   - 点击"开始导入"

4. **等待导入完成**
   - 进度条显示导入进度
   - 自动去重（根据题目内容hash）
   - 导入完成后自动跳转到首页

### 方法二：系统自带导入功能

1. 启动系统：`npm run dev`
2. 访问：`http://localhost:5173/import`
3. 上传 `scripts/parsed_questions.json`
4. 系统会自动解析和导入

---

## 📂 文件说明

```
zhengquantest/
├── scripts/
│   ├── parse_pdf_questions.py    # PDF解析脚本
│   └── parsed_questions.json     # 解析结果（3320题）
├── public/
│   └── import-batch.html         # 浏览器批量导入页面
└── README_IMPORT.md              # 本文档
```

---

## 🔧 重新解析PDF

如果需要重新解析PDF或添加新的PDF文件：

```bash
# 安装依赖（如果未安装）
pip3 install pymupdf

# 运行解析脚本
python3 scripts/parse_pdf_questions.py \
  "/Users/zhh/Downloads/2.送文档题库" \
  scripts/parsed_questions.json

# 查看解析结果统计
python3 -c "
import json
with open('scripts/parsed_questions.json') as f:
    questions = json.load(f)
print(f'总题数: {len(questions)}')
print(f'单选: {len([q for q in questions if q[\"type\"]==\"single\"])}')
print(f'多选: {len([q for q in questions if q[\"type\"]==\"multiple\"])}')
"
```

---

## 📋 JSON数据格式

解析后的JSON遵循系统标准格式：

```json
{
  "section": "finance_basic",           // 科目
  "chapter": "第一章 金融市场体系/第一节 金融市场概述",
  "type": "single",                     // 题型：single/multiple/true_false
  "stem": "题干内容",
  "options": [
    {"key": "A", "text": "选项A内容"},
    {"key": "B", "text": "选项B内容"}
  ],
  "answer": ["A"],                      // 正确答案
  "explanation": "解析内容",
  "source": "PDF文件名",
  "tags": [],
  "contentHash": "md5哈希值"           // 用于去重
}
```

---

## ✅ 导入后验证

导入完成后，在系统首页可以看到：

- ✅ 总题数统计
- ✅ 按科目分类（金融基础/法律法规）
- ✅ 可以开始练习
- ✅ 错题本功能可用

---

## 🎯 下一步

导入完成后，你可以：

1. **开始练习**：首页点击"金融基础练习"或"法律法规练习"
2. **查看题库**：浏览所有题目，支持按章节/题型筛选
3. **错题复习**：答错的题目自动进入错题本
4. **模拟考试**：按科目进行模拟考试

---

## 🐛 常见问题

**Q: 导入后题目数量不对？**
A: 系统会自动去重，相同题目（根据contentHash）只保留一条。

**Q: 如何删除已导入的题目？**
A: 在设置页面可以导出备份后清空数据库重新导入。

**Q: PDF解析出错？**
A: 确保PDF文件格式正确，题目格式为慧考智学标准格式（题号+题干+选项+参考答案+解析）。

---

Generated on 2026-06-13
