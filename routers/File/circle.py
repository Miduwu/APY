from fastapi import APIRouter, Query, Response
from main import APYManager

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/circle",
    description="Apply a circle cut to your image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def circlify(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png")
):
    image = await APYManager.open_image(image, param="image")
    final = APYManager.ellipse(image)

    return Response(content=APYManager.prepare(final), media_type="image/png")