from fastapi import FastAPI,Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from config import SYSTEM_PROMT,API_KEY,BASE_URL,MODEL
from pydantic import BaseModel, ValidationError
from fastapi.responses import RedirectResponse
import re
import json
from openai import AsyncOpenAI, APIError,APIConnectionError,RateLimitError
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class AIRequest(BaseModel):
    prompt: str

class Ingredient(BaseModel):
    name: str
    quantity: str | None = None

class Recipe(BaseModel):
    title: str
    description: str
    time_minutes: int
    servings: int
    difficulty: str
    ingredients: list[Ingredient]
    steps: list[str]
    tips: str | None = None

client = AsyncOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
)
@app.get("/")
async def root():
    return RedirectResponse(url="/base")
@app.get("/base")
async def tasks(request: Request):
    return templates.TemplateResponse(request,"base.html")

@app.post("/products/ai/")
async def ai(request: AIRequest):

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMT},
                {"role": "user", "content": request.prompt},
            ],
            response_format = {"type": "json_object"}
        )
    except RateLimitError:
        raise HTTPException(429, "Слишком много запросов. Подождите минуту.")
    except APIConnectionError:
        raise HTTPException(504, "Не удалось подключиться к AI. Проверьте интернет.")
    except APIError as e:
        raise HTTPException(502, f"Ошибка AI: {e}")

    content = response.choices[0].message.content

    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
    content = re.sub(r"<reasoning>.*?</reasoning>", "", content, flags=re.DOTALL)
    content = re.sub(r"^```(?:json)?\s*", "", content.strip())
    content = re.sub(r"\s*```$", "", content.strip())
    content = content.strip()
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(502, f"Модель вернула невалидный JSON: {e}")

    try:
        recipe = Recipe.model_validate(parsed)
    except ValidationError as e:
        raise HTTPException(502, f"Схема рецепта не совпала: {e}")
    return recipe





