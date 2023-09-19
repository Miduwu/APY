from middle.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from main import APYManager
from typing import Literal

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/github",
    description="Search for a github user/repo information",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def github(
    query: str = Query(description="The query to search in github", max_length=150, min_length=1),
    type: Literal["user", "repo"] = Query("repo", description="The type of data to search")
):
    if type == "repo":
        url = f"https://api.github.com/search/repositories?q={query}&page=1&per_page=1"
        func = lambda x: not x or not "items" in x or not len(x["items"])
    else:
        url = f"https://api.github.com/users/{query}"
        func = lambda x: not x or "login" not in x
    res = await APYManager.request(method="GET", url=url)
    if not res or func(res):
        raise HTTPException(404, { "error": "I was unable to find something related to that", "loc": "query", "param_type": "query"})
    return HTTPResponse.use(data=res["items"][0] if type == "repo" else res)