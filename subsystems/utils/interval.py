import numpy as np
from ..libs import rvms


def confidence_interval(alpha, n, l) -> float:
    sigma = np.std(l, ddof=1)
    if n > 1:
        t = rvms.idfStudent(n - 1, 1 - alpha / 2)
        return (t * sigma) / np.sqrt(n - 1)
    else:
        return 0.0
