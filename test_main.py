import asyncio
import traceback
from litellm import acompletion
async def translate_text(text, target_language="zh"):
    try:
        response = await acompletion(
            model="gemini/gemini-pro",
            messages=[
                {
                    "content": f"Translate the following text to {target_language}: {text}",
                    "role": "user",
                }
            ],
            stream=True,
        )
        
        # print(f"response: {response}")
        async for chunk in response:
            print(chunk.choices[0].delta.content)
    except:
        print(f"error occurred: {traceback.format_exc()}")
        pass



asyncio.run(translate_text('hello'))