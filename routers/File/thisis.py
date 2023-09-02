from fastapi import APIRouter, Query, Response
from main import APYManager, LocalImagesManager, TypeFaceManager
from PIL import Image, ImageDraw

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/thisis",
    description="Make a playlist image using your image and text",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def This_is(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png"),
    text: str = Query(description="The text for the image", max_lenght=100)
):
    img = await APYManager.open_image(image, param="image")
    img = APYManager.ellipse(img.resize((345, 345), Image.Resampling.LANCZOS))
    overlay = LocalImagesManager.fetch("thisis").convert("RGBA")
    await APYManager.draw_gradient(overlay, [(0, 217), (600, 700)], APYManager.get_dominant_colors(img, 2))
    overlay.paste(img, ((overlay.width - img.width) // 2, (overlay.height - img.height) // 2 + 78), img)
    font = TypeFaceManager.fetch("FranklinGothicDemi", size=25)
    W, H = APYManager.get_metrics(font, text)
    draw = ImageDraw.Draw(overlay)
    draw.text(((overlay.width - W) / 2, 115), text=text, font=font, fill="Black")
    return Response(content=APYManager.prepare(overlay), media_type="image/png")