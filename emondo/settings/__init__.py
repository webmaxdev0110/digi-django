# application_python cookbook expects manage.py in a top level
# instead of app level dir, so the relative import can fail
try:
    from emondo.emondo.settings.base import *
except ImportError:
    from emondo.settings.base import *

try:
    from local_settings import *
except ImportError:
    pass