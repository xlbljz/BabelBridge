import asyncio
import subprocess
import openai
import sys

from litellm import acompletion
import asyncio
import os
import traceback


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

        async for chunk in response:
            print(chunk.choices[0].delta.content)

    except:
        print(f"error occurred: {traceback.format_exc()}")
        sys.exit(1)


async def read_stream_and_translate(stream, target_language="zh"):
    while True:
        line = await stream.readline()
        if line:
            translated_line = await translate_text(
                line.decode("utf-8"), target_language
            )
            print(translated_line)
        else:
            break


async def main():
    # 启动子进程
    process = await asyncio.create_subprocess_exec(
        "memgpt",
        "run",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )

    # 创建读取和翻译 stdout 和 stderr 的任务
    stdout_task = asyncio.create_task(read_stream_and_translate(process.stdout))
    stderr_task = asyncio.create_task(read_stream_and_translate(process.stderr))

    # 等待子进程结束
    await process.wait()

    # 等待所有任务完成
    await asyncio.gather(stdout_task, stderr_task)

    # 子进程结束后的输入处理
    while True:
        user_input = input("请输入命令行输入: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        translated_input = await translate_text(
            user_input, "en"
        )  # 假设命令行工具使用英文
        process.stdin.write((translated_input + "\n").encode("utf-8"))
        await process.stdin.drain()

        # 处理子进程的输出
        line = await process.stdout.readline()
        if line:
            translated_line = await translate_text(line.decode("utf-8"), "zh")
            print(translated_line)
        else:
            break


if __name__ == "__main__":
    asyncio.run(main())
