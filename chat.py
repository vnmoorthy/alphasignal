import os
from openai import OpenAI

_parasail_key = os.environ.get("PARASAIL_API_KEY", "")
if not _parasail_key:
    raise EnvironmentError("PARASAIL_API_KEY is not set. Add it to your Replit Secrets.")

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=_parasail_key,
)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of San Francisco?"},
]

chat_completion = client.chat.completions.create(
    model="parasail-glm-52",
    messages=messages,
    max_completion_tokens=1024,
)

response_message = chat_completion.choices[0].message
print(
    {
        "role": response_message.role,
        "content": response_message.content,
    }
)