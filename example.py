import pickle


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2


class ClosedPolyline:
    def __init__(self, lines):
        self.lines = lines


def main():
    p1 = Point(2, 3)
    p2 = Point(3, 5)
    p3 = Point(0, 0)
    line1 = Line(p1, p2)
    line2 = Line(p1, p3)
    line3 = Line(p2, p3)
    closed_polyline = ClosedPolyline([line1, line2, line3])

    print(closed_polyline)
    bin_data = pickle.dumps(closed_polyline)
    print(bin_data)
    new_obj = pickle.loads(bin_data)
    print(new_obj)


if __name__ == "__main__":
    main()