import os
from openai import OpenAI
from pydantic import BaseModel
api_key = os.getenv('ARK_API_KEY')

client = OpenAI(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=api_key,
)
class Step(BaseModel):
    explanation: str  # Step details
    output: str       # Step computation results

class MathResponse(BaseModel):
    steps: list[Step]       # List of solution steps
    final_answer: str       # Final answer
response = client.responses.parse(
    model="doubao-seed-2-1-lite-260915",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "return in json format how can I solve 8x + 7 = -23"
                }
            ]
        }
    ],
    text_format=MathResponse
)

print(response.output_parsed)
