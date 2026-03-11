#!/usr/bin/env python3
"""
微信公众号文章读取工具 (WeChat Article Reader)

本模块用于抓取和解析微信公众号文章内容，支持提取文章标题、公众号名称和正文内容。

功能特点:
    - 模拟微信内置浏览器访问，绕过部分访问限制
    - 自动处理重定向链接
    - 智能识别文章验证码拦截场景

使用方式:
    命令行: python weixin_reader.py <url>
    模块导入: from weixin_reader import read_wechat_article

依赖库:
    - httpx: 现代化的 HTTP 客户端，支持异步和同步请求
    - beautifulsoup4: HTML/XML 解析库，用于提取页面内容

作者: cnwarden
创建日期: 2026-03
"""

import sys
import httpx
from bs4 import BeautifulSoup

# ============================================================================
# 常量定义
# ============================================================================

# 模拟微信内置浏览器的 User-Agent
# 使用 iPhone 设备标识，MicroMessenger 为微信客户端标识
WECHAT_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "MicroMessenger/8.0.38(0x18002629) NetType/WIFI Language/zh_CN"
)

# HTTP 请求超时时间（秒）
REQUEST_TIMEOUT = 30

# ============================================================================
# 核心功能函数
# ============================================================================


def read_wechat_article(url: str) -> dict:
    """
    读取微信公众号文章内容

    该函数通过模拟微信客户端发送 HTTP 请求，获取公众号文章页面，
    然后使用 BeautifulSoup 解析 HTML 提取关键信息。

    工作流程:
        1. 构造模拟微信浏览器的请求头
        2. 发送 GET 请求获取文章页面
        3. 解析 HTML 提取标题、公众号名称、正文
        4. 处理异常情况（验证码拦截、解析失败等）

    Args:
        url (str): 微信公众号文章链接
            格式示例: https://mp.weixin.qq.com/s?__biz=xxx&mid=xxx&idx=1&sn=xxx

    Returns:
        dict: 包含以下字段的字典
            - title (str): 文章标题，解析失败时为空字符串
            - account (str): 公众号名称，解析失败时为空字符串
            - content (str): 文章正文内容，解析失败时为空字符串
            - error (str | None): 错误信息，成功时为 None

    Raises:
        不抛出异常，所有错误通过返回字典的 error 字段返回

    Example:
        >>> result = read_wechat_article("https://mp.weixin.qq.com/s/xxx")
        >>> if result["error"]:
        ...     print(f"读取失败: {result['error']}")
        >>> else:
        ...     print(f"标题: {result['title']}")
    """
    # 构造请求头，模拟微信内置浏览器
    # Accept 和 Accept-Language 保持标准浏览器配置
    headers = {
        "User-Agent": WECHAT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    # 初始化返回结果结构
    result = {"title": "", "account": "", "content": "", "error": None}

    try:
        # 使用 httpx 客户端发送请求
        # follow_redirects=True: 自动跟随 302 等重定向
        # timeout: 设置超时避免长时间阻塞
        with httpx.Client(follow_redirects=True, timeout=REQUEST_TIMEOUT) as client:
            resp = client.get(url, headers=headers)

            # 使用 BeautifulSoup 解析 HTML
            # 'html.parser' 是 Python 内置解析器，无需额外依赖
            soup = BeautifulSoup(resp.text, 'html.parser')

            # ----------------------------------------------------------------
            # 提取文章标题
            # 微信文章标题通常在 h1 或 h2 标签中，class 为 rich_media_title
            # ----------------------------------------------------------------
            title_elem = (
                soup.find('h1', class_='rich_media_title') or
                soup.find('h2', class_='rich_media_title')
            )
            if title_elem:
                result["title"] = title_elem.get_text(strip=True)

            # ----------------------------------------------------------------
            # 提取公众号名称
            # 公众号名称在 id="js_name" 的链接中，或 class 为 rich_media_meta_nickname
            # ----------------------------------------------------------------
            account_elem = (
                soup.find('a', id='js_name') or
                soup.find('span', class_='rich_media_meta_nickname')
            )
            if account_elem:
                result["account"] = account_elem.get_text(strip=True)

            # ----------------------------------------------------------------
            # 提取正文内容
            # 正文在 id="js_content" 的 div 中，备选 class 为 rich_media_content
            # separator='\n' 保持段落换行，strip=True 去除首尾空白
            # ----------------------------------------------------------------
            content_elem = (
                soup.find('div', id='js_content') or
                soup.find('div', class_='rich_media_content')
            )
            if content_elem:
                result["content"] = content_elem.get_text(separator='\n', strip=True)
            else:
                # 无法找到正文元素，检查是否被验证码拦截
                # 微信对部分文章会要求输入验证码才能访问
                if soup.find(text=lambda t: t and '验证' in t):
                    result["error"] = "文章需要验证码，无法直接访问"
                else:
                    result["error"] = "无法解析文章内容"

    except httpx.TimeoutException:
        # 请求超时，可能是网络问题或服务器响应慢
        result["error"] = f"请求超时（{REQUEST_TIMEOUT}秒），请检查网络连接"
    except httpx.RequestError as e:
        # 其他请求错误（DNS 解析失败、连接被拒绝等）
        result["error"] = f"请求失败: {str(e)}"
    except Exception as e:
        # 捕获其他未预期的异常，确保函数不会崩溃
        result["error"] = f"未知错误: {str(e)}"

    return result


# ============================================================================
# 命令行入口
# ============================================================================


def main():
    """
    命令行入口函数

    解析命令行参数，调用文章读取函数，并格式化输出结果。

    Usage:
        python weixin_reader.py <url>

    Exit Codes:
        0: 成功读取文章
        1: 参数错误或读取失败
    """
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python weixin_reader.py <url>")
        print("示例: python weixin_reader.py 'https://mp.weixin.qq.com/s/xxx'")
        sys.exit(1)

    # 获取文章 URL
    url = sys.argv[1]

    # 调用核心函数读取文章
    result = read_wechat_article(url)

    # 处理错误情况
    if result["error"]:
        print(f"错误: {result['error']}")
        sys.exit(1)

    # 格式化输出结果
    if result["title"]:
        print(f"标题: {result['title']}")
    if result["account"]:
        print(f"公众号: {result['account']}")
    if result["content"]:
        print(f"\n--- 正文内容 ---\n")
        print(result["content"])


if __name__ == "__main__":
    main()
