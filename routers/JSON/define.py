from middle.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from main import APYManager

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/define",
    description="Define a term using the urban dictionary",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def npm(
    query: str = Query(description="The term to define", max_length=500, min_length=1),
    limit: int = Query(5, description="The limit of results", ge=1, le=10)
):
    res = await APYManager.request(method="GET", url="https://api.urbandictionary.com/v0/define", params={"term": query})
    if not res or not res["list"]:
        raise HTTPException(404, { "error": "I was unable to find something related to that", "loc": "query", "param_type": "query"})
    return HTTPResponse.use(data=res["list"][0:limit])