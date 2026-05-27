import os
import re
import sys
import csv
import random
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.model_factory import Model, ModelConfig
from scripts.rewrite import rewrite_questions
from scripts.answer_jailbreak_questions import answer_jailbreak_questions
from scripts.Multi_Turn import rewrite_questions_again
from eval.score import score_eval
from config.config import load_config
from scripts.open_source import load_model_and_tokenizer, answer_with_local_model, score_eval_local

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
config = load_config(os.path.join(BASE, "config", "Close.yaml"))

INPUT_CSV = os.path.join(DATA, "harmful.csv")
OUTPUT_CSV = os.path.join(DATA, "rewrite.csv")
ANSWER_CSV = os.path.join(DATA, "answer.csv")
SCORE_CSV = os.path.join(DATA, "score.csv")
SCORE2_CSV = os.path.join(DATA, "score2.csv")
MUTI_CSV = os.path.join(DATA, "muti_questions.csv")

async def main():
    await rewrite_questions(input_csv=INPUT_CSV, output_csv=OUTPUT_CSV)
    if config.open_source == False:
        await answer_jailbreak_questions
        asr,fail_list = await score_eval(input_csv=OUTPUT_CSV, output_csv=SCORE_CSV)
        if asr < 0.9:
            rewrite_questions_again(fail_list=fail_list)
        asr,fail_list = await score_eval(input_csv=MUTI_CSV, output_csv=SCORE2_CSV)
        print(f'asr={asr}%')
        print(f'fail={fail_list}')
    else:
        model_path_dicts = {"llama2": "./models/llama2/llama-2-7b-chat-hf", "vicuna": "./models/vicuna/vicuna-7b-v1.3",
                        "guanaco": "./models/guanaco/guanaco-7B-HF", "WizardLM": "./models/WizardLM/WizardLM-7B-V1.0",
                        "mpt-chat": "./models/mpt/mpt-7b-chat", "mpt-instruct": "./models/mpt/mpt-7b-instruct",
                        "falcon": "./models/falcon/falcon-7b-instruct"}
        model_path = model_path_dicts[config.model]
        model, tokenizer = load_model_and_tokenizer(model_path, low_cpu_mem_usage=True, use_cache=False, device=config.device)
        await answer_with_local_model(model, tokenizer, input_csv=OUTPUT_CSV, output_csv=ANSWER_CSV)
        asr, fail_list = await score_eval_local(model, tokenizer, input_csv=ANSWER_CSV, output_csv=SCORE_CSV)
        if asr < 0.9:
            rewrite_questions_again(fail_list=fail_list)
        asr,fail_list = await score_eval_local(model, tokenizer, input_csv=ANSWER_CSV, output_csv=SCORE2_CSV)
        print(f'asr={asr}%')
        print(f'fail={fail_list}')

if __name__ == "__main__":
    asyncio.run(main())
