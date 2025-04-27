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
    return save_image_or_video(ctx, handler, '.png')


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
    return save_image_or_video(ctx, handler, '.png')


@mcp.tool()
async def edit_image(ctx: Context, prompt: str, image_path: str):
    """Edit an image using the Gemini Flash Edit model."""
    await ctx.info(f"Editing image with prompt: {prompt}")
    image_url = fal_client.upload_file(image_path)
    handler = fal_client.submit(
        "fal-ai/gemini-flash-edit",
        arguments={"prompt": prompt, "image_url": image_url},
    )
    return save_image_or_video(ctx, handler, '.png')


@mcp.tool()
async def generate_video(ctx: Context, prompt: str, image_path: str, negative_prompt: str = "None"):
    """Generate a video based on a prompt and an initial image using the wan-i2v/turbo model."""
    await ctx.info(f"Generating video with prompt: {prompt}")
    image_url = fal_client.upload_file(image_path)
    if negative_prompt == "None":
        negative_prompt = (
            "bright colors, overexposed, static, blurred details, subtitles, style, artwork, painting, "
            "picture, still, overall gray, worst quality, low quality, JPEG compression residue, ugly, "
            "incomplete, extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, "
            "malformed limbs, fused fingers, still picture, cluttered background, three legs, many people "
            "in the background, walking backwards"
        )
    handler = fal_client.submit(
        "fal-ai/wan-i2v/turbo",
        arguments={
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_url": image_url,
            "num_frames": 81,
            "frames_per_second": 16,
            "resolution": "480p",
            "num_inference_steps": 30,
            "shift": 5,
            "acceleration": "regular",
            "aspect_ratio": "auto",
        },
    )
    return save_image_or_video(ctx, handler, '.mp4')


def save_image_or_video(ctx: Context, handler, file_extension: str):
    """Saves the image or video result from a fal-client handler."""
    result = handler.get()
    media_url = None

    if result.get("images"):
        media_url = result.get("images")[0].get("url")
    elif result.get("image"):
        media_url = result.get("image")["url"]
    elif result.get("video"):
        media_url = result.get("video")["url"]

    if media_url:
        response = requests.get(media_url)
        response.raise_for_status()

        save_dir = os.environ.get("SAVE_MEDIA_DIR")
        if not save_dir:
            raise Exception("SAVE_MEDIA_DIR environment variable not set.")

        os.makedirs(save_dir, exist_ok=True)
        next_index = len(os.listdir(save_dir))
        filepath = os.path.join(save_dir, f"{next_index:05d}{file_extension}")

        with open(filepath, "wb") as f:
            f.write(response.content)
        ctx.info(f"Saved to {filepath}")
        return f"The image or video was successfully generated and saved at: {filepath}"

    raise Exception("Error generating or saving the image or video")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
