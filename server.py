import mimetypes
import os
import quart
import quart_cors
from quart import request

# Note: Setting CORS to allow chat.openapi.com is only required when running a localhost plugin
app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

PROTO = "http://"  # TODO Make this https

DEBUG = True  # TODO Turn off for production


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


@app.get("/canvas")
async def canvas():
    # TODO: Fill in with result of running the model
    filename = "static/cat.svg"
    return await quart.send_file(filename, mimetype="image/svg")


def handle_instruction(instruction):
    print("Handling instruction:", instruction)


def main():
    app.run(debug=DEBUG, host="0.0.0.0", port=5002)


if __name__ == "__main__":
    main()
