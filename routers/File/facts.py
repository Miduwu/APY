from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager, LocalImagesManager
from PIL import Image, ImageDraw
from textwrap import fill

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/facts",
    description="Make a facts meme with your own text",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def facts(
    text: str = Query(description="The text for the image", max_lenght=100)
):
    font = TypeFaceManager.fetch("GGSans", "Medium", size=22)
    text = fill(text, 22)
    image = LocalImagesManager.fetch("facts").convert("RGBA")
    img = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask = ImageDraw.Draw(img)
    mask.text((75, 400), text, font=font, fill="Black")
    img = img.rotate(-15, resample=Image.BICUBIC)
    image.paste(img, (0, 0), img)

    return Response(content=APYManager.prepare(image), media_type="image/png")