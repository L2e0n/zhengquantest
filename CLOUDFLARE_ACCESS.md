# Cloudflare Access 配置指南

为 test.guguji.icu 添加登录验证

## 步骤1：启用 Zero Trust

1. 访问 https://dash.cloudflare.com
2. 在左侧菜单找到 **Zero Trust**（或 **Access**）
3. 首次使用需要创建一个 Team（团队名称随意，如 `guguji-team`）
4. 选择免费计划（Free Plan - 50 个用户足够）

## 步骤2：创建 Application

1. 进入 **Access** → **Applications**
2. 点击 **Add an application**
3. 选择 **Self-hosted**

### 应用配置

**Application name**: 证券考试题库

**Session duration**: 24 hours（用户登录后 24 小时内有效）

**Application domain**: 
- Subdomain: `test`
- Domain: `guguji.icu`

完整域名会显示：`test.guguji.icu`

点击 **Next**

## 步骤3：创建访问策略（Policy）

**Policy name**: 允许邮箱访问

**Action**: Allow

**Configure rules**:

### 选项A：仅允许特定邮箱（推荐）
- **Include**: 
  - Selector: `Emails`
  - Value: 输入允许的邮箱，如：
    ```
    your@email.com
    friend@example.com
    ```
  （每行一个）

### 选项B：允许任何邮箱（不推荐）
- **Include**:
  - Selector: `Emails ending in`
  - Value: `@gmail.com` 或 `@qq.com` 等

### 选项C：用一次性 PIN 码
- **Include**:
  - Selector: `Emails`
  - Value: 你的邮箱
- **Authentication methods**:
  - 选择 `One-time PIN`

点击 **Next** → **Add application**

## 步骤4：完成

✅ 配置完成！

现在访问 `https://test.guguji.icu` 会：
1. 跳转到 Cloudflare Access 登录页面
2. 输入邮箱地址
3. 收到验证码邮件
4. 输入验证码后进入网站
5. 24小时内无需重复登录

## 额外配置（可选）

### 1. 自定义登录页面
在 **Settings** → **Custom Pages** 可以自定义登录页样式

### 2. 启用 Google OAuth
在 **Settings** → **Authentication** 添加 Google 登录

### 3. 查看访问日志
在 **Logs** → **Access** 可以看到谁在什么时候登录了

## 免费限额

- ✅ 50 个用户
- ✅ 无限次登录
- ✅ 基础统计

## 注意事项

⚠️ 如果你想移除登录验证，只需在 Applications 列表中删除该应用即可。

---

配置完成后，所有访问者都需要通过邮箱验证才能使用网站！
