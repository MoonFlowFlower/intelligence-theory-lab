from math import sqrt


def dot(a: tuple[float, float] | list[float], b: tuple[float, float] | list[float]) -> float:
    return float(a[0] * b[0] + a[1] * b[1])


def mat_vec(m: list[list[float]], v: tuple[float, float] | list[float]) -> list[float]:
    return [m[0][0] * v[0] + m[0][1] * v[1], m[1][0] * v[0] + m[1][1] * v[1]]


def outer(a: list[float], b: tuple[float, float] | list[float]) -> list[list[float]]:
    return [[a[0] * b[0], a[0] * b[1]], [a[1] * b[0], a[1] * b[1]]]


def weighted_least_squares(
    rows: list[tuple[tuple[float, float], float, float]],
    ridge: float = 0.05,
) -> list[float]:
    a00 = ridge
    a01 = 0.0
    a11 = ridge
    b0 = 0.0
    b1 = 0.0
    for x, y, weight in rows:
        a00 += weight * x[0] * x[0]
        a01 += weight * x[0] * x[1]
        a11 += weight * x[1] * x[1]
        b0 += weight * x[0] * y
        b1 += weight * x[1] * y
    det = a00 * a11 - a01 * a01
    if abs(det) < 1e-12:
        return [0.0, 0.0]
    return [(a11 * b0 - a01 * b1) / det, (-a01 * b0 + a00 * b1) / det]


def rmse(values: list[float]) -> float:
    if not values:
        return 0.0
    return sqrt(sum(v * v for v in values) / len(values))
