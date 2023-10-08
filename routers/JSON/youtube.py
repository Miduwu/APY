from middle.schemas import HTTPResponse
from middle.YoutubeCrawler import search
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from main import APYManager

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/youtube",
    description="Search for a youtube video",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def YouTube_video(
    query: str = Query(description="A youtube video title", min_length=2, max_length=150),
    limit: int = Query(1, description="The limit of results to show", ge=1, le=20)
):
    try:
        res = await search(APYManager, query)
        videos = res.videos if res else None
        if not videos or not len(videos):
            raise Exception("")
        videos = [v.get_properties() for v in videos]
        return HTTPResponse.use(data=videos[:limit])
    except:
        raise HTTPException(404, { "error": "I was unable to find something related to that", "loc": "query", "param_type": "query"})