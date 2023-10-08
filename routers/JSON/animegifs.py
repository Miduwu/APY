from middle.schemas import HTTPResponse
from fastapi import APIRouter, Query
from main import APYManager
from typing import Literal
from random import choice
from static.gifs import Collection

router = APIRouter(prefix="/json", tags=["JSON"])

T = Literal["angry", "baka", "bite", "blush", "cry", "dance", "deredere", "happy", "hug", "kiss", "path", "punch", "slap", "sleep", "smug"]

@router.get("/animegifs",
    description="Get a random anime gif",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def anime_gifs(
    style: T = Query(description="The gif type")
):
    return HTTPResponse.use(data=choice(Collection.get(style.upper())))