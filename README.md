# BrachioTools
BrachioTools contains a port of BrachioGraph, but for MicroPython (see: mp folder).
BrachioTools can also turn an SVG into an brachio graph JSON file. \
`NOTE: Will only use the poly lines in an SVG (paths are not ).`

## Usage For MicroPython

In the `mp` folder, there is a file called `bundle.py` and `bundle-min.py`. These files contain the program and the configuration (at the top). These files are runnable. \
Possible error messages:
- `ERROR: This device does not have MicroPython.`: This means that the code is not running on micropython, because it couldn't find the `machine` module.
- `ERROR: ulab micropython is not installed.`: This means that [ulab](https://github.com/v923z/micropython-ulab) is not installed as the firmware.

## Usage For Tools

The converter is located in converter.py. \
You can execute the python program: \
`python converter.py [svgFile] [outputFile] [true/false (join lines)] [true/false (round values)]` or \
You can use the file as an module. \
Or in the web folder there is a flask program that you can run using flask: `flask --app main.py run` and use it in the web.

You can visualise a brachio json file using the drawer.py: \
`python drawer.py [file]`.