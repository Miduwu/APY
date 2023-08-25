from fastapi import APIRouter, Query, Response
from main import APYManager
from PIL import ImageOps

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/mirror",
    description="Apply a mirror effect to your image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def gray_scale(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    image = await APYManager.open_image(image, mode="RGB", param="image")
    
    return Response(content=APYManager.prepare(ImageOps.mirror(image)), media_type="image/png")