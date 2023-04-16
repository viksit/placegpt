import json

import quart
import quart_cors
from quart import request

# Note: Setting CORS to allow chat.openapi.com is only required when running a localhost plugin
app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


@app.get("/logo.png")
async def plugin_logo():
    filename = "logo.png"
    return await quart.send_file(filename, mimetype="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers["Host"]
    with open("manifest.json") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the manifest
        text = text.replace("PLUGIN_HOSTNAME", f"http://{host}")  # TODO: https
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers["Host"]
    with open("openapi.yaml") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
        text = text.replace("PLUGIN_HOSTNAME", f"http://{host}")  # TODO: https
        return quart.Response(text, mimetype="text/yaml")


OBJECTS = {}


@app.post("/api/draw")
async def receive_instruction():
    request = await quart.request.get_json(force=True)
    print(f"request is {request}")
    handle_instruction(request["instruction"])
    return quart.Response(response="OK", status=200)


def handle_instruction(instruction):
    print("Handling instruction:", instruction)


def main():
    app.run(debug=True, host="0.0.0.0", port=5002)


if __name__ == "__main__":
    main()
