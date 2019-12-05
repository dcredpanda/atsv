# Controllers for database

import os
import glob

#@1 below will import all routes in current path, autodefines routes
__all__ = [os.path.basename(f)[:-3]
           for f in glob.glob(os.path.dirname(__file__) + "/*.py")]

