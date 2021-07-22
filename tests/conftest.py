import os
import shutil
import pytest
from pathlib import Path


def create_dirs(*args):
    for dir in args:
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)


class Dict2Class(object):
    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])


def pytest_configure():
    pytest.data_dir = Path.cwd() / 'tests' / 'data'
    pytest.out_dir = Path.cwd() / 'tests' / 'data' / 'tmp' / 'niffler-tests'
    pytest.create_dirs = create_dirs
    pytest.Dict2Class = Dict2Class

@pytest.fixture(scope="session", autouse=True)
def delete_out_dir():
    yield
    shutil.rmtree(pytest.out_dir.parent)