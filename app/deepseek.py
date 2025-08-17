from openai import OpenAI

from settings import DEEP_SEEK_API_KEY, DEEP_SEEK_BASE_URL

client = OpenAI(
    api_key = DEEP_SEEK_API_KEY,
    base_url = DEEP_SEEK_BASE_URL
)

response = client.chat.completions.create(
    model = "deepseek-chat",
    messages = [{"role": "user", "content": "Hello world"}]
)

print(response.choices[0].message.content)
