import os

from langchain_community.chat_models import ChatZhipuAI

# 设置环境变量
# 请将密钥替换为你自己的密钥，可以在智谱官网申请。LANGCHAIN对应的密钥也可以在其官网上申请。
os.environ["ZHIPUAI_API_KEY"] = "1cb56cec680228ed7b3a9f33d9e1b3b4.fln59ZZnsCVNEGlj"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["TAVILY_API_KEY"] = "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"
os.environ["LANGCHAIN_API_KEY"] = "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"

model = ChatZhipuAI(
    model="glm-4",
    temperature=0.5,
)

# 华为云密钥，请替换成自己申请的密钥，并将桶名替换为实际桶名，Endpoint参数在申请华为云储存时获取
OBS_ACCESS_KEY = 'JMZUN3ANMT1YOGL7FGQK'
OBS_SECRET_KEY = 'ENzg76QSnUHKIThEywqlqakZEx6qXqtNYnaazM6f'
OBS_BUCKET_NAME = 'test-e795'
Endpoint = 'https://obs.cn-east-3.myhuaweicloud.com'
