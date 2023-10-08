from fastapi import APIRouter, Query, Response
from main import APYManager, LocalImagesManager
from PIL import Image

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/mad",
    description="Make a mad image your own image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def mad(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    avatar = (await APYManager.open_image(image, param="image")).resize((180, 144))
    overlay = LocalImagesManager.fetch("mad")
    base = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    base.paste(avatar, (220, 147), avatar)
    base.paste(overlay, (0, 0), overlay)

    return Response(content=APYManager.prepare(base), media_type="image/png")