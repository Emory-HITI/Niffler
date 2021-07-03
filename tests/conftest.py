import os
import pytest
from pathlib import Path


def create_dirs(*args):
    for dir in args:
        if not os.path.exists(dir):
            os.makedirs(dir)


def pytest_configure():
    pytest.data_dir = Path.cwd() / 'tests' / 'data'
    pytest.out_dir = Path.cwd() / 'tests' / 'data' / 'tmp' / 'niffler-tests'
    pytest.create_dirs = create_dirs
