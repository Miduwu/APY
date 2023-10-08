from fastapi import APIRouter, Query, Response
from main import APYManager, LocalImagesManager
from PIL import Image

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/whoreallyare",
    description="Make a whoreallyare image your own image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def whoreally(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    avatar = APYManager.ellipse((await APYManager.open_image(image, param="image"))).resize((190, 190), Image.Resampling.LANCZOS)
    overlay = LocalImagesManager.fetch("whoreally")
    overlay.paste(avatar, (68, 580), avatar)

    return Response(content=APYManager.prepare(overlay), media_type="image/png")