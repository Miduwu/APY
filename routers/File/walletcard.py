from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager, LocalImagesManager
from PIL import Image, ImageDraw, ImageFilter

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/walletcard",
    description="Make a facts meme with your own text",
    response_class=Response,
    responses=APYManager.get_responses(image=True)           
)
async def wallet_card(
    image: str = Query(description="The image URL", example="https://images.com/myimage.png"),
    username: str = Query(description="The username"),
    wallet: int | float = Query(0, description="The money in wallet"),
    bank: int | float = Query(0, description="The money in the bank"),
    background: str = Query(None, description="An optional image URL for the card background"),
    footer: str = Query("APY", description="The footer for the card"),
    blur: bool = Query(True, description="If the background (if image) must have a blur filter")
):
    avatar = await APYManager.open_image(image, param="image")
    overlay = LocalImagesManager.fetch("wallet")
    base = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    if background:
        background: Image.Image = (await APYManager.open_image(background, param="background")).resize(base.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur([0, 10][blur]))
        base.paste(background, (0, 0), background)
    else:
        await APYManager.draw_gradient(base, [(-2, -2), (520, 285)], APYManager.get_dominant_colors(avatar))
    
    avatar = APYManager.ellipse(avatar).resize((42, 42), Image.Resampling.LANCZOS)
    base.paste(avatar, (50, 47), avatar)
    base.paste(overlay, (0, 0), overlay)

    await APYManager.draw_text(base, xy=(105, 56), text=username, font=TypeFaceManager.fetch("GGSans", "Medium", 17), colour="White")

    draw = ImageDraw.Draw(base)
    w, h = APYManager.get_metrics(TypeFaceManager.fetch("GGSans", "Bold", 16), footer)
    draw.text(((base.width - w) // 2, 240), footer, colour="#dadada", font=TypeFaceManager.fetch("GGSans", "Bold", 16))
    font = TypeFaceManager.fetch("GGSans", "Normal", 19)
    draw.text((115, 111), str(wallet), colour="White", font=font)
    draw.text((115, 158), str(bank), colour="White", font=font)
    draw.text((115, 204), str(wallet + bank), colour="White", font=font)
    
    return Response(content=APYManager.prepare(base), media_type="image/png")