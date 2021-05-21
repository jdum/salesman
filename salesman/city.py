#!/usr/bin/env python
"""
"""
from dataclasses import dataclass, astuple
from os.path import exists
from functools import lru_cache
from math import dist
from secrets import randbelow
import yaml

from .parameters import Parameters

CITIES = "cities.yml"


@lru_cache(maxsize=None)
def distance(c0, c1):
    return dist(astuple(c0), astuple(c1))


@dataclass(frozen=True)
class City:
    x: int
    y: int

    __annotations__ = {
        "x": int,
        "y": int,
    }

    def __repr__(self):
        return f"({self.x},{self.y})"

    def distance(self, other):
        return distance(self, other)


def line():
    print("-" * 80)


_word_cities = []


def world_cities(p=None):
    global _word_cities
    if not _word_cities:
        path = p.join(CITIES)
        if not exists(path):
            generate_cities(p)
            p.erase_high_score()
        with open(path) as f:
            content = yaml.load(f, yaml.SafeLoader)
        _word_cities = tuple(City(i[0], i[1]) for i in content["cities"])
    return _word_cities


def city_nb(nb):
    return world_cities()[nb]


def generate_cities(p):
    nb_cities = p.get("nb_cities")
    line()
    print(
        f"Generating {nb_cities} cities.",
    )
    cities = []
    test_exist = set()
    size_x = p.get("size_x")
    size_y = p.get("size_y")
    while len(cities) < nb_cities:
        x = randbelow(size_x)
        y = randbelow(size_y)
        if (x, y) in test_exist:
            continue
        test_exist.add((x, y))
        cities.append(City(x, y))
    path = p.join(CITIES)
    print("Saving to", path)
    with open(path, "w") as f:
        yaml.dump({"cities": list(list(astuple(i)) for i in cities)}, f)


def test_cities(p):
    print(world_cities(p))
    for xy in ((0, 1), (1, 2), (0, 2)):
        x, y = xy
        print(city_nb(x), city_nb(y), city_nb(x).distance(city_nb(y)))


if __name__ == "__main__":
    test_cities(Parameters())
