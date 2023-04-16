#%%
import cv2
import diffusers
import numpy as np
from cairosvg import svg2png
from diffusers import DiffusionPipeline, StableDiffusionControlNetPipeline
from PIL import Image

#%%
def get_canny_image(svg_file="static/output.svg", png_file="static/stylized.png"):
    svg2png(url=svg_file, write_to=svg_file.replace(".svg", ".png"))

    img = Image.open(svg_file.replace(".svg", ".png"))
    img = img.convert("RGB")


    image = np.array(img)

    low_threshold = 100
    high_threshold = 200

    image = cv2.Canny(image, low_threshold, high_threshold)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    canny_image = Image.fromarray(image)

    return canny_image
#%%
def stylize(canny_image, prompt):
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        "krea/aesthetic-controlnet"
    )
    pipe = pipe.to("mps")
    pipe.enable_attention_slicing()
    image = pipe(image=canny_image, prompt=prompt, num_inference_steps=20).images[0]
    return image




#%%
cny = get_canny_image()

# %%
stylize(cny, "aesthetic")
# %%
