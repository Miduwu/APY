from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager
from PIL import Image, ImageDraw, ImageFilter
from fastapi.exceptions import HTTPException
from colour import Color
from math import isnan

def calculate(pr, total):
    prg = (pr / total) * 425
    if isnan(prg) or prg < 0:
        return 0
    if prg > 425:
        return 425
    return prg

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/rankcard",
    description="Make a rankcard using your own data",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def rank_card(
    image: str = Query(description="The avatar URL", example="https://images.com/myimage.png"),
    username: str = Query(description="The username"),
    xp: int | float = Query(description="The user experience", le=1000000, ge=0),
    total: int | float = Query(description="The required experience", le=1000000, ge=0),
    level: int = Query(0, description="The user level", le=10000, ge=0),
    rank: int = Query(0, description="The user rank", le=10000, ge=0),
    color: str = Query("5865F2", description="The color of the bar", regex="([a-fA-F0-9]{6}|[a-fA-F0-9]{3})"),
    background: str = Query(None, description="The background image URL for the card"),
    blur: bool = Query(True, description="If the card background must have a blur filter")
):
    if xp > total:
        raise HTTPException(422, { "error": "XP value cannot be greater than TOTAL value", "loc": "xp", "param_type": "query"})

    avatar = await APYManager.open_image(image, param="image")
    base = Image.new("RGBA", (750, 256), (0, 0, 0, 0))
    if background:
        bg = await APYManager.open_image(background, param="background")
        bg = bg.resize(base.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur([0, 20][blur]))
        base.paste(bg, (0, 0), bg)
    else:
        bg = avatar.copy().resize((750, 750), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur([0, 20][blur]))
        base.paste(bg, ((base.width - 750) // 2, (base.height - 750) // 2), bg)
    
    mask = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, base.width, base.height), 30, fill=(0, 0, 0, 180))
    base = Image.alpha_composite(base, mask)

    avatar = APYManager.apply_rounded_borders(avatar, 100).resize((256, 256))
    base.paste(avatar, (0, 0), avatar)

    font = TypeFaceManager.fetch("FranklinGothicDemi", "Regular", size=44)
    font2 = TypeFaceManager.fetch("GGSans", "Medium", size=15)
    await APYManager.draw_text(base, xy=(285, 40), text=username, font=font)
    draw = ImageDraw.Draw(base)
    draw.text((287, 90), f"Level: {level}    Rank: #{rank}", font=font2, fill="#dadada")

    bar_color = Color("#"+color)
    bar_color.luminance = 0.20
    draw.rounded_rectangle((285, 185, 285 + 425, 185 + 40), 15, fill=bar_color.hex_l)
    if xp >= 1:
        draw.rounded_rectangle((288, 188, calculate(xp, total) + 285, 188 + 34), 15, fill="#"+color, outline=bar_color.hex_l, width=7)

    draw.text((290, 160), f"XP: {xp}   /   {total}", font=font2, fill="White")

    mask = Image.new('L', base.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, base.width, base.height), 30, fill=255)
    base.putalpha(mask)

    return Response(content=APYManager.prepare(base), media_type="image/png")