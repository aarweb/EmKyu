import os

from dotenv import dotenv_values

environment = {**dotenv_values(), **os.environ}
