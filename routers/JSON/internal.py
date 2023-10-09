from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from middle.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from difflib import get_close_matches
from main import APYManager

router = APIRouter(tags=["JSON"])

#@router.get("/", include_in_schema=False)
#async def home():
#    result = {}
#    routes = [x for x in APYManager.app.routes if "/json" in x.path or "/image" in x.path]
#    for route in routes:
#        prefix = route.path.split("/")[1]
#        result.setdefault(prefix, []).append(route.path)
#    result = {"base_url": "https://api.munlai.me", **result}
#    return HTTPResponse.use(data=result)

@router.get("/help",
    description="Search a doc specification about a route or a schema",
    response_model=HTTPResponse,
    responses=APYManager.get_responses())
async def help(
    query: str = Query(description="The route/schema name")
):
    spec = APYManager.get_openapi_spec()
    final = None
    for path, path_spec in spec["paths"].items():
        if query.lower() in path:
            final = spec["paths"][path]
    if final:
        return HTTPResponse.use(data=final)
    else:
        if "components" in spec:
            components = spec["components"]
            if "schemas" in components:
                schema_names = list(components["schemas"].keys())
                matches = get_close_matches(query, schema_names)
                if matches:
                    schema_name = matches[0]
                    final = components["schemas"][schema_name]
    if final is None:
        raise HTTPException(404,detail={"error": "Your query was not found", "loc": "query", "param_type": "query"})

@router.get("/docs", include_in_schema=False)
async def docs():
    return get_redoc_html(
        openapi_url=APYManager.app.openapi_url,
        title="APY Classic - Documentation",
        redoc_favicon_url="https://i.imgur.com/onn7Vbn.png",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

@router.get("/", include_in_schema=False)
async def launcher():
    return get_swagger_ui_html(
        openapi_url=APYManager.app.openapi_url,
        title=f"APY Classic - Launcher",
        swagger_favicon_url="https://i.imgur.com/onn7Vbn.png"
    )