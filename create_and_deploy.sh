#!/bin/bash
set -e

echo "🚀 开始部署证券考试网站..."
echo ""

# 检查 gh 是否已安装
if ! command -v gh &> /dev/null; then
    echo "❌ 请先安装 GitHub CLI: brew install gh"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "❌ 请先登录 GitHub: gh auth login"
    exit 1
fi

cd /Users/zhh/Downloads/cybcow/zhengquantest

echo "📦 创建 GitHub 仓库..."
gh repo create zhengquantest --public --description "证券从业资格考试题库系统 - Vue 3 + TypeScript" --source=. --remote=origin --push

echo ""
echo "✅ 仓库创建并推送成功！"
echo ""
echo "📋 接下来的步骤："
echo ""
echo "1. 访问 https://dash.cloudflare.com"
echo "2. Workers & Pages → Create application → Pages → Connect to Git"
echo "3. 选择 zhengquantest 仓库"
echo "4. 构建配置："
echo "   - Build command: npm run build"
echo "   - Build output: dist"
echo "5. 部署完成后，添加自定义域名: test.guguji.icu"
echo ""
echo "🎉 部署指南已保存在 DEPLOY.md"
