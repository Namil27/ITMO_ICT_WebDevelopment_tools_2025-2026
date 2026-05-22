import aiohttp
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl


class ParseRequest(BaseModel):
    url: HttpUrl


class ParseResponse(BaseModel):
    url: HttpUrl
    title: str


app = FastAPI(
    title="Parser Service",
    description="Сервис парсинга страниц для лабораторной работы 3.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Parser service is running"}


@app.post("/parse", response_model=ParseResponse)
async def parse_page(request: ParseRequest):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(str(request.url), timeout=10) as response:
                response.raise_for_status()
                html = await response.text()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to load page: {exc}",
        ) from exc

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title"

    return ParseResponse(url=request.url, title=title)
