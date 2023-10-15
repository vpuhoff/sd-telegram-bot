from random import random
from time import sleep

from shared import app


@app.task
def say_hello(name: str):
    sleep(random())
    return f"Hello {name}"