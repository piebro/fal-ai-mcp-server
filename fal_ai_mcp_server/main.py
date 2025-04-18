import os

import fal_client
import requests
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("Fal AI MCP Server", log_level="ERROR")


@mcp.tool()
async def generate_image(ctx: Context, prompt: str):
    """Generate an image using the Flux model."""
    await ctx.info(f"Generating image with prompt: {prompt}")
    handler = fal_client.submit(
        "fal-ai/flux/dev",
        arguments={
            "prompt": prompt,
            "image_size": {"width": 512, "height": 512},
            "enable_safety_checker": False,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "num_images": 1,
            "output_format": "png",
        },
    )
    return save_image(ctx, handler)


@mcp.tool()
async def generate_image_lora(ctx: Context, prompt: str, lora_url: str, lora_scale: float = 1):
    """Generate an image using the Flux model with a LoRA."""
    await ctx.info(f"Generating image with prompt: {prompt} and LoRA: {lora_url}")
    handler = fal_client.submit(
        "fal-ai/flux-lora",
        arguments={
            "prompt": prompt,
            "image_size": {"width": 512, "height": 512},
            "enable_safety_checker": False,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "num_images": 1,
            "output_format": "png",
            "loras": [{"path": lora_url, "scale": lora_scale}],
        },
    )
    return save_image(ctx, handler)


@mcp.tool()
async def edit_image(ctx: Context, prompt: str, image_path: str):
    """Edit an image using the Gemini Flash Edit model."""
    await ctx.info(f"Editing image with prompt: {prompt}")
    image_url = fal_client.upload_file(image_path)
    handler = fal_client.submit(
        "fal-ai/gemini-flash-edit",
        arguments={"prompt": prompt, "image_url": image_url},
    )
    return save_image(ctx, handler)


def save_image(ctx: Context, handler):
    result = handler.get()

    image_url = None
    if result.get("images"):
        image_url = result.get("images")[0].get("url")
    elif result.get("image"):
        image_url = result.get("image")["url"]

    if image_url:
        response = requests.get(image_url)
        response.raise_for_status()

        save_dir = os.environ.get("SAVE_IMAGE_DIR")
        if not save_dir:
            raise Exception("SAVE_IMAGE_DIR environment variable not set.")

        os.makedirs(save_dir, exist_ok=True)
        next_index = len([f for f in os.listdir(save_dir) if f.lower().endswith(".png")])
        filepath = os.path.join(save_dir, f"{next_index:05d}.png")
        with open(filepath, "wb") as f:
            f.write(response.content)
        ctx.info(f"Image saved to {filepath}")
        return f"SEND_IMAGE_PATH: {filepath}"
    raise Exception("Error generating or saving the image")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
