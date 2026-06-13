# 部署到 test.guguji.icu

## 方案一：Cloudflare Pages（推荐）

### 1. 创建 GitHub 仓库

```bash
# 在 GitHub 创建新仓库（私有或公开）
# 仓库名：zhengquantest

# 添加远程仓库
git remote add origin https://github.com/你的用户名/zhengquantest.git

# 推送代码
git push -u origin master
```

### 2. 连接 Cloudflare Pages

1. 访问 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 进入 **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**
3. 选择你的 GitHub 仓库 `zhengquantest`
4. 构建配置：
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
   - **Root directory**: `/`
5. 点击 **Save and Deploy**

### 3. 配置自定义域名

1. 在 Cloudflare Pages 项目页面，进入 **Custom domains**
2. 点击 **Set up a custom domain**
3. 输入：`test.guguji.icu`
4. Cloudflare 会自动添加 DNS 记录（因为你的域名已经在 Cloudflare）
5. 等待几分钟，SSL 证书自动配置完成

✅ 完成！访问 `https://test.guguji.icu`

---

## 方案二：Vercel

### 1. 安装 Vercel CLI

```bash
npm i -g vercel
```

### 2. 部署

```bash
vercel
```

按提示操作：
- 选择 GitHub 仓库或直接部署本地代码
- Project Name: `zhengquantest`
- Build Command: `npm run build`
- Output Directory: `dist`

### 3. 配置域名

```bash
vercel domains add test.guguji.icu
```

然后在你的域名 DNS 添加 CNAME 记录：
- Name: `test`
- Value: `cname.vercel-dns.com`

---

## 方案三：Netlify

### 1. 安装 Netlify CLI

```bash
npm i -g netlify-cli
```

### 2. 部署

```bash
netlify init
```

按提示操作，构建配置：
- Build command: `npm run build`
- Publish directory: `dist`

### 3. 配置域名

在 Netlify Dashboard：
- **Domain settings** → **Add custom domain**
- 输入 `test.guguji.icu`
- 添加 DNS 记录（CNAME 或 A 记录）

---

## 推荐：Cloudflare Pages

**优势**：
- ✅ 完全免费，无限流量
- ✅ 全球 CDN，中国访问速度快
- ✅ 自动 HTTPS
- ✅ 域名已在 Cloudflare，DNS 配置自动完成
- ✅ 每次 push 自动部署

**部署后特性**：
- 每次推送到 `master` 分支自动部署
- 提供预览链接（`.pages.dev`）
- 支持环境变量
- 支持自定义构建命令

---

## 本地预览构建结果

```bash
npm run build
npm run preview
```

访问 `http://localhost:4173`

---

## 注意事项

1. **题库数据**：首次访问需要手动导入 `scripts/parsed_questions_cleaned.json`
2. **数据持久化**：所有数据保存在用户浏览器 IndexedDB，清除浏览器数据会丢失
3. **备份**：建议定期使用"设置"页面的"导出备份"功能
4. **更新题库**：重新解析 PDF 后，用户需要重新导入

---

## GitHub Actions 自动部署（可选）

已包含 `.github/workflows/deploy.yml`，需要配置 Secrets：

1. 在 GitHub 仓库 **Settings** → **Secrets and variables** → **Actions**
2. 添加：
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`

获取方式：
- API Token: Cloudflare Dashboard → My Profile → API Tokens → Create Token
- Account ID: Cloudflare Dashboard → Workers & Pages → 项目页面右侧

配置后，每次 push 自动部署！
