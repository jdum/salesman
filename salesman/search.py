#!/usr/bin/env python
"""
Knapsack Solver with basic genetic algo
Dont expect docstring!
"""
from random import choice
from time import time

from .parameters import Parameters
from .road import Road, mix_roads
from .city import world_cities


def line():
    print("-" * 80)


def spent(t0, t):
    m, s = divmod(t - t0, 60)
    m = int(m)
    if m == 0:
        return f"{s:.3f}s"
    return f"{m}m{s:.3f}s"


def uniq(pool):
    # uniq on sorted list
    if not pool:
        return pool
    result = [pool[0]]
    for s in pool:
        if s != result[-1]:
            result.append(s)
    return result


def sort_pool(pool):
    sdpool = sorted((r.length, r) for r in pool)
    return list(x[1] for x in sdpool)


def init_pool(p):
    cities = world_cities(p)
    pool = list(Road.random(cities) for _i in range(p.get("pool_size")))
    print(f"generated {len(pool)} random paths")
    return pool


def top_half_average(pool):
    top = len(pool) // 2
    return sum(i.length for i in pool[:top]) / top


def print_bests(top_average, pool):
    print(f"best of pool of {len(pool)}:")
    print("    ", pool[0].short_repr())
    print("    ", pool[1].short_repr())
    print("    ", pool[2].short_repr())
    print(f"average value top half: {top_average:,}")


def next_generation(round_nb, p, pool):
    # assume pool is sorted
    # remove the bad scores, keep the high scores:
    pool = pool[: p.get("pool_keep_best")]  # keep high scores
    # add some random to the pool, aka ~mutation,
    nb_random = p.get("pool_add_random")
    cities = world_cities()
    for _i in range(nb_random):
        pool.append(Road.random(cities))
    # generate the pool by mixing
    # of 50% bests + 20 random
    new_pool = []
    uniq_try = 5
    while len(new_pool) < p.get("pool_size") and uniq_try > 0:
        while len(new_pool) < p.get("pool_size"):
            cpt_err = 0
            while True:
                a = choice(pool)
                b = choice(pool)
                if a != b:
                    break
                cpt_err += 1
                if cpt_err >= 10:
                    break
            new_pool.append(mix_roads(a, b))
        new_pool = uniq(sort_pool(new_pool))
        uniq_try -= 1
    pool = new_pool
    line()
    print("round", round_nb)
    top_average = top_half_average(pool)
    print_bests(top_average, pool)
    return pool


def main():
    p = Parameters()
    t0 = time()
    print("generate pool...")
    pool = sort_pool(init_pool(p))
    print(spent(t0, time()))
    high_score_path = p.read_high_score()
    if high_score_path is None:
        high_score = 1e100
        winner = None
    else:
        winner = Road.from_list(high_score_path)
        high_score = winner.length
    for r in pool:
        print(r.length)
    line()
    for i in range(1, p.get("nb_rounds") + 1):
        t1 = time()
        pool = next_generation(i, p, pool)
        # more_random = bool(top_average <= last_average)
        # last_average = top_average
        if pool[0].length < high_score:
            winner = pool[0]
            high_score = pool[0].length
            print("TOP:", winner.short_repr())
        else:
            print("top:", winner.short_repr())
        t = time()
        print(spent(t1, t), "cumul:", spent(t0, t), "av:", spent(0.0, (t - t0) / i))
    p.set_high_score(winner)


if __name__ == "__main__":
    main()
