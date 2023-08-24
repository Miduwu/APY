# import modules
import importlib, importlib.util, abc, httpx, textwrap
import os, io, re, traceback, typing, json, numpy as np
from dataclasses import dataclass
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from PIL import Image, ImageDraw, ImageFont

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
                    return res.text()
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
        return bio
    
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
    
    def get_dominant_colors(self, image: Image.Image, colors: int = 2):
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
    
    async def draw_gradient(base, xy, colors, direction="vertical"):
        """
        Draws a gradient in an image
        """
        def interpolate_color(color1, color2, ratio):
            return tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(color1, color2))
        
        width, height = xy[1]
        gradient = []
        color_range = len(colors) - 1
        if direction == "vertical":
            for i in range(height):
                ratio = i / (height - 1)
                color_index = int(ratio * color_range)
                color1, color2 = colors[color_index], colors[color_index + 1]
                gradient.append(interpolate_color(color1, color2, ratio))
        elif direction == "horizontal":
            for i in range(width):
                ratio = i / (width - 1)
                color_index = int(ratio * color_range)
                color1, color2 = colors[color_index], colors[color_index + 1]
                gradient.append(interpolate_color(color1, color2, ratio))
        d = ImageDraw.Draw(base)
        if direction == "vertical":
            for i, color in enumerate(gradient):
                d.line((xy[0][0], xy[0][1] + i, xy[0][0] + width, xy[0][1] + i + 1), fill=color, width=1)
        elif direction == "horizontal":
            for i, color in enumerate(gradient):
                d.line((xy[0][0] + i, xy[0][1], xy[0][0] + i + 1, xy[0][1] + height), fill=color, width=1)
    
    def get_metrics(self, font: ImageFont.FreeTypeFont, text: str):
        """
        Get the text metrics
        """
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]