# BrachioTools
Can turn an SVG into an brachio graph JSON file. \
NOTE: Will only use the poly lines in an SVG (paths are not ).

## Usage

The converter is located in converter.py. \
You can execute the python program: \
`python converter.py [svgFile] [outputFile] [true/false (join lines)] [true/false (round values)]` or \
You can use the file as an module. \
Or in the web folder there is a flask program that you can run using flask: `flask --app main.py run` and use it in the web.

You can visualise a brachio json file using the drawer.py: \
`python drawer.py [file]`.