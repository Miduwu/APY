from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager, LocalImagesManager
from PIL import Image, ImageDraw
from textwrap import fill

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/santa",
    description="Make a santa meme with your own text",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def santa(
    text: str = Query(description="The text for the image", max_lenght=100)
):
    font = TypeFaceManager.fetch("GGSans", "Medium", size=13)
    text = fill(text, 17)
    image = LocalImagesManager.fetch("santa").convert("RGBA")
    img = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask = ImageDraw.Draw(img)
    mask.text((20, 140), text, font=font, align="center", fill="Black")
    img = img.rotate(10, resample=Image.BICUBIC)
    image.paste(img, (0, 0), img)

    return Response(content=APYManager.prepare(image), media_type="image/png")