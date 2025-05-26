import aiohttp
from PIL import Image, ImageDraw
from io import BytesIO
import discord

async def fetch_avatar(session, url):
    async with session.get(url) as resp:
        resp.raise_for_status()
        data = await resp.read()
        return Image.open(BytesIO(data)).convert("RGBA")
    


async def wedgeImageByURLs(urls,client):
    images = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            img = await fetch_avatar(session, url)
            images.append(img)
    pie = composite_pie_chart_images(images)
    image_binary = BytesIO()
    pie.save(image_binary, format="PNG")
    image_binary.seek(0)
    file = discord.File(fp=image_binary, filename="pie_chart.png")
    return file

def create_wedge_mask(size, start_angle, end_angle):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    center = (size[0] // 2, size[1] // 2)
    radius = min(size) // 2

    draw.pieslice([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius],
                  start=start_angle, end=end_angle, fill=255)
    return mask

def composite_pie_chart_images(images):
    n = len(images)
    min_dim = min(min(img.size) for img in images)
    canvas_size = (min_dim, min_dim)
    images = [img.resize(canvas_size) for img in images]

    final = Image.new("RGBA", canvas_size)
    angle_per_slice = 360 / n

    for i, img in enumerate(images):
        start_angle = i * angle_per_slice
        end_angle = (i + 1) * angle_per_slice
        mask = create_wedge_mask(canvas_size, start_angle, end_angle)
        final.paste(img, (0, 0), mask)

    return final
