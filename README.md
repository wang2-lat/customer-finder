# Customer Finder

帮技术创始人找到产品的目标客户聚集地和验证渠道效果。

## 功能

- 搜索 Reddit/HackerNews/ProductHunt 相关讨论
- 分析讨论热度和用户痛点匹配度
- 输出 Top 10 潜在渠道
- 生成针对每个渠道的冷启动话术模板

## 安装


## 配置

创建 `.env` 文件（可选，用于 Reddit API）：


**获取 Reddit API 凭证：**
1. 访问 https://www.reddit.com/prefs/apps
2. 创建 "script" 类型应用
3. 复制 client_id 和 secret

## 使用


## 示例输出


## 注意事项

- 首次运行会较慢（需要抓取数据）
- Reddit API 有速率限制（60请求/分钟）
- HackerNews 使用公开 API（无需认证）
- ProductHunt 数据通过公开页面抓取