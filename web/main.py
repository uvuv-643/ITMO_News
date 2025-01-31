import re
import time
from typing import List
from venv import logger

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import HttpUrl
from schemas.request import PredictionRequest, PredictionResponse
from utils.numbers.extractor import NumberExtractor
from yandex.parser import get_answer
from yandex.proxy import make_requests_to_yagpt

# Initialize
app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    body = await request.body()
    logger.info(
        f"Incoming request: {request.method} {request.url}\n"
        f"Request body: {body.decode()}"
    )

    response = await call_next(request)
    process_time = time.time() - start_time

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    logger.info(
        f"Request completed: {request.method} {request.url}\n"
        f"Status: {response.status_code}\n"
        f"Response body: {response_body.decode()}\n"
        f"Duration: {process_time:.3f}s"
    )

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


@app.post("/api/request", response_model=PredictionResponse)
async def predict(body: PredictionRequest):
    extractor = NumberExtractor()
    try:
        body_split = re.split(r'\\n|\r\n|\r|\n', body.query)
        logger.info(f"Processing prediction request with id: {body.id}")
        answers = []
        question_parts = []
        print(body_split)
        question_ended = False
        for x in body_split:
            print(x)
            if any(char.isdigit() for char in x) and len(question_parts) or question_ended:
                question_ended = True
                answers.append(extractor.replace_groups(re.sub(r'^\s*\d+\.\s*', '', x)))
            else:
                question_parts.append(extractor.replace_groups(x))

        response = get_answer(answers, await make_requests_to_yagpt("Университет ИТМО: " + ", ".join(question_parts)))
        answer = response.answer_index
        sources: List[HttpUrl] = list(map(lambda url: HttpUrl(url), response.sources))
        response = PredictionResponse(
            id=body.id,
            answer=answer,
            reasoning=response.reasoning,
            sources=sources,
        )
        logger.info(f"Successfully processed request {body.id}")
        return response
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Validation error for request {body.id}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Internal error processing request {body.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
