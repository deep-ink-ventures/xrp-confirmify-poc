from . import *
import os

DEBUG = False

# enforce overwrites
SECRET_KEY = os.environ['SECRET_KEY']
SIMPLE_JWT['SIGNING_KEY'] = os.environ['JWT_SIGNING_KEY']
