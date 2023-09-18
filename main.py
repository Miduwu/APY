# Import useful modules
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from middleware.schemas import HTTPBadResponse
from middleware.FontsManager import TypefaceManager
from middleware.ImagesManager import LocalImagesManager
from uvicorn import Config, run
from middleware.APYManager import Util
from os import getenv
from json import loads

apy = FastAPI(
    title="APY",
    description="A powerful image generation & JSON response API written in Python.",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    debug=False
)

APYManager = Util(apy)

TypeFaceManager = TypefaceManager("static/fonts")
LocalImagesManager = LocalImagesManager("static/assets")

@apy.on_event("startup")
async def startup():
    print("¡APY IS ONLINE!")
    await APYManager._load_routes()
    await APYManager._load_programming_languages()

@apy.exception_handler(RequestValidationError)
@apy.exception_handler(422)
async def handle_validation_error(req: Request, exception: RequestValidationError | HTTPException):
    error_detail = loads(exception.json())[0] if hasattr(exception, "json") else exception.detail
    parameter, location = error_detail.get("loc", [None, None])
    status_code = exception.status_code if hasattr(exception, "status_code") else 422
    error_message = error_detail.get("msg", "Unknown error").title()
    
    return HTTPBadResponse.use(
        status=status_code,
        data={"error": error_message, "loc": location, "param_type": parameter}
    )

@apy.exception_handler(405)
@apy.exception_handler(400)
@apy.exception_handler(404)
async def handle_bad_request_error(request: Request, exception: HTTPException):
    return HTTPBadResponse.use(status=exception.status_code, data=exception.detail)

@apy.exception_handler(500)
async def handle_internal_error(request: Request, exception: HTTPException):
    return HTTPBadResponse.use(
        status=500,
        data={"error": "Internal server error", "loc": None, "param_type": None}
    )

Config(apy)

if __name__ == "__main__":
    run("main:apy", port=getenv("PORT") or 3000, host="0.0.0.0", reload=True)