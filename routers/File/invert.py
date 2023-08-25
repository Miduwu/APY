from fastapi import APIRouter, Query, Response
from main import APYManager
from PIL import ImageOps

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/invert",
    description="Apply an invert filter to your image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def invert(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    image = await APYManager.open_image(image, mode="RGB", param="image")

    return Response(content=APYManager.prepare(ImageOps.invert(image)), media_type="image/png")