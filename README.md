# YingFlow Skills

**[English](README_EN.md)** | 中文

一套为 Claude Code 及兼容 Agent 框架设计的 AI 技能集合。通过专业的内容生成、数据提取和自动化工作流工具，扩展 Agent 能力边界。

## 项目简介

YingFlow Skills 提供模块化、生产就绪的技能组件，可轻松集成到 AI 编程助手中。每个技能遵循统一的接口规范，并附带完整文档。

## 可用技能

### weixin_reader

**微信公众号文章阅读器** — 提取并解析微信公众号文章内容。

| 特性 | 说明 |
|------|------|
| **功能** | 抓取并解析 `mp.weixin.qq.com` 文章 |
| **方式** | 模拟移动端 User-Agent（微信内置浏览器） |
| **输出** | 结构化数据：标题、公众号名称、完整正文 |
| **依赖** | `httpx`, `beautifulsoup4` |

**核心特性：**
- 使用真实移动端请求头绕过基础反爬机制
- 自动处理重定向
- 干净的文本提取与格式化
- 验证码保护内容的错误处理

**使用示例：**
```bash
python3 weixin_reader.py "https://mp.weixin.qq.com/s?__biz=xxx&mid=xxx"
```

---

### self_photo

**AI 自拍照生成器** — 基于豆包 Seedream 模型生成写实风格自拍图像。

| 特性 | 说明 |
|------|------|
| **功能** | 文生图自拍照生成 |
| **模型** | 豆包 Seedream 5.0 (doubao-seedream-5-0-260128) |
| **输出** | 高分辨率人像图片 (1728x2304) |
| **风格** | 日系胶片质感、柔和光影、浅景深 |

**核心特性：**
- 从自然语言输入智能构建提示词
- 可配置参数：年龄、发型、服装、时间、场景
- 专业相机模拟（Canon EOS R5, 85mm f/1.4）
- 直接 URL 输出并支持自动下载到本地

**默认参数：**
- 年龄：20 岁
- 发型：黑色自然微卷长发
- 服装：白色棉麻连衣裙
- 时间：午后阳光
- 场景：带绿植和白色窗帘的咖啡店

**环境要求：**
- 需配置 `ARK_TOKEN` 环境变量（火山引擎 API 认证）

---

## 安装方式

### Claude Code 用户

```bash
# 克隆仓库
git clone https://github.com/cnwarden/yingflow-skills.git

# 复制技能到 Claude Code 技能目录
cp -r yingflow-skills/skills/* ~/.claude/skills/
```

### 其他 Agent 框架

每个技能均为独立模块，可按照您框架的技能注册模式进行集成。详细集成说明请参阅各技能目录下的 `SKILL.md` 文件。

## 目录结构

```
skills/
├── weixin_reader/
│   ├── SKILL.md           # 技能清单与文档
│   └── weixin_reader.py   # 主程序实现
└── self_photo/
    └── SKILL.md           # 技能清单（含内嵌逻辑）
```

## 参与贡献

欢迎贡献新技能，请确保遵循现有结构规范：

1. 在 `skills/` 下创建以技能名命名的目录
2. 包含 `SKILL.md`，注明触发条件和使用说明
3. 按需添加实现文件
4. 更新本 README 文档

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

*为 AI Agent 生态而构建*
