import os
from openai import OpenAI
import base64

# 读取本地图片并进行Base64编码
def read_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

client = OpenAI(
    api_key="sk-ddcd1e783e694fe085fc7d21d262fb66",  # ✅ 正确：直接传入 API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 替换为你自己的本地图片路径
local_image_path = "D:/Users/lenovo/Desktop/competetion/smart_city/data/baitan/baitan_original/baitan_10.jpg"

completion = client.chat.completions.create(
    model="qwen-vl-max-latest", 
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{read_image_as_base64(local_image_path)}"
                    },
                },
                {"type": "text", "text": "是否存在摆摊,只回答yes or no?"},
            ],
        },
    ],
)

print(completion.choices[0].message.content)