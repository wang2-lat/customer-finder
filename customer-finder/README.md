# Customer Finder

自动发现和验证潜在付费客户的 CLI 工具。

## 功能

- 从 Reddit/HackerNews/ProductHunt 抓取关键词相关讨论
- 识别正在寻找解决方案的潜在客户
- 输出客户列表（含联系方式、痛点描述、讨论链接）
- 生成个性化触达话术模板

## 安装


## 配置

创建 `.env` 文件或设置环境变量：


### 获取 Reddit API 凭证

1. 访问 https://www.reddit.com/prefs/apps
2. 点击 "create another app"
3. 选择 "script"，填写名称和重定向 URI (http://localhost:8080)
4. 获取 client_id 和 client_secret

## 使用

### 基本搜索


### 指定时间范围


### 输出到文件


### 生成触达话术


## 参数说明

- `keywords`: 产品关键词（必需）
- `--platforms`: 搜索平台，可选 reddit/hackernews/producthunt（默认全部）
- `--days`: 搜索最近 N 天的内容（默认 30）
- `--min-score`: 最低评分/点赞数（默认 3）
- `--output`: 输出文件路径（默认 customers.json）
- `--limit`: 每个平台最多返回结果数（默认 50）

## 输出格式


## 注意事项

- 遵守各平台 API 使用条款
- 建议添加请求间隔避免限流
- 联系客户前请人工复核结果
- 触达话术需根据实际情况调整