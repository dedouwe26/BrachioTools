import sys, os
import json
import turtle

if len(sys.argv) < 2:
    print("Usage: python drawer.py [file]")
    exit()

def parse(data: str) -> tuple[list[list[tuple[float, float]]], float, float, float, float]:
    lines = json.loads(data)
    minX = 0
    minY = 0
    width = 0
    height = 0
    for line in lines:
        for point in line: 
            minX = min(minX, point[0])
            minY = min(minY, point[1])
            width = max(width, point[0])
            height = max(height, point[1])
    return (lines, width, height, minX, minY)

with open(os.path.abspath(sys.argv[1])) as file:
    lines, width, height, minX, minY = parse(file.read())

screen = turtle.Screen()
screen.setup(width, height)

t = turtle.Turtle("circle")
t.color("black")

t.penup()
for line in lines:
    for point in line:
        t.goto(point[0]-(width/2), -(point[1]-(height/2)))
        t.pendown()
    t.penup()

turtle.mainloop()