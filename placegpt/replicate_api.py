# %%

import replicate
import os
from cairosvg import svg2png

# %%
os.environ["REPLICATE_API_TOKEN"] = "cdfdd32a0bd5e1b2df1f9fb6768c6ad3eb16ad41"


# %%
def stylize(image_path="static/output.svg", prompt: str = "aestheic"):
    svg2png(url=image_path, write_to=image_path.replace(".svg", ".png"))

    output = replicate.run(
        "rossjillian/controlnet:d55b9f2dcfb156089686b8f767776d5b61b007187a4e1e611881818098100fbb",
        input={
            "image": open(image_path.replace(".svg", ".png"), "rb"),
            "prompt": prompt,
            "structure": "canny",
        },
    )

    return output[0]


# %%
if __name__ == "__main__":
    stylize(prompt="aesthetic solar system")

# %%
