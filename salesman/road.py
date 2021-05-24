#!/usr/bin/env python
from dataclasses import dataclass, field, astuple
from itertools import tee
from random import randrange
from copy import deepcopy

from .city import world_cities, distance, City
from .parameters import Parameters


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


@dataclass(frozen=False)
class Road:
    path: tuple = field(default=None, init=True, compare=True, hash=True, repr=True)
    _xpath: tuple = field(
        default=None, init=False, compare=False, hash=False, repr=False
    )
    _nodes_set: set = field(
        default=None, init=False, compare=False, hash=False, repr=False
    )
    _edges_list: list = field(
        default=None, init=False, compare=False, hash=False, repr=False
    )
    _edges_set: set = field(
        default=None, init=False, compare=False, hash=False, repr=False
    )
    _length: float = field(
        default=None, init=False, compare=False, hash=False, repr=False
    )
    # __annotations__ = {"path": tuple}

    def short_repr(self):
        return (
            f"{self.length:.1f} : {self.path[1]} {self.path[2]} "
            f"{self.path[3]}...{self.path[-1]}"
        )

    @classmethod
    def random(cls, cities):
        path = []
        avail = list(deepcopy(cities))
        path.append(avail.pop(0))
        while avail:
            path.append(avail.pop(randrange(len(avail))))
        return cls(tuple(path))

    @classmethod
    def from_list(cls, path):
        return cls(tuple(City(*xy) for xy in path))

    def export_path(self):
        return list(list(astuple(x)) for x in self.path)

    @property
    def xpath(self):
        "extended path"
        if self._xpath is None:
            self._xpath = self.path + (self.path[0],)
        return self._xpath

    @property
    def nodes_set(self):
        if self._nodes_set is None:
            self._nodes_set = set(self.path)
        return self._nodes_set

    @property
    def edges_list(self):
        if self._edges_list is None:
            self._edges_list = list(pairwise(self.xpath))
        return self._edges_list

    @property
    def edges_set(self):
        if self._edges_set is None:
            self._edges_set = set(pairwise(self.xpath))
        return self._edges_set

    @property
    def length(self):
        if self._length is None:
            self._length = sum(distance(*p) for p in pairwise(self.xpath))
        return self._length

    def shorter_than(self, r):
        if isinstance(r, float):
            return bool(self.length < r)
        return bool(self.length < r.length)

    def first(self, nb):
        """Return a new object from the n first nodes"""
        return self.__class__(self.path[:nb])

    def first_half(self):
        return self.first(len(self.path) // 2)

    def append_one_random(self, cities):
        """Return a new object by adding some random node"""
        nodes = self.nodes_set
        avail = list(x for x in deepcopy(cities) if x not in nodes)
        if not avail:
            return None
        new = avail.pop(randrange(len(avail)))
        return self.__class__(self.path + (new,))

    def append_road(self, road):
        """Try to append each node of another instance, return a new instance"""
        nodes = self.nodes_set
        path = list(self.path)
        for node in road.path:
            if node in nodes:
                continue
            path.append(node)
            nodes.add(node)
        return self.__class__(tuple(path))


def optimize_abcd(road):
    """optimize path for 4 points

    when path is ABCD, check if ACBD whould be better
    """
    need_optimize = True
    while need_optimize:
        need_optimize = False
        for i in range(len(road.xpath) - 3):
            if check_optimal(road.xpath[i : i + 4]):
                continue
            else:
                # swap
                road = Road(
                    road.path[: i + 1]
                    + (road.path[i + 2],)
                    + (road.path[i + 1],)
                    + road.path[i + 3 :]
                )
                need_optimize = True
                break
    return road


def check_optimal(path):
    # assume len(path) == 4
    a, b, c, d = path
    if (distance(a, b) + distance(b, c) + distance(c, d)) <= (
        distance(a, c) + distance(b, c) + distance(b, d)
    ):
        return True  # no change
    return False


def mix_roads(r1, r2):
    m = r1.first_half()
    return m.append_road(r2)


def test_road(cities):
    r1 = Road.random(cities)
    print(r1)
    print(r1.length)
    r2 = Road.random(cities)
    print(r2)
    print(r2.length)
    print("shorter:", r2.shorter_than(r1))
    r = r1.first(4)
    print("first 4:")
    print(r)
    rr = r.append_road(r2)
    print(rr)
    print("mix:")
    print(mix_roads(r1, r2))
    print("==")
    print(r1 == r2)
    print(r1 == r1)
    r3 = Road(r1.path)
    print(r3)
    print(r1 == r3)


if __name__ == "__main__":
    test_road(world_cities(Parameters()))
