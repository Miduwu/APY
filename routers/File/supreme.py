from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager
from PIL import Image, ImageDraw

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/supreme",
    description="Make a supreme-like logo with your own image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def supreme(
    text: str = Query(description="The text for the image", max_lenght=55)
):
    font = TypeFaceManager.fetch("HelveticaNow", size=60)
    W, H = APYManager.get_metrics(font, text)
    image = Image.new("RGBA", (W + 30, H + 20))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, image.width, image.height), 10, fill="Red")
    draw.text((15, 7.5), text, font=font, fill="White")

    return Response(content=APYManager.prepare(image), media_type="image/png")