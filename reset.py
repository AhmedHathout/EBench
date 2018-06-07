#!/usr/bin/env python3

from os.path import dirname
from libraries_paths.libraries_paths import provers_library
import shutil

if __name__ == '__main__':
    shutil.rmtree(dirname(dirname(provers_library)), True)