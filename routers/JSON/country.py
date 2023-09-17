from middleware.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from main import APYManager

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/country",
    description="Search for a country data",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def country(
    query: str = Query(description="The country exact name", max_length=150, min_length=1, example="Mexico")
):
    try:
        r = await APYManager.request(method="GET", url=f"https://restcountries.com/v3.1/name/{query}")
        if not r:
            raise HTTPException(404, { "error": "I was unable to find something related to that", "loc": "query", "param_type": "query"})
        return HTTPResponse.use(data=r[0])
    except:
        raise HTTPException(404, { "error": "I was unable to find something related to that", "loc": "query", "param_type": "query"})