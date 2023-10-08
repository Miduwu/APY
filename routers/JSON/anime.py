from middle.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from main import APYManager
from typing import Literal

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/anime",
    description="Get an anime/manga title information",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def anime_or_manga_search(
    type: Literal["anime", "manga"] = Query("anime", description="The type of search"),
    query: str = Query(description="The anime/manga title to search", example="nanatsu no taizai"),
    limit: int = Query(1, description="The limit of results to show", ge=1, le=10)
):
    URL = f"https://kitsu.io/api/edge/{type}?filter[text]={query}&page[offset]=0"
    res = await APYManager.request(method="GET", url=URL)
    if not res or not res["data"] or not len(res["data"]):
        raise HTTPException(404, { "error": "I was unable to find something related to that", "loc": "query", "param_type": "query"})
    return HTTPResponse.use(data=res["data"][:limit])