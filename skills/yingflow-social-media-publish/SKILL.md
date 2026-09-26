---
name: yingflow-social-media-publish
description: |
  发布社交媒体内容到 yingflow.cn。当用户提到`发布到小红书`、`发布到yingflow`等发布意图时触发，
  将发布记录写入 yingflow 多维表格。
metadata:
  clawdbot:
    emoji: 🚀
    requires:
      os: [linux, darwin]
    priority: 1
---

# YingFlow 社交媒体发布器

## 一、发布记录到多维表格

通过 `/api/v1/feishu/bitable/table/add` 接口，把一条发布记录写入 yingflow 发布表。

### 发布表字段

除「唯一ID」（表格自动生成，无需提交）外，发布账号、标题、内容、标签、图片和三个枚举字段均须提供有效值；发布时间不传默认当前时间，封面图可以留空：

| 列名 | 类型 | 参数 |
|---|---|---|
| 发布渠道 | 多选（提交时为单元素数组） | `--channel`：只能是「小红书」「抖音」「百家号」「视频号」 |
| 发布类型 | 多选（提交时为单元素数组） | `--type`：只能是「图文」「视频」 |
| 发布账号 | 文本 | `--account` |
| 发布时间 | 日期（毫秒时间戳） | `--publish-time`，不传默认当前时间 |
| 发布状态 | 多选（提交时为单元素数组） | `--status`：只能是「已发布」「待发布」「发布失败」 |
| 标题 | 文本 | `--title` |
| 内容 | 文本 | `--content` |
| 标签 | 文本 | `--tags`：每个标签以 `#` 开头，用空格分隔，不能用逗号 |
| 图片 | 文本 | `--image`：多个图片 URL 用逗号连接 |
| 封面图 | 文本 | `--cover`：可为空，提供时必须是 http(s) URL |

### 流程

1. **组织字段**：从用户提供的内容里抽取/整理上述字段。字段值缺失时向用户确认，不要臆造；封面图允许留空。发布渠道、发布类型和发布状态都必须属于上表列出的值，不要推断或创造其他选项。
2. **提交记录**：只能通过 `scripts/publish.py` 写入；脚本校验三个枚举字段，并按多选列要求将发布渠道、发布类型、发布状态转换成单元素数组。当前这张表的多选列未拒绝新选项（实测 `已完成` 被接受），不能绕过脚本直接向网关提交记录来期待服务端拒绝非法状态。成败只看响应 `code`（`0` 成功，非 `0` 是飞书错误码，如 `91403` 权限不足）。
3. 成功后把返回的 `record_id` 反馈给用户。

### 用法

```bash
export YINGFLOW_MD_TOKEN="<你的表格 app_token>"
export YINGFLOW_TABLE_TOKEN="<你的数据表 token>"
python3 scripts/publish.py \
  --channel "抖音" --type "视频" --account "一禾电台" \
  --status "待发布" --title "标题" --content "正文内容" \
  --tags "#AI #科技" --image "https://example.com/a.jpg,https://example.com/b.jpg" --cover ""
```

运行前由用户在环境中设置 `YINGFLOW_MD_TOKEN`（表格 app_token）和 `YINGFLOW_TABLE_TOKEN`（数据表 token）。技能不得在脚本、命令参数或文档中写入实际 token；缺少环境变量时提醒用户设置后重试。
