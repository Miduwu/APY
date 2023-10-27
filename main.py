# Import useful modules
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from middle.schemas import HTTPBadResponse
from middle.FontsManager import TypefaceManager
from middle.ImagesManager import LocalImagesManager
from middle.APYManager import Util
from os import getenv
from json import loads
from hypercorn.config import Config
from hypercorn.asyncio import serve
from asyncio import run
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

apy = FastAPI(
    title="APY",
    description="A powerful image generation & JSON response API written in Python.",
    version="2.2.1",
    docs_url=None,
    redoc_url=None,
    debug=False
)

APYManager = Util(apy)

config = Config()
config.bind = [f"0.0.0.0:{getenv('PORT') or 3000}"]

TypeFaceManager = TypefaceManager("static/fonts")
LocalImagesManager = LocalImagesManager("static/assets")

@apy.middleware("https")
async def call_next(req: Request, call_next):
    start_time = datetime.now()
    response = await call_next(req)
    end_time = datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()
    webhook = getenv("WEBHOOK")
    embed = {
        "title": "API Request",
        "description": "```"+str(req.url).replace("https://", "")+"```",
        "color": 3447003,
        "fields": [
            {"name": "Method", "value": req.method, "inline": True},
            {"name": "Time", "value": str(round(elapsed_time, 3))+"s", "inline": True},
            {"name": "Status", "value": str(response.status_code) + " :warning:" if response.status_code == 500 else str(response.status_code), "inline": True}
        ],
        "footer": {"text": req.client.host, "icon": {"url": "https://i.imgur.com/onn7Vbn.png"}}
    }
    try:
        if webhook:
            await APYManager.request(method="POST", url=webhook, json={"embeds": [embed]})
        return response
    except:
        return response

@apy.on_event("startup")
async def startup():
    print("¡APY IS ONLINE!")

@apy.exception_handler(RequestValidationError)
@apy.exception_handler(422)
async def handle_validation_error(req: Request, exception: RequestValidationError | HTTPException):
    error_detail = loads(exception.json())[0] if hasattr(exception, "json") else exception.detail
    parameter, location = error_detail.get("loc", [None, None])
    status_code = exception.status_code if hasattr(exception, "status_code") else 422
    error_message = error_detail.get("msg", "Unknown error")
    
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

async def main():
    await APYManager._load_routes()

    await serve(apy, config)

if __name__ == "__main__":
    run(main())
    # run("main:apy", port=getenv("PORT") or 3000, host="0.0.0.0", reload=True)