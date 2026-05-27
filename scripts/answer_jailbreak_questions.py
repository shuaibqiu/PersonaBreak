import os
import csv
import asyncio
from typing import Callable
from call_model import call_closed_model
from prompt import score_prompt
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "data")

async def answer_jailbreak_questions(
    input_csv: str = os.path.join(_DATA_DIR, "rewrite.csv"),
    output_csv: str = os.path.join(_DATA_DIR, "answer.csv"),
    system_prompt: str = score_prompt,
    model_call_func: Callable = call_closed_model,
    encoding: str = "utf-8"
) -> None:
    # 读取原始困境文件
    with open(input_csv, 'r', encoding=encoding) as f:
        reader = csv.reader(f)
        header = next(reader)                     # 跳过表头
        rows = [row for row in reader]


    output_rows = []
    for row in rows:
        question = row[2].strip()
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        for attempt in range(3):
            try:
                raw = await model_call_func(messages, temperature=0.7)
                if isinstance(raw, dict) and 'choices' in raw:
                    answer = raw['choices'][0]['message']['content']
                elif isinstance(raw, str):
                    answer = raw
                else:
                    answer = f"[错误] {raw.get('error', '未知返回类型')}"
                answer = answer.strip()
                print(f"完成了第{row[0]}")
                break
            except Exception as e:
                if attempt < 2:
                    print(f"尝试中{e}")
                    sleep_time = 1 * (2 ** attempt)
                    await asyncio.sleep(sleep_time)
                else:
                    answer = f"[回答失败] {e}"
        await asyncio.sleep(0.5)
        output_rows.append([row[0],question, answer])

    # 写入新 CSV
    with open(output_csv, 'w', encoding=encoding, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["seq", "question", "answer"])
        writer.writerows(output_rows)

    print(f"已完成 {len(rows)} 个问题的回答，结果保存至 {output_csv}")


if __name__ == "__main__":
    asyncio.run(answer_jailbreak_questions())