import numpy as np
from svg.path import parse_path, Move, Line, CubicBezier, QuadraticBezier
from xml.dom import minidom

def svg_to_functions(svg_file, degree_upper=5):
    doc = minidom.parse(svg_file)
    path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
    doc.unlink()

    functions = []

    for path_string in path_strings:
        path = parse_path(path_string)
        points = []
        for segment in path:
            if isinstance(segment, (Line, CubicBezier, QuadraticBezier)):
                points.append((segment.start.real, segment.start.imag))
                points.append((segment.end.real, segment.end.imag))
            
        if points:
            points = np.array(points)
            x, y = points[:,0], points[:,1]

            degree = min(len(points) - 1, degree_upper)
            coeffs = np.polyfit(x, y, degree)

            expression = ' + '.join(f'{coeff}*x**{degree-i}' for i, coeff in enumerate(coeffs))
            functions.append(expression)

    return functions