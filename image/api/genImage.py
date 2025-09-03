import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16
).to("cuda")

image = pipe("A fantasy landscape with castles and dragons, digital art").images[0]
image.save("output.png")
