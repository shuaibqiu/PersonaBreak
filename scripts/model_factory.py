from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from call_model import call_closed_model


@dataclass
class ModelConfig:
    name: str
    provider: str = "aliyun"
    model: str = "deepseek-v4-flash"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 1.0
    extra: Dict[str, Any] = field(default_factory=dict)


class Model:
    def __init__(self, config: ModelConfig):
        self.config = config

    async def call(self, messages: List[Dict[str, str]], **overrides) -> Dict[str, Any]:
        kw = {**{k: getattr(self.config, k) for k in ("provider", "model", "api_key", "temperature", "max_tokens", "top_p")}, **self.config.extra, **overrides}
        raw = await call_closed_model(messages=messages, **kw)
        return {"model": self.config.name, "raw": raw, "text": raw.get("choices", [{}])[0].get("message", {}).get("content", "")}


class ModelFactory:
    def __init__(self, configs: Optional[List[ModelConfig]] = None):
        self._models: Dict[str, Model] = {}
        if configs:
            for c in configs:
                self._models[c.name] = Model(c)

    def add(self, config: ModelConfig):
        self._models[config.name] = Model(config)

    def get(self, name: str) -> Optional[Model]:
        return self._models.get(name)

    async def call(self, name: str, messages: List[Dict[str, str]], **overrides) -> Dict[str, Any]:
        return await self._models[name].call(messages, **overrides)
