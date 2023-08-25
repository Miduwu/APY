from fastapi import APIRouter, Query, Response
from main import APYManager
from PIL import ImageFilter

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/blur",
    description="Apply a blur filter to your image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def blur(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png"),
    radius: int = Query(2, description="The radius for the blur", ge=1, le=10)
):
    final = await APYManager.open_image(image, param="image")
    return Response(content=APYManager.prepare(final.filter(ImageFilter.GaussianBlur(radius))), media_type="image/png")