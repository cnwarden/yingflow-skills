#!/usr/bin/env python3
"""发布一条记录到 yingflow.cn 飞书多维表格（发布表）。

调用 /api/v1/feishu/bitable/table/add 接口写入一条发布记录。
除「唯一ID」（表格自动生成）外，其余字段都需要在发布时提供。

字段：
  发布渠道 / 发布类型 / 发布账号 / 发布时间 / 发布状态 /
  标题 / 内容 / 标签 / 图片 / 封面图
其中「发布时间」是日期列，传毫秒时间戳；不传则默认取当前时间。

用法：
  python3 publish.py \
    --channel "抖音" --type "视频" --account "一禾电台" \
    --status "已发布" --title "标题" --content "正文" \
    --tags "#AI #科技" --image "https://...jpg" --cover "https://...jpg" \
    [--publish-time 1789474176000]

使用前设置 YINGFLOW_MD_TOKEN 和 YINGFLOW_TABLE_TOKEN 环境变量。
成败判断：响应 code == 0 为成功，返回 record_id；非 0 是飞书错误码。
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://yingflow.cn/api/v1/feishu/bitable/table/add"
CHANNEL_VALUES = ("小红书", "抖音", "百家号", "视频号")
TYPE_VALUES = ("图文", "视频")
STATUS_VALUES = ("已发布", "待发布", "发布失败")

# 命令行参数名 -> 表格列名（枚举字段和发布时间单独处理）
FIELD_MAP = {
    "account": "发布账号",
    "title": "标题",
    "content": "内容",
    "tags": "标签",
    "image": "图片",
    "cover": "封面图",
}


def validate(args) -> str | None:
    """校验字段；通过返回 None，失败返回错误信息。"""
    if args.channel not in CHANNEL_VALUES:
        return f"发布渠道只能是：{'、'.join(CHANNEL_VALUES)}"
    if args.type not in TYPE_VALUES:
        return f"发布类型只能是：{'、'.join(TYPE_VALUES)}"
    if args.status not in STATUS_VALUES:
        return f"发布状态只能是：{'、'.join(STATUS_VALUES)}"
    for name in ("account", "title", "content"):
        if not getattr(args, name).strip():
            return f"{FIELD_MAP[name]}不能为空"
    # 标签：多个标签之间只能用空格分隔（不允许逗号），且每个必须以 # 开头
    if not args.tags.strip():
        return "标签不能为空"
    if "," in args.tags or "，" in args.tags:
        return "标签之间必须用空格分隔，不允许使用逗号"
    tags = args.tags.split()
    bad = [t for t in tags if not t.startswith("#")]
    if bad:
        return f"标签必须以 # 开头，不合法的标签: {' '.join(bad)}"
    # 图片：支持逗号连接的多个 URL，每个都必须是 http(s) 链接
    urls = [u.strip() for u in args.image.split(",")]
    if not urls[0] or any(not u for u in urls):
        return "图片不能为空，多个图片链接必须用逗号分隔"
    bad = [u for u in urls if not re.match(r"^https?://", u)]
    if bad:
        return f"图片必须是链接（http/https 开头）: {', '.join(bad)}"
    # 封面图：可为空；一旦提供必须是 http(s) 链接
    if args.cover and args.cover.strip():
        if not re.match(r"^https?://", args.cover.strip()):
            return f"封面图必须是链接（http/https 开头）: {args.cover}"
    return None


def build_fields(args) -> dict:
    fields = {}
    for arg_name, col_name in FIELD_MAP.items():
        value = getattr(args, arg_name)
        if value is not None:
            fields[col_name] = value
    fields["发布渠道"] = [args.channel]
    fields["发布类型"] = [args.type]
    fields["发布状态"] = [args.status]
    # 发布时间：日期列 -> 毫秒时间戳，默认取当前时间
    fields["发布时间"] = args.publish_time if args.publish_time else int(time.time() * 1000)
    return fields


def add_record(md_token: str, table_token: str, fields: dict) -> dict:
    payload = json.dumps(
        {"md_token": md_token, "table_token": table_token, "fields": fields}
    ).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            result = json.loads(body)
        except json.JSONDecodeError:
            result = None
        if isinstance(result, dict) and "code" in result:
            return result
        return {"code": -1, "message": f"HTTP {e.code}: {body}"}
    except urllib.error.URLError as e:
        return {"code": -1, "message": f"网络错误: {e.reason}"}


def main() -> int:
    p = argparse.ArgumentParser(description="发布一条记录到 yingflow 发布表")
    p.add_argument("--channel", required=True, help="发布渠道：小红书/抖音/百家号/视频号")
    p.add_argument("--type", dest="type", required=True, help="发布类型：图文/视频")
    p.add_argument("--account", required=True, help="发布账号")
    p.add_argument("--status", required=True, help="发布状态：已发布/待发布/发布失败")
    p.add_argument("--title", required=True, help="标题")
    p.add_argument("--content", required=True, help="内容")
    p.add_argument("--tags", required=True, help="标签")
    p.add_argument("--image", required=True, help="图片")
    p.add_argument("--cover", default="", help="封面图 URL，可为空")
    p.add_argument("--publish-time", type=int, dest="publish_time",
                   help="发布时间（毫秒时间戳），默认当前时间")
    args = p.parse_args()

    for name in ("YINGFLOW_MD_TOKEN", "YINGFLOW_TABLE_TOKEN"):
        if not os.environ.get(name, "").strip():
            print(f"✗ 缺少环境变量 {name}，请设置后重试")
            return 1

    err = validate(args)
    if err:
        print(f"✗ 校验失败: {err}")
        return 1

    fields = build_fields(args)
    print(f"⬆ 提交记录: {json.dumps(fields, ensure_ascii=False)}")
    result = add_record(os.environ["YINGFLOW_MD_TOKEN"].strip(), os.environ["YINGFLOW_TABLE_TOKEN"].strip(), fields)

    if result.get("code") == 0:
        record_id = result.get("data", {}).get("record", {}).get("record_id", "")
        print(f"✓ 发布成功，record_id: {record_id}")
        return 0
    print(f"✗ 发布失败 code={result.get('code')}: {result.get('message')}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
