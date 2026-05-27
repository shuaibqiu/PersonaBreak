import os
import yaml
from pathlib import Path
from types import SimpleNamespace
def dict_to_namespace(d):
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = dict_to_namespace(value)
            elif isinstance(value, list):
                d[key] = [dict_to_namespace(item) if isinstance(item, dict) else item for item in value]
        return SimpleNamespace(**d)
    return d

def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    config=dict_to_namespace(config)
    return config