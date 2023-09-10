from fastapi import APIRouter, Query, Response
from main import APYManager, LocalImagesManager

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/beautiful",
    description="Make a beautiful meme using your own image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def beautiful(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    avatar = (await APYManager.open_image(image, param="image")).resize((104, 106))
    base = LocalImagesManager.fetch("beautiful")
    base.paste(avatar, (252, 25), avatar)
    base.paste(avatar, (252, 225), avatar)

    return Response(content=APYManager.prepare(base), media_type="image/png")