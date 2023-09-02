from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager, LocalImagesManager
from textwrap import fill

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/sonic",
    description="Make a sonic meme with your own text",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def sonic(
    text: str = Query(description="The text for the image", max_lenght=150)
):
    font = TypeFaceManager.fetch("GGSans", "Bold", size=18)
    text = fill(text, 50)
    image = LocalImagesManager.fetch("sonic").convert("RGBA")
    await APYManager.draw_text(image, xy=(366, 65), text=text, fill="White", font=font)

    return Response(content=APYManager.prepare(image), media_type="image/png")