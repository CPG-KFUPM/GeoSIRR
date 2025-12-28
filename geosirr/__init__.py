from . import io
from . import llm
from . import vis

try:
    from .version import build as __build__
    from .version import version as __version__
except ImportError:
    from datetime import datetime

    __build__ = None
    __version__ = "unknown-" + datetime.today().strftime("%Y%m%d")
