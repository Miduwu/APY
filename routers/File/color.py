from fastapi import APIRouter, Query, Response
from main import APYManager, TypeFaceManager
from PIL import Image, ImageDraw

router = APIRouter(prefix="/image", tags=["Files"])

@router.get("/color",
    description="Make an image of the color you provided"
)
async def show_color(
    code: str = Query(description="The hex code", regex="([a-fA-F0-9]{6}|[a-fA-F0-9]{3})"),
    width: int = Query(512, description="The image width", ge=15, le=1024),
    height: int = Query(512, description="The image height", ge=15, le=1024),
    showCode: bool = Query(True, description="If the image has to show the color code"),
    radius: int = Query(15, description="The radius for the rounded image", ge=0, le=150)
):
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([(0, 0), (width, height)], radius, fill="#"+code)
    if showCode:
        font = TypeFaceManager.fetch("GGSans", "Bold", size=45)
        text = f"#{code}"
        draw.text((25, height - 80), text, fill="White", font=font)
    
    return Response(content=APYManager.prepare(image).getvalue(), media_type="image/png")