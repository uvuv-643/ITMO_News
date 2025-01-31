from __future__ import print_function

import asyncio
import os
import re
from typing import Any, List

import aiohttp
from dotenv import load_dotenv

from utils.numbers.extractor import NumberExtractor
from yandex.models import ResponseYaGpt, ResponseSource
from yandex.parser import get_answer


async def get_response_from_ya_gpt(question: str, website: str) -> Any | None:
  load_dotenv()
  API_KEY = os.environ.get("API_KEY")
  YA_GPT_URL = os.environ.get("YA_GPT_URL")
  payload = {
    "messages": [
      {
        "role": "user",
        "content": question
      }
    ],
    "site": website
  }
  headers = {'Authorization': f'Api-Key {API_KEY}'}
  try:
    async with aiohttp.ClientSession() as session:
      async with session.post(YA_GPT_URL, json=payload, headers=headers) as response:
        response.raise_for_status()
        data = await response.json()
        return data
  except:
    return None


async def make_requests_to_yagpt(question: str) -> List[ResponseYaGpt]:
  result = []
  try:
    website_pool = ['itmo.ru', 'minobrnauki.gov.ru', 'sobaka.ru', 'tass.ru']
    tasks = list(map(lambda x: get_response_from_ya_gpt(question, x), website_pool))
    responses = await asyncio.gather(*tasks)
    responses = list(filter(lambda r: not (r is None or 'message' not in r or 'content' not in r['message'] or 'не найдено' in r['message']['content']), responses))
    for idx, response in enumerate(responses):
      try:
        answer = response['message']['content']
        extractor = NumberExtractor()
        answer = extractor.replace_groups(answer)
        answer_without_sources = re.sub(r'\[\d+]', '', answer)
        sources = []
        if 'used_sources' in response:
          sources = [ResponseSource(index=k, title=v["title"], url=v["url"]) for k, v in response['used_sources'].items()]
        result.append(ResponseYaGpt(answer, sources, answer_without_sources, idx == 0))
      except:
        pass

  except:
    pass
  print(result)
  return result
