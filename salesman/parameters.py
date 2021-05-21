#!/usr/bin/env python
from dataclasses import dataclass, asdict, field
import os
from copy import deepcopy
from os.path import join, exists, expanduser
import yaml


PARAMS = "params.yml"
DEFAULT_PARAMS = {
    "data_path": "~/tmp/salesman/data",
    "nb_cities": 100,
    "size_x": 1000,
    "size_y": 1000,
    "pool_size": 250,
    "pool_keep_best": 66,
    "pool_add_random": 33,
    "nb_rounds": 100,
}

HIGH_SCORE = "high_score.yml"


@dataclass
class Parameters:
    data_path: str = DEFAULT_PARAMS["data_path"]
    content: dict = field(default_factory=dict)

    def __post_init__(self):
        self.parse()

    def join(self, fname):
        return join(expanduser(self.data_path), fname)

    def ensure_data_dir(self):
        if not exists(expanduser(self.data_path)):
            os.makedirs(expanduser(self.data_path), exist_ok=True)

    def erase_high_score(self):
        path = self.join(HIGH_SCORE)
        no_score = {"length": 1e100, "path": None}
        self.ensure_data_dir()
        with open(path, "w") as f:
            yaml.dump(no_score, f)

    def set_high_score(self, road):
        path = self.join(HIGH_SCORE)
        self.ensure_data_dir()
        with open(path, "w") as f:
            yaml.dump({"length": road.length, "path": road.export_path()}, f)

    def read_high_score(self):
        path = self.join(HIGH_SCORE)
        self.ensure_data_dir()
        try:
            with open(path) as f:
                return yaml.load(f, yaml.SafeLoader)["path"]
        except (ValueError, KeyError, IOError):
            return None

    @property
    def path_params(self):
        return join(expanduser(self.data_path), PARAMS)

    def make_default_file(self):
        if exists(self.path_params):
            return
        self.content = deepcopy(DEFAULT_PARAMS)
        self.save()

    def save(self):
        self.content["data_path"] = expanduser(self.data_path)
        self.ensure_data_dir()
        with open(self.path_params, "w") as f:
            yaml.dump(self.content, f)

    def parse(self):
        self.make_default_file()
        with open(self.path_params) as f:
            self.content = yaml.load(f, yaml.SafeLoader)

    def get(self, key):
        if not self.content:
            self.parse()
        return self.content.get(key)

    def set(self, key, value):
        if not self.content:
            self.parse()
        self.content[key] = value
        if key == "data_path":
            self.data_path = value
        self.save()


if __name__ == "__main__":
    p = Parameters()
    print(asdict(p))
