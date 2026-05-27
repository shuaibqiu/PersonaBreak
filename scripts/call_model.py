import os
import asyncio
import httpx
from typing import Optional, Dict, Any, List

async def call_closed_model(
    messages: List[Dict[str, str]],
    provider: str = 'aliyun',
    model: str = '',
    api_key: Optional[str] = '',
    temperature: float = 0.7,
    max_tokens: int = 1024,
    top_p: float = 1.0,
    stop: Optional[List[str]] = None,
    additional_params: Optional[Dict[str, Any]] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> Dict[str, Any]:

    provider = provider.lower()
    if provider == "aliyun":
        api_key = api_key or os.getenv('aliyun_API_KEY') 
        url = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
    elif provider == "foreign model":
        api_key = api_key
        url = ''
    else:
        return {'error': f'Unsupported provider: {provider}'}

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': model,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        # 'top_p': top_p,
        # 'stop': stop,
    }

    if additional_params:
        payload.update(additional_params)
    payload = {k: v for k, v in payload.items() if v is not None}

    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 429 or response.status_code >= 500:
                    error_msg = response.json().get('error', {}).get('message', response.text)
                    if attempt < max_retries:
                        sleep_time = retry_delay * (2 ** (attempt - 1))
                        await asyncio.sleep(sleep_time)
                        continue
                    else:
                        return {
                            'error': f'API error after {max_retries} retries: {error_msg}',
                            'status_code': response.status_code,
                        }
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    return {'error': f'Request failed after {max_retries} retries: {str(e)}'}

    return {'error': 'Unexpected flow'}

