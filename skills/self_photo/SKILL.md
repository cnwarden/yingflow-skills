---
name: self_photo
description: 根据要求生成自拍照
---

# 自拍照生成

## 简介

自拍照生成

- 专业的文生自拍图AIGC专家


## Skill指令

当用户调用此Skill时，请按照以下流程执行, 并按照顺序输出中间思考过程，最终把结果整理并输出

准备：
从环境变量ARK_TOKEN获取对应的值, 如果不存在报错缺少ARK_TOKEN

1. 形成提示词
分析用户自拍需求，不要询问用户，如果没有按你理解的默认值替代：
- 年龄：默认20岁
- 头发：默认黑色
- 穿着：默认白色棉麻连衣裙
- 时间：默认午后
- 场景：默认咖啡店

基础提示词:
一位<年龄>亚洲女生，<头发>长发，自然微卷，素颜淡妆，皮肤白皙通透，穿着<穿着>，坐在窗边，<时间>阳光洒在脸上，在<场景>，微笑看向镜头，背景是绿植和白色窗帘，日系胶片色调，柔和光影，Canon EOS R5, 85mm f/1.4, 浅景深

根据分析结果替换提示词形成新的生图提示词 PROMPT

2. 生图服务调用

替换提示词 和 ARK_TOKEN，然后调用该服务

```bash
curl -X POST https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ARK_TOKEN>" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": <PROMPT>,
    "sequential_image_generation": "disabled",
    "response_format": "url",
    "size": "1728x2304",
    "stream": false,
    "watermark": false
}'
```

3. 解析结果

结果示例，解析json结果，获取url，并下载到本地

例如这里的图片url是"https://ark-acg-cn-beijing.tos-cn-beijing.volces.com/doubao-seedream-5-0/021772009955889982b29f8728970ed398f78ebc517c3ae230b92_0.jpeg?X-Tos-Algorithm=TOS4-HMAC-SHA256&X-Tos-Credential=AKLTYWJkZTExNjA1ZDUyNDc3YzhjNTM5OGIyNjBhNDcyOTQ%2F20260225%2Fcn-beijing%2Ftos%2Frequest&X-Tos-Date=20260225T085948Z&X-Tos-Expires=86400&X-Tos-Signature=4672d0b632e24bfac361ea331abcc6a44a170e88ede8980aa754c0f94ba7ffee&X-Tos-SignedHeaders=host"

```json
{"model":"doubao-seedream-5-0-260128","created":1772009988,"data":[{"url":"https://ark-acg-cn-beijing.tos-cn-beijing.volces.com/doubao-seedream-5-0/021772009955889982b29f8728970ed398f78ebc517c3ae230b92_0.jpeg?X-Tos-Algorithm=TOS4-HMAC-SHA256&X-Tos-Credential=AKLTYWJkZTExNjA1ZDUyNDc3YzhjNTM5OGIyNjBhNDcyOTQ%2F20260225%2Fcn-beijing%2Ftos%2Frequest&X-Tos-Date=20260225T085948Z&X-Tos-Expires=86400&X-Tos-Signature=4672d0b632e24bfac361ea331abcc6a44a170e88ede8980aa754c0f94ba7ffee&X-Tos-SignedHeaders=host","size":"3136x1312"}],"usage":{"generated_images":1,"output_tokens":16072,"total_tokens":16072}}
```

