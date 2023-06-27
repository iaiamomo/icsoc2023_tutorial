import logging
from typing import Optional, Any
import math
import random
import re 

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

class RegexConstrainedString(str):
    """
    A string that is constrained by a regex.

    The default behaviour is to match anything.
    Subclass this class and change the 'REGEX' class attribute to implement a different behaviour.
    """

    REGEX = re.compile(".*", flags=re.DOTALL)

    def __new__(cls, value: str, *_args: Any, **_kwargs: Any) -> Any:
        """Instantiate a new object."""
        if type(value) == cls:  # pylint: disable=unidiomatic-typecheck
            return value
        inst = super(RegexConstrainedString, cls).__new__(cls, value)
        return inst

    def __init__(self, *_: Any, **__: Any) -> None:
        """Initialize a regex constrained string."""
        super().__init__()
        if not self.REGEX.fullmatch(self):
            self._handle_no_match()

    def _handle_no_match(self) -> None:
        raise ValueError(
            f"Value '{self}' does not match the regular expression {self.REGEX}"
        )

class ServiceId(RegexConstrainedString):

    REGEX = re.compile("^[A-Za-z0-9-_]+$")
