from pathlib import Path
from PIL import ImageFont
from abc import ABC

class TypefaceManager(ABC):
    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.is_dir():
            raise ValueError(f"Invalid directory: {path}")
        self.typefaces = self._load_typefaces()

    def _load_typefaces(self):
        typefaces = {}
        font_files = list(self.path.glob("*.ttf")) + list(self.path.glob("*.otf"))
        for font_file in font_files:
            typeface_name, *style = font_file.stem.split("_")
            style = style[0] if style else "Regular"
            typeface = ImageFont.truetype(str(font_file), size=12)
            typefaces.setdefault(typeface_name, {})[style] = typeface
        return typefaces

    def fetch(self, name, style="Regular", size=12) -> ImageFont.FreeTypeFont:
        typeface = self.typefaces.get(name, {}).get(style)
        if typeface:
            return typeface.font_variant(size=size)
        else:
            raise ValueError(f"Typeface {name} with style {style} not found.")