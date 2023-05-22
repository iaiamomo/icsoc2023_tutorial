import logging
from typing import Optional
import math
import random

def setup_logger(name: Optional[str] = None):
    """Set up the logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt="[%(asctime)s][%(name)s][%(levelname)s] %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def normpdf(mean = 0.5, sd = 0.1) -> float:
    x = random.random()
    var = float(sd)**2
    denom = (2*math.pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom