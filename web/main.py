from flask import Flask
from flask import request
import sys, os
import importlib.util
spec = importlib.util.spec_from_file_location("converter", os.path.abspath("../converter.py"))
converter = importlib.util.module_from_spec(spec)
sys.modules["converter"] = converter
spec.loader.exec_module(converter)

app = Flask(__name__)

@app.route("/")
def hello_world():
    with open("index.html", "rb") as f:
        return f.read()

@app.route("/convert", methods = ["POST"])
def convert():
    if not request.method == "POST":
        return "only use in POST"
    if not (request.headers.get("Content-Type", "") == "image/svg+xml"):
        return "not right content type"
    return converter.toJsonRaw(request.get_data(), request.headers.get("joinLines", "false")=="true", request.headers.get("roundValues", "false")=="true")