from fastapi import APIRouter, Query, Response
from main import APYManager, LocalImagesManager
from PIL import Image

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/sus",
    description="Make a sus (among us) image your own image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def sus(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    avatar = (await APYManager.open_image(image, param="image")).resize((277, 277))
    overlay = LocalImagesManager.fetch("sus")
    base = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    base.paste(avatar, (210, 377 // 2), avatar)
    base.paste(overlay, (0, 0), overlay)

    return Response(content=APYManager.prepare(base), media_type="image/png")