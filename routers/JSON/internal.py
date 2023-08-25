from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from middleware.schemas import HTTPResponse
from fastapi import APIRouter
from main import apy

router = APIRouter()

@router.get("/", include_in_schema=False)
async def home():
    result = {}
    routes = [x for x in apy.routes if "/json" in x.path or "/image" in x.path]
    for route in routes:
        prefix = route.path.split("/")[1]
        result.setdefault(prefix, []).append(route.path)
    result = {"base_url": "https://api.munlai.me", **result}
    return HTTPResponse.use(status=200, data=result)

@router.get("/docs", include_in_schema=False)
async def docs():
    return get_redoc_html(
        openapi_url=apy.openapi_url,
        title="APY Classic - Documentation",
        redoc_favicon_url="https://i.imgur.com/onn7Vbn.png",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

@router.get("/launcher", include_in_schema=False)
async def launcher():
    return get_swagger_ui_html(
        openapi_url=apy.openapi_url,
        title=f"APY Classic - Launcher",
        swagger_favicon_url="https://i.imgur.com/onn7Vbn.png"
    )