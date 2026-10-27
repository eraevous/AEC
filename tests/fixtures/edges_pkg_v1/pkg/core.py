import os
import json as js
from .base import Base
from pkg.extras import *
from pkg.util import helper


class Worker(Base):
    def step(self):
        return helper(2)


async def fetch():
    return await load()


def load():
    data = js.loads("{}")
    getattr(os, "getcwd")()
    return data


def main():
    w = Worker()
    w.run()
    return CONSTANT


CONSTANT = 3
