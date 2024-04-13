import sys, os
import xml.sax
import json

DECIMALS = 3
CLOSENESS = 128

class SVGParser(xml.sax.ContentHandler):
    roundValues: bool = False
    width: int = 0
    height: int = 0
    elements: list[list[tuple[float, float]]] = []

    def __init__(self, roundValues: bool):
        super().__init__()
        self.roundValues = roundValues

    def startElement(self, name, attrs):
        if name == "svg":
            self.width = int(float(attrs["width"].replace("px", "").replace("pt", "")))
            self.height = int(float(attrs["height"].replace("px", "").replace("pt", "")))
        elif name == "polyline":
            arr: list[tuple[float, float]] = []
            sub = ""
            for char in attrs["points"]:
                if char == "," or char == " ":
                    if len(arr) < 1:
                        if self.roundValues:
                            arr.append((round(float(sub), DECIMALS), None))
                        else:
                            arr.append((float(sub), None))
                    elif arr[-1][1] == None:
                        if self.roundValues:
                            arr[-1] = (arr[-1][0], round(float(sub), DECIMALS))
                        else:
                            arr[-1] = (arr[-1][0], float(sub))
                    else:
                        if self.roundValues:
                            arr.append((round(float(sub), DECIMALS), None))
                        else:
                            arr.append((float(sub), None))
                    sub = ""
                else:
                    sub+=char
            if self.roundValues and not sub == "":
                arr[-1] = (arr[-1][0], round(float(sub), DECIMALS))
            elif not sub == "":
                arr[-1] = (arr[-1][0], float(sub))

            # for pos in attrs["points"].split(" "):
            #     if pos == "":
            #         continue
            #     coord = pos.split(",")
            #     if self.roundValues:
            #         arr.append((round(float(coord[0]), DECIMALS), round(float(coord[1]), DECIMALS)))
            #     else:
            #         arr.append((float(coord[0]), float(coord[1])))
                
            self.elements.append(arr)

def toJson(inputPath: str, outputPath: str, joinLines: bool = False, roundValues: bool = False):
    """This should convert a SVG file into a brachio JSON file.

    Args:
        inputPath: path to SVG, 
        outputPath: path to JSON."""
    
    with open(inputPath, "r") as svg:
        with open(outputPath, "w") as json:
            json.write(toJsonRaw(svg.read(), joinLines, roundValues))

def __parseSVG(data: str, roundValues: bool) -> list[list[tuple[float, float]]]:
    parser = SVGParser(roundValues)
    xml.sax.parseString(data, parser)
    return parser.elements

def __resize(lines: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    # TODO: resize
    return lines

def __distsum(*args):
    # Code from brachiograph
    return sum(
        [
            ((args[i][0] - args[i - 1][0]) ** 2 + (args[i][1] - args[i - 1][1]) ** 2) ** 0.5
            for i in range(1, len(args))
        ]
    )

def __sortLines(lines: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    # Code from brachiograph
    clines = lines[:]
    slines = [clines.pop(0)]
    while clines != []:
        x = None
        s = 1000000
        r = False
        for l in clines:
            d = __distsum(l[0], slines[-1][-1])
            dr = __distsum(l[-1], slines[-1][-1])
            if d < s:
                x = l[:]
                s = d
                r = False
            if dr < s:
                x = l[:]
                s = s
                r = True
        clines.remove(x)
        if r == True:
            x = x[::-1]
        slines.append(x)
    return slines

def __joinLines(lines: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    # Code from brachiograph
    previous_line = None
    new_lines = []
    for line in lines:
        if not previous_line:
            new_lines.append(line)
            previous_line = line
        else:
            xdiff = abs(previous_line[-1][0] - line[0][0])
            ydiff = abs(previous_line[-1][1] - line[0][1])
            if xdiff**2 + ydiff**2 <= CLOSENESS:
                previous_line.extend(line)
            else:
                new_lines.append(line)
                previous_line = line
    lines = new_lines
    return lines

def toJsonRaw(data: str, joinLines: bool = False, roundValues: bool = False) -> str:
    """This should convert a SVG data into a brachio JSON data.
    
    Args:
        data: The SVG data, 
    Returns: The JSON data."""
    lines = __parseSVG(data, roundValues)
    lines = __resize(lines)
    lines = __sortLines(lines)
    if joinLines:
        lines = __joinLines(lines)

    return json.dumps(lines)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 4:
        print("Usage: python converter.py [svgFile] [outputFile] [true/false (join lines)] [true/false (round values)]")
        exit()
    
    print(args[0],"->",args[1]+"\nJoin lines [%s]\nRound values [%s]" % ("*" if args[2]=="true" else " ", "*" if args[3]=="true" else " "))

    toJson(os.path.abspath(args[0]), os.path.abspath(args[1]), args[2]=="true", args[3]=="true")

    print("Done.")
