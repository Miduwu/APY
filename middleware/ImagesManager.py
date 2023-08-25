from pathlib import Path
from PIL import Image
from abc import ABC

class LocalImagesManager(ABC):
    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.is_dir():
            raise ValueError(f"Invalid directory: {path}")
        self.images = self._load_images()

    def _load_images(self):
        images = {}
        image_files = list(self.path.glob("*.png")) + list(self.path.glob("*.jpg")) + list(self.path.glob("*.jpeg"))
        for image_file in image_files:
            image_name = image_file.stem
            image = Image.open(image_file)
            images[image_name] = image
        return images

    def fetch(self, image_name: str) -> Image.Image:
        image = self.images.get(image_name)
        if image:
            return image.copy()
        else:
            raise ValueError(f"Image not found: {image_name}")