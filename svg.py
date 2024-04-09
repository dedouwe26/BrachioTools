import sys, os

def toJson(inputPath: str, outputPath: str):
    """This should convert a SVG file into a brachio JSON file.

    Args:
        inputPath: path to SVG, 
        outputPath: path to JSON."""
    
    with open(inputPath, "r") as svg:
        with open(outputPath, "w") as json:
            json.write(toJsonRaw(svg.read()))

def __parseSVG(data: str) -> list[list[tuple[float, float]]]:
    pass

def __resize():
    pass

def __sortLines(lines: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    pass

def __joinLines(lines: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    pass

def toJsonRaw(data: str) -> str:
    """This should convert a SVG data into a brachio JSON data.
    
    Args:
        data: The SVG data, 
    Returns: The JSON data."""
    lines = __parseSVG(data)

if __name__ == "__main__":
    args = sys.argv[1:]
    print(args)