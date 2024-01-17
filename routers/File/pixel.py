from fastapi import APIRouter, Query, Response
from main import APYManager

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/pixel",
    description="Apply a pixel filter to your image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def pixel(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png"),
    amount: int = Query(5, description="The pixelate level", ge=1, le=100)
):
    img = await APYManager.open_image(image, mode="RGB", param="image")
    org_size = img.size
    img = img.resize(size=(org_size[0] // amount, org_size[1] // amount), resample=0)
    img = img.resize(org_size, resample=0)

    return Response(content=APYManager.prepare(img), media_type="image/png")