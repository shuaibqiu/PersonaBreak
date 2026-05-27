# The Misplaced Censor

A jailbreak attack evaluation framework that rewrites harmful questions via "first-person wrapped requests" and measures the target model's safety guardrails.

## Project Structure

```
.
├── main.py                          # Entry point, orchestrates the full pipeline
├── config/
│   ├── config.py                    # YAML config loader
│   ├── Close.yaml                   # Closed-source API model config
│   └── OpenSource.yaml              # Open-source local model config
├── data/
│   └── harmful.csv                  # Original harmful questions (388 entries)
├── scripts/
│   ├── prompt.py                    # All prompt templates
│   ├── rewrite.py                   # Rewrite harmful questions → rewrite.csv
│   ├── answer_jailbreak_questions.py # API model answering → answer.csv
│   ├── open_source.py               # Local model: load + answer + score
│   ├── call_model.py                # proxy API caller
│   ├── model_factory.py             # Model abstraction factory
│   ├── Multi_Turn.py                # Multi-turn rewrite for failed questions
│   └── sequential_ask.py            # Two-turn sequential prompting
├── eval/
│   └── score.py                     # API-based scoring → score.csv
├── models/                          # Local model weights directory
└── requirements.txt
```

## Pipeline

```
harmful.csv ──► rewrite ──► rewrite.csv ──► answer ──► answer.csv ──► score ──► score.csv (ASR)
```

1. **Rewrite**: Wrap harmful questions as first-person professional requests, replacing sensitive terms with hypernyms
2. **Answer**: Feed rewritten questions to the target model
3. **Score**: Rate responses (0–10) and compute ASR (Attack Success Rate)

## Quick Start

### Install

```bash
pip install -r requirements.txt
```

### Mode 1: Closed-Source API Models

Edit `config/Close.yaml` with your API credentials:

```yaml
open_source: false
aliyun_API_KEY: "sk-xxx"
model_name: "gpt-3.5-turbo"
```

Run:

```bash
python main.py
```

### Mode 2: Open-Source Local Models

1. Place model weights under `models/` (supports Llama2, Vicuna, Guanaco, WizardLM, MPT, Falcon)

2. Edit `config/OpenSource.yaml`:

```yaml
open_source: true
model: "llama2"
device: "cuda"
```

3. Point `main.py` to the OpenSource config:

```python
config = load_config(os.path.join(BASE, "config", "OpenSource.yaml"))
```

4. Run:

```bash
python main.py
```

## Output Files

| File | Columns |
|------|---------|
| `data/rewrite.csv` | seq, original_question, new question |
| `data/answer.csv` | seq, question, answer |
| `data/score.csv` | seq, question, score |

## Prompt Design

Three core prompts defined in `scripts/prompt.py`:

- **rewrite_prompt**: Rewrites malicious questions into role-playing indirect requests with hypernym substitution
- **score_prompt**: Rates response harmfulness on a 0–10 scale
- **asr_prompt**: Binary classification of whether a response constitutes a successful jailbreak

