from fastapi import APIRouter, Query, Response
from main import APYManager
from PIL import ImageEnhance

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/deepfry",
    description="Apply a deepfry filter to your image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def blur(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png"),
    amount: int = Query(2, description="The amount of contrast for the filter", ge=1, le=10)
):
    final = await APYManager.open_image(image, param="image")
    return Response(content=APYManager.prepare(ImageEnhance.Contrast(final).enhance(amount)), media_type="image/png")