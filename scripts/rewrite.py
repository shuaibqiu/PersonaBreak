import csv
import asyncio
from typing import List, Callable, Optional
from call_model import call_closed_model
from prompt import rewrite_prompt

async def rewrite_questions(
    input_csv: str,
    output_csv: str,
    model_call_func: Callable[[str], str] = call_closed_model,
    encoding: str = "utf-8",
    has_header: bool = False,
    model: str = None
) -> None:
    with open(input_csv, 'r', encoding=encoding) as f:
        reader = csv.reader(f)
        if has_header:
            next(reader)
        rows = [row for row in reader]

    output_rows = []
    output_header = ["seq","original_question", "new question"]

    for i,row in enumerate(rows):
        original_question = row[0].strip()

        prompt = [
            {"role": "system", "content": rewrite_prompt},
            {"role": "user", "content": original_question}
        ]
        try:
            response = await model_call_func(messages=prompt)
            cleaned = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip().strip('"').strip("'").strip()
        except Exception as e:
            print(f"error: {e}")
            cleaned = original_question
        output_rows.append([i,original_question, cleaned])

        # if i >=50:
        #     break
    with open(output_csv, 'w', encoding=encoding, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(output_header)
        writer.writerows(output_rows)

