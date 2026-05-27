import os
import csv
import ast
import asyncio
from typing import Callable
from call_model import call_closed_model

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "data")


async def sequential_ask(
    input_csv: str = os.path.join(_DATA_DIR, "multi_questions.csv"),
    output_csv: str = os.path.join(_DATA_DIR, "sequential_answers.csv"),
    model_call_func: Callable = call_closed_model,
    encoding: str = "utf-8",
    has_header: bool = False,
    model: str = None

) -> None:
    rows = []
    with open(input_csv, "r", encoding=encoding) as f:
        reader = csv.reader(f)
        if has_header:
            next(reader)
        for row in reader:
            rows.append(row)

    output_rows = []
    for idx, row in enumerate(rows):

        first_question = row[0].strip()
        second_question = row[1].strip()

        for attempt in range(3):
            try:
                messages = [
                    {"role": "user", "content": first_question},
                ]
                first_raw = await model_call_func(messages, temperature=0.7)
                if isinstance(first_raw, dict) and "choices" in first_raw:
                    first_answer = first_raw["choices"][0]["message"]["content"]
                elif isinstance(first_raw, str):
                    first_answer = first_raw
                else:
                    first_answer = f"[error] {first_raw.get('error')}"
                first_answer = first_answer.strip()
                break
            except Exception as e:
                if attempt < 2:
                    print(f"error: {e}")
                    await asyncio.sleep(1 * (2**attempt))
                else:
                    first_answer = f"[error] {e}"

        for attempt in range(3):
            try:
                messages = [
                    {"role": "user", "content": first_question},
                    {"role": "assistant", "content": first_answer},
                    {"role": "user", "content": second_question},
                ]
                second_raw = await model_call_func(messages, temperature=0.7)
                if isinstance(second_raw, dict) and "choices" in second_raw:
                    second_answer = second_raw["choices"][0]["message"]["content"]
                elif isinstance(second_raw, str):
                    second_answer = second_raw
                else:
                    second_answer = f"[error] {second_raw.get('error')}"
                second_answer = second_answer.strip()
                break
            except Exception as e:
                if attempt < 2:
                    print(f"error:{e}")
                    await asyncio.sleep(1 * (2**attempt))
                else:
                    second_answer = f" {e}"

        await asyncio.sleep(0.5)
        output_rows.append([idx, second_answer])
    with open(output_csv, "w", encoding=encoding, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["seq", "first_question", "second_question", "second_answer"])
        writer.writerows(output_rows)

