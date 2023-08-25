from fastapi import APIRouter, Query, Response
from main import APYManager, LocalImagesManager

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/communist",
    description="Apply a communist filter to your image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def communist(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    img = await APYManager.open_image(image, param="image")
    overlay = LocalImagesManager.fetch("communism").resize(img.size)
    img.paste(overlay, (0, 0), overlay)
    return Response(content=APYManager.prepare(img), media_type="image/png")