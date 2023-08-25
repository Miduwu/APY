from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager, LocalImagesManager
from PIL import Image, ImageDraw
from textwrap import fill

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/badnews",
    description="Make a bad news meme with your own text",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def supreme(
    text: str = Query(description="The text for the image", max_lenght=130)
):
    font = TypeFaceManager.fetch("FranklinGothicDemi", size=32)
    overlay = LocalImagesManager.fetch("gru")
    text = fill(text, 22)
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.text((60, 15), "guys i have bad news", font=font, fill="White", stroke_fill="Black", stroke_width=2)
    W, H = APYManager.get_metrics(font, text)
    pos = ((overlay.width - W) / 2, ((overlay.height - H) - 20))
    draw.text(pos, text, font=font, fill="White", stroke_fill="Black", stroke_width=2)

    return Response(content=APYManager.prepare(overlay), media_type="image/png")