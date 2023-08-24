import re
from middleware.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from main import APYManager

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/imagesearch",
    description="Search for images in bing",
    response_model=HTTPResponse
)
async def bing_images(
    query: str = Query(description="The query to search in bing", max_length=150, min_length=1)
):
    res = await APYManager.request(method="GET", url="https://www.bing.com/images/async", params={ "q": query, "adlt": "on" }, get="bytes")
    if not res:
        raise HTTPException(404, { "error": "I was unable to find something related to that", "loc": "query", "param_type": "query"})
    urls = re.findall("murl&quot;:&quot;(.*?)&quot;", res.decode("utf8"))
    return HTTPResponse.use(status=200, data=list(urls))