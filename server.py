import json
import mimetypes
import os
import tempfile
import threading
from functools import wraps
import quart
import quart_cors
from quart import request
from cairosvg import svg2png
import requests


from placegpt.render import PromptManager
from placegpt.replicate_api import stylize

# Note: Setting CORS to allow chat.openapi.com is only required when running a localhost plugin
app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

PROTO = "http://"  # TODO Make this https

DEBUG = True  # TODO Turn off for production

prompt_manager = PromptManager()


@app.get("/logo.png")
async def plugin_logo():
    filename = "static/logo.png"
    return await quart.send_file(filename, mimetype="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers["Host"]
    with open("manifest.json") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the manifest
        text = text.replace("PLUGIN_HOSTNAME", f"{PROTO}{host}")
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers["Host"]
    with open("openapi.yaml") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
        text = text.replace("PLUGIN_HOSTNAME", f"{PROTO}{host}")
        return quart.Response(text, mimetype="text/yaml")


@app.post("/api/draw")
async def receive_instruction():
    request = await quart.request.get_json(force=True)
    handle_instruction(request["instruction"])
    return quart.Response(response="OK", status=200)


@app.post("/api/stylize")
async def stylize_image():
    request = await quart.request.get_json(force=True)
    style_image_url = stylize(image_path="static/output.png", prompt=request["prompt"])
    download_image(style_image_url, "static/output.png")
    return quart.Response(response="OK", status=200)


@app.get("/history")
async def history():
    history_json = json.dumps(history)
    return quart.Response(response=history_json, status=200, mimetype="text/json")


@app.route("/static/<path:filename>")
async def serve_files(filename):
    filepath = os.path.join("static", filename)

    if not os.path.exists(filepath):
        return "File not found", 404

    mime_type, _ = mimetypes.guess_type(filepath)
    return await quart.send_file(filepath, mime_type)


@app.get("/")
async def home():
    filename = "static/index.html"
    return await quart.send_file(filename, mimetype="text/html")


SERVE_SVG = False


@app.get("/canvas")
async def canvas():
    if SERVE_SVG:
        filename = "static/output.svg"
        return await quart.send_file(filename, mimetype="image/svg")
    else:
        filename = "static/output.png"
        return await quart.send_file(filename, mimetype="image/png")


instructions_list = []


# Handle one request at a time.
def synchronized(func):
    lock = threading.Lock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return wrapper


history = []


@synchronized
def handle_instruction(instruction):
    print("Handling instruction:", instruction)
    prompt_manager.run_prompt_with_state(instruction)

    history.append(instruction)

    objects = list(prompt_manager.img_objects.values())
    write_output_images(objects)


def write_output_images(objects=[]):
    header = """ <svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000"> """
    footer = """ </svg> """

    svg = "\n".join([header] + objects + [footer])

    svg_path = "static/output.svg"
    with open(svg_path, "w") as f:
        f.write(svg)

    convert_svg_to_png(svg_path, svg_path.replace(".svg", ".png"))


def convert_svg_to_png(image_path: str, target_path: str):
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        svg2png(url=image_path, write_to=temp_file.name)
    os.rename(temp_file.name, target_path)


def download_image(url: str, target_path: str = "static/output.png"):
    response = requests.get(url)

    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            with open(temp_file.name, "wb") as f:
                f.write(response.content)
        os.rename(temp_file.name, target_path)
    else:
        print("Error downloading image:", response.status_code)


def main():
    # Initial empty render.
    write_output_images()

    app.run(debug=DEBUG, host="0.0.0.0", port=5002)


if __name__ == "__main__":
    main()
