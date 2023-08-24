from middleware.schemas import HTTPResponse
from fastapi import APIRouter
from main import apy

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/", include_in_schema=False)
async def home():
    result = {}
    routes = [x for x in apy.routes if "/json" in x.path or "/image" in x.path]
    for route in routes:
        prefix = route.path.split("/")[1]
        result.setdefault(prefix, []).append(route.path)
    base_url = "https://api.munlai.me"
    result = {"base_url": base_url, **result}
    return HTTPResponse.use(status=200, data=result)