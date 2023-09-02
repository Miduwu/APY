from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager, LocalImagesManager
from PIL import Image, ImageDraw

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/discordjs",
    description="Make a discordjs-like logo with your own image",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def discordjs(
    text: str = Query(description="The text for the image", max_lenght=55)
):
    font = TypeFaceManager.fetch("FranklinGothicDemi", size=85)
    overlay = LocalImagesManager.fetch("js").resize((165, 165), Image.Resampling.LANCZOS)
    W, H = APYManager.get_metrics(font, text.upper())
    image = Image.new("RGBA", (W + 150, H + 100))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, image.width, image.height), 10, fill="#090A16")
    await APYManager.draw_text(image, xy=(30, H / 1.9), text=text.upper(), font=font, fill="White", align="center")
    image.paste(overlay, (W - 24, H // 4 - 12), overlay)

    return Response(content=APYManager.prepare(image), media_type="image/png")