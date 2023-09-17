# import modules
import importlib, importlib.util, abc, httpx
import os, io, typing, numpy as np
from dataclasses import dataclass
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from .schemas import HTTPResponse, HTTPBadResponse
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

@dataclass(frozen=True)
class Util(abc.ABC):
    app: FastAPI

    async def load_routes(self):
        """
        Loads all the FastAPI routers from the directory
        """
        for folder in os.listdir("./routers"):
            for file in os.listdir(f"./routers/{folder}"):
                if file.endswith(".py") and "ignore" not in file:
                    name = importlib.util.resolve_name(file[:-3], None)
                    router = importlib.import_module(f"routers.{folder}.{name}", None)
                    if hasattr(router, "router"):
                        self.app.include_router(getattr(router, "router"))
                    else:
                        pass
    
    async def request(self, *, method: str, url: str, params: typing.Dict[str, str] = {}, headers: typing.Dict[str, str] = {}, json: typing.Dict | None = None, get: typing.Literal["json", "text", "bytes"] = "json"):
        """
        Make a HTTP request
        """
        try:
            async with httpx.AsyncClient() as client:
                res = await client.request(method, url, json=json, params=params, headers=headers)
                if res.status_code != 200 and res.status_code != 201:
                    pass
                if get == "json":
                    return res.json()
                elif get == "text":
                    return res.text
                elif get == "bytes":
                    return res.read()
        except:
            pass
    
    async def open_image(self, data: str, mode: typing.Literal["RGB", "RGBA"] = "RGBA", param=None):
        """
        Opens (local/remote) the image and return it
        """
        if not data and param:
            raise HTTPException(422, { "msg": "Missing image URL", "loc": (param, "query")})
        else:
            pass
        if data.startswith("path:"):
            try:
                with Image.open(data.replace("path:", "")) as img:
                    return img.convert(mode)
            except:
                pass
        else:
            try:
                r = await self.request(method="GET", url=data, get="bytes")
                with Image.open(io.BytesIO(r)) as img:
                    return img.convert(mode)
            except:
                if param:
                    raise HTTPException(422, { "msg": "Invalid image URL provided", "loc": (param, "query") })
                else:
                    pass
    
    def prepare(self, image: Image.Image, format="PNG"):
        """
        Prepares the final result of the image
        """
        bio = io.BytesIO()
        image.save(bio, format)
        if format.lower() == "gif":
            bio.seek(0, 0) # animated images (gif)
        else:
            bio.seek(0) # static images
        return bio.getvalue()
    
    def ellipse(self, image: Image.Image):
        """
        Returns an image with an ellipse
        """
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        width, height = image.size
        draw.ellipse((0, 0, width, height), fill=255)
        image.putalpha(mask)
        return image
    
    async def draw_text(self, image: Image.Image, **kwargs):
        """
        Draws an advanced text
        """
        with Pilmoji(image) as pilmoji:
            pilmoji.text(**kwargs)
    
    def apply_rounded_borders(self, image: Image.Image, radius: int = 10):
        """
        Returns this image but with rounded borders
        """
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        width, height = image.size
        draw.rounded_rectangle((0, 0, width, height), radius, fill=255)
        image.putalpha(mask)
        return image
    
    def get_advanced_metrics(self, image: Image.Image, font: ImageFont.FreeTypeFont, text: str, spacing: int = 4):
        """
        Get the metrics of an advanced text
        """
        with Pilmoji(image) as pilmoji:
            return pilmoji.getsize(text=text, font=font, spacing=spacing)
    
    def kmeans(self, pixels, k, max_iter=100):
        """
        Returns the most common but with different scores pixels
        """
        centroids = pixels[np.random.choice(pixels.shape[0], size=k, replace=False)]
        for _ in range(max_iter):
            distances = np.sqrt(((pixels - centroids[:, np.newaxis])**2).sum(axis=2))
            closest = np.argmin(distances, axis=0)
            new_centroids = []
            for cluster_idx in range(centroids.shape[0]):
                cluster_pixels = pixels[closest == cluster_idx]
                if len(cluster_pixels) > 0:
                    new_centroid = cluster_pixels.mean(axis=0)
                    new_centroids.append(new_centroid)
                else:
                    new_centroids.append(centroids[cluster_idx])
            new_centroids = np.array(new_centroids)
            if np.all(centroids == new_centroids):
                break
            centroids = new_centroids
        return centroids
    

    
    def get_dominant_colors(self, img: Image.Image, colors: int = 2):
        """
        Get the dominant colors of an image using clusters
        """
        img = img.resize((int(img.size[0] / 2), int(img.size[1] / 2)))
        img = img.convert('RGBA')
        pixels = np.array(img)
        pixels = pixels.reshape(-1, pixels.shape[-1])
        dominant_colors = self.kmeans(pixels, colors)
        closest = np.argmin(np.sqrt(((pixels - dominant_colors[:, np.newaxis])**2).sum(axis=2)), axis=0)
        cluster_counts = np.bincount(closest, minlength=dominant_colors.shape[0])
        pairwise_distances = np.sqrt(((dominant_colors[:, np.newaxis, :] - dominant_colors[np.newaxis, :, :])**2).sum(axis=2))
        scores = cluster_counts * (1 / (1 + pairwise_distances.sum(axis=0)))
        sorted_indices = np.argsort(scores)[::-1]
        sorted_dominant_colors = dominant_colors[sorted_indices]
        return [list(map(int, color)) for color in sorted_dominant_colors[:colors]]
    
    async def draw_gradient(self, base: Image.Image, xywh: typing.Tuple[typing.Tuple[int]], colors: typing.List, direction: str = "vertical"):
        """
        Draws a gradient on the image.
        """
        if direction not in ("vertical", "horizontal"):
            raise ValueError("Invalid direction value. Only 'vertical' or 'horizontal' are allowed.")
        
        if len(colors) < 2:
            raise ValueError("At least two colors are required for a gradient.")
        
        gradient = []
        W, H = xywh[1]
        use = H if direction == "vertical" else W
        for i in range(use):
            index = int(i / use * (len(colors) - 1))
            r1, g1, b1, a1 = colors[index]
            r2, g2, b2, a2 = colors[index + 1]
            ratio = i / use * (len(colors)) - index
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            gradient.append((r, g, b))
        
        d = ImageDraw.Draw(base)
        for i in range(use):
            if direction == "vertical":
                d.line((xywh[0][0], xywh[0][1] + i, xywh[0][0] + W, xywh[0][1] + i + 1), fill=gradient[i], width=1)
            else:
                d.line((xywh[0][0] + i, xywh[0][1], xywh[0][0] + i + 1, xywh[0][1] + H), fill=gradient[i], width=1)
    
    def get_metrics(self, font: ImageFont.FreeTypeFont, text: str):
        """
        Get the text metrics
        """
        if "\n" in text:
            lines = text.split("\n")
            W, H = 0, 0
            for line in lines:
                bbox = font.getbbox(line)
                width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                if width > W:
                    W = width
                H += height
            return W, H
        else:
            bbox = font.getbbox(text)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def get_responses(self, image: bool = False, media_type: str ="image/png"):
        """
        Returns a dict of responses
        """
        description = "The image result"
        return {
            200: {"description": description, "content": {media_type: {}}}
            if image
            else {"model": HTTPResponse},
            422: {"model": HTTPBadResponse},
            400: {"model": HTTPBadResponse},
            401: {"model": HTTPBadResponse},
            404: {"model": HTTPBadResponse},
            405: {"model": HTTPBadResponse},
            500: {"model": HTTPBadResponse},
        }
