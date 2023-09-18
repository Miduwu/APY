from middleware.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from main import APYManager

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/npm",
    description="Search for a package in npmjs.com",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def npm(
    query: str = Query(description="The package name (exact match)", max_length=150, min_length=1)
):
    res = await APYManager.request(method="GET", url=f"https://registry.npmjs.org/{query.lower().replace(' ', '-')}")
    if not res:
        raise HTTPException(404, { "error": "I was unable to find something related to that", "loc": "query", "param_type": "query"})
    return HTTPResponse.use(data=res)