import math

def quadrant(x, y):
    if math.isclose(x, 0) and math.isclose(y, 0):
        return "origin"
    elif math.isclose(x, 0):
        return "y-axis"
    elif math.isclose(y, 0):
        return "x-axis"
    elif x > 0 and y > 0:
        return "quadrant 1"
    elif x < 0 and y > 0:
        return "quadrant 2"
    elif x < 0 and y < 0:
        return "quadrant 3"
    else:
        return "quadrant 4"