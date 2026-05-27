import csv
import asyncio
import os
from typing import List, Callable, Optional
from call_model import call_closed_model
from prompt import Multi_Turn_promptt
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "data")

async def rewrite_questions_again(
    fail_list:list,
    input_csv: str = os.path.join(_DATA_DIR, "score.csv"),
    output_csv: str = os.path.join(_DATA_DIR, "muti_questions.csv"),
    model_call_func: Callable[[str], str] = call_closed_model,
    encoding: str = "utf-8",
    has_header: bool = True
) -> None:
    rows = []
    with open(input_csv, 'r', encoding=encoding) as f:
        reader = csv.reader(f)
        if has_header:
            next(reader)
        for idx, row in enumerate(reader):
            if idx in fail_list:
                rows.append(row)

    output_rows = []
    output_header = ["seq","original_question", "new question"]

    for i,row in enumerate(rows):
        original_question = row[1].strip()

        prompt = [
            {"role": "system", "content": Multi_Turn_promptt},
            {"role": "user", "content": original_question}
        ]
        try:
            response = await model_call_func(provider='aliyun', model='deepseek-v4-flash', messages=prompt)
            cleaned = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip().strip('"').strip("'").strip()
        except Exception as e:
            print(f"error: {e}")
            cleaned = original_question
        output_rows.append([i,original_question, cleaned])

        if i >=50:
            break
    with open(output_csv, 'w', encoding=encoding, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(output_header)
        writer.writerows(output_rows)

