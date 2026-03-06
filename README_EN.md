# YingFlow Skills

[中文](README.md) | **English**

A curated collection of AI agent skills designed for Claude Code and compatible agent frameworks. These skills extend agent capabilities with specialized tools for content generation, data extraction, and automation workflows.

## Overview

YingFlow Skills provides modular, production-ready skills that can be easily integrated into AI coding assistants. Each skill follows a consistent interface pattern and includes comprehensive documentation.

## Available Skills

### weixin_reader

**WeChat Article Reader** — Extract and parse content from WeChat Official Account articles.

| Feature | Description |
|---------|-------------|
| **Purpose** | Fetch and parse articles from `mp.weixin.qq.com` |
| **Method** | Mobile User-Agent simulation (WeChat in-app browser) |
| **Output** | Structured data: title, account name, full article content |
| **Dependencies** | `httpx`, `beautifulsoup4` |

**Key Features:**
- Bypasses basic anti-scraping measures using authentic mobile headers
- Automatic redirect handling
- Clean text extraction with proper formatting
- Error handling for CAPTCHA-protected content

**Usage:**
```bash
python3 weixin_reader.py "https://mp.weixin.qq.com/s?__biz=xxx&mid=xxx"
```

---

### self_photo

**AI Selfie Generator** — Generate photorealistic selfie images using Doubao's Seedream model.

| Feature | Description |
|---------|-------------|
| **Purpose** | Text-to-image selfie generation |
| **Model** | Doubao Seedream 5.0 (doubao-seedream-5-0-260128) |
| **Output** | High-resolution portrait images (1728x2304) |
| **Style** | Japanese film aesthetic, soft lighting, shallow depth of field |

**Key Features:**
- Intelligent prompt construction from natural language input
- Configurable parameters: age, hair style, clothing, time of day, scene
- Professional camera simulation (Canon EOS R5, 85mm f/1.4)
- Direct URL output with automatic local download

**Default Parameters:**
- Age: 20 years old
- Hair: Black, naturally wavy long hair
- Clothing: White linen dress
- Time: Afternoon sunlight
- Scene: Coffee shop with plants and white curtains

**Requirements:**
- `ARK_TOKEN` environment variable for Volcengine API authentication

---

## Installation

### For Claude Code

```bash
# Clone the repository
git clone https://github.com/cnwarden/yingflow-skills.git

# Copy skills to Claude Code skills directory
cp -r yingflow-skills/skills/* ~/.claude/skills/
```

### For Other Agent Frameworks

Each skill is self-contained and can be integrated following your framework's skill registration pattern. Refer to individual `SKILL.md` files for detailed integration instructions.

## Skill Structure

```
skills/
├── weixin_reader/
│   ├── SKILL.md           # Skill manifest and documentation
│   └── weixin_reader.py   # Main implementation
└── self_photo/
    └── SKILL.md           # Skill manifest with embedded logic
```

## Contributing

Contributions are welcome. Please ensure new skills follow the existing structure:

1. Create a directory under `skills/` with your skill name
2. Include a `SKILL.md` with trigger conditions and usage instructions
3. Add implementation files as needed
4. Update this README with skill documentation

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*Built for the AI agent ecosystem*
