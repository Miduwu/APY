from fastapi import APIRouter, Query, Response
from main import APYManager, LocalImagesManager
from PIL import Image

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/simp",
    description="Apply a simp filter to your image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def simp(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    img = await APYManager.open_image(image, param="image")
    overlay = LocalImagesManager.fetch("simp").resize(img.size, Image.Resampling.LANCZOS)
    img.paste(overlay, (0, 0), overlay)
    return Response(content=APYManager.prepare(img), media_type="image/png")