from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager, LocalImagesManager
from PIL import Image, ImageDraw, ImageFilter

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/welcomecard",
    description="Make a welcomecard using your own data",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def welcome_card(
    image: str = Query(description="The avatar URL", example="https://images.com/myimage.png"),
    title: str = Query("Welcome", description="The title for the card", max_length=80),
    subtitle: str = Query("Enjoy your stay!", description="The subtitle for the card", max_lenght=100),
    background: str = Query(None, description="The background for the card"),
    blur: bool = Query(True, description="If the card background must have a blur filter")
):
    avatar = await APYManager.open_image(image, param="image")
    image = Image.new("RGBA", (1024, 500), (0, 0, 0, 255))
    colors = APYManager.get_dominant_colors(avatar)
    if background:
        background = await APYManager.open_image(background, param="background").resize(image.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur([0, 10][blur]))
        image.paste(background, (0, 0), background)
    else:
        await APYManager.draw_gradient(image, [(0, 0), (2048, 500)], colors)
    avatar = APYManager.ellipse(avatar).resize((220, 220))
    mask = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((45, 45, 1024 - 45, 500 - 45), 20, fill=(0, 0, 0, 200))
    image = Image.alpha_composite(image, mask)
    image.paste(avatar, ((image.width - avatar.width) // 2, 65), avatar)

    font = TypeFaceManager.fetch("SuperCorn", size=65)
    font2 = TypeFaceManager.fetch("FranklinGothicDemi", size=33)
    X, Y = APYManager.get_metrics(font, title)
    X1, Y1 = APYManager.get_metrics(font2, subtitle)
    await APYManager.draw_text(image, xy=((image.width - X) // 2, 295), text=title, font=font)
    await APYManager.draw_text(image, xy=((image.width - X1) // 2, 360), text=subtitle, font=font2)

    return Response(content=APYManager.prepare(image), media_type="image/png")