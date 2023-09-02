from fastapi import APIRouter, Query, Response
from main import APYManager, LocalImagesManager
from PIL import Image, ImageFilter
from typing import Literal

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/ship",
    description="Make a ship image of two images",
    response_class=Response,
    responses=APYManager.get_responses(image=True)
)
async def ship(
    image: str = Query(description="The image number 1 URL", example="https://images.com/myimage.png", alias="image1"),
    image2: str = Query(description="The image number 2 URL", example="https://images.com/myimage2.png"),
    style: Literal["normal", "fire", "broken"] | None = Query("normal", description="The style of the heart"),
    background: str | None = Query(None, description="An optional background for the image"),
    blur: bool | None = Query(True, description="If the background must have a blur filter")
):
    base = Image.new("RGBA", (1250, 500), (0, 0, 0, 0))
    images = (await APYManager.open_image(image, param="image"), await APYManager.open_image(image2, param="image2"))
    images = (images[0].resize((650, 650)), images[1].resize((650, 650)))
    background: Image.Image | None = await APYManager.open_image(background, param="background") if background else None
    if background:
        background = background.resize((1250, 500), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur([0, 25][blur]))
        base.paste(background, (0, 0), background)
    else:
        base.paste(images[0].filter(ImageFilter.GaussianBlur([0, 25][blur])), (-10, -50), images[0].filter(ImageFilter.GaussianBlur([0, 25][blur])))
        base.paste(images[1].filter(ImageFilter.GaussianBlur([0, 25][blur])), (base.width // 2, -50), images[1].filter(ImageFilter.GaussianBlur([0, 25][blur])))
    images = (APYManager.apply_rounded_borders(images[0], 20).resize((372, 372), Image.Resampling.LANCZOS), APYManager.apply_rounded_borders(images[1], 20).resize((372, 372), Image.Resampling.LANCZOS))
    base.paste(images[0], (60, 70), images[0])
    base.paste(images[1], (820, 70), images[1])
    overlay = LocalImagesManager.fetch(f"heart_{style}").resize((323, 323))
    base.paste(overlay, (465, 95), overlay)
    return Response(content=APYManager.prepare(base), media_type="image/png")