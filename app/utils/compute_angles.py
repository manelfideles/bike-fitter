import math


def calculate_angle(a, b, c):
    """
    Calculates the angle at point 'b' given three 2D points: a, b, and c.
    Returns angle in degrees.
    """
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])

    dot_product = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(*ba)
    mag_bc = math.hypot(*bc)

    if mag_ba * mag_bc == 0:
        return None

    cosine_angle = dot_product / (mag_ba * mag_bc)
    angle = math.acos(max(-1, min(1, cosine_angle)))
    return math.degrees(angle)
