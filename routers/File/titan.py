from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager, LocalImagesManager
from textwrap import fill

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/titan",
    description="Make a titan meme with your own text",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def titan(
    text1: str = Query(description="The text for the image", max_lenght=150),
    text2: str = Query(description="The text for the image", max_lenght=150)
):
    font = TypeFaceManager.fetch("GGSans", "Bold", size=50)
    font2 = TypeFaceManager.fetch("GGSans", "Bold", size=30)
    image = LocalImagesManager.fetch("titan").convert("RGBA")
    await APYManager.draw_text(image, xy=(360, 250), text=fill(text1, 12), fill="White", font=font, stroke_width=2, stroke_fill="Black")
    await APYManager.draw_text(image, xy=(160, 855), text=fill(text2, 20), fill="White", font=font2, stroke_width=2, stroke_fill="Black")
    return Response(content=APYManager.prepare(image), media_type="image/png")