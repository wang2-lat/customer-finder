# Customer Finder

帮技术创始人找到产品的真实付费客户渠道。

## 功能

- 🎯 根据产品描述自动生成客户画像
- 🔍 爬取 Reddit/ProductHunt 相关讨论
- 📊 输出带联系方式的潜在客户清单（CSV）
- 📧 支持邮箱提取和联系方式聚合

## 安装


## 配置

### 1. 获取 Reddit API 密钥

访问 https://www.reddit.com/prefs/apps

1. 点击 "create another app"
2. 选择 "script" 类型
3. 填写名称和描述
4. 复制 `client_id` 和 `client_secret`

### 2. 运行配置向导


或手动创建 `.env` 文件：


## 使用

### 基础用法


### 自定义输出路径


### 调整爬取数量


## 输出格式

生成的 CSV 包含以下字段：

| 字段 | 说明 |
|------|------|
| platform | 平台（Reddit/ProductHunt） |
| author | 作者用户名 |
| email | 邮箱（如果提取到） |
| title | 帖子/产品标题 |
| url | 原始链接 |
| source | 来源（subreddit/分类） |
| score | 热度分数 |

## 下一步行动

1. **筛选高质量线索**：打开CSV，关注 score > 10 且有邮箱的记录
2. **个性化触达**：
   - 访问原始链接了解用户痛点
   - 发送个性化邮件（避免群发模板）
   - 在Reddit评论中提供价值（非广告）
3. **持续跟进**：每周运行一次，发现新讨论

## 注意事项

- Reddit API 限制：60请求/分钟
- 邮箱提取率约 10-20%（取决于用户公开程度）
- LinkedIn 需要付费 API，当前版本不支持
- 遵守平台服务条款，避免过度爬取

## 故障排查

### Reddit API 错误


### 无结果

- 尝试更通用的产品描述
- 增加 `--reddit-limit` 参数
- 检查关键词是否过于小众

## 许可证

MIT