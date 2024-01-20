from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager, LocalImagesManager
from textwrap import fill

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/twoways",
    description="Make a two ways meme with your own text",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def two_ways(
    text1: str = Query(description="The text1 for the image", max_lenght=150),
    text2: str = Query(description="The text2 for the image", max_lenght=150),
    text3: str = Query(description="The text3 for the image", max_lenght=150)
):
    font = TypeFaceManager.fetch("GGSans", "Bold", size=40)
    image = LocalImagesManager.fetch("twoways").convert("RGBA")
    metrics = APYManager.get_metrics(font, text1)
    await APYManager.draw_text(image, xy=((image.size[0] - metrics[0]) // 2, 475), text=text1, font=font, stroke_width=2, stroke_fill="Black")
    await APYManager.draw_text(image, xy=(110, 210), text=fill(text2, 20), fill="White", font=font, stroke_width=2, stroke_fill="Black")
    await APYManager.draw_text(image, xy=(485, 210), text=fill(text3, 12), fill="White", font=font, stroke_width=2, stroke_fill="Black")
    return Response(content=APYManager.prepare(image), media_type="image/png")