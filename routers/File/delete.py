from fastapi import APIRouter, Query, Response
from main import APYManager, LocalImagesManager

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/delete",
    description="Make a delete trash meme using your own image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def delete(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    avatar = (await APYManager.open_image(image, param="image")).resize((180, 180))
    base = LocalImagesManager.fetch("delete")
    base.paste(avatar, (135, 135), avatar)

    return Response(content=APYManager.prepare(base), media_type="image/png")