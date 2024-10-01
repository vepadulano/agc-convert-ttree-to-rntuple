#!/usr/bin/env python

"""Command line tool to convert AGC nanoAODs to RNTuple"""

import os
from pathlib import Path
from pprint import pprint

def main():

    inputdirs = [ p for p in Path("/data/agc-nanoaod/rdf-cache/nanoAOD").rglob("*") if p.is_dir()]
    inputfiles = [ str(p).split("nanoAOD/")[1] for p in Path("/data/agc-nanoaod/rdf-cache/nanoAOD").rglob("*") if p.is_file()]

    with open("filelist.txt","w") as f:
        for path in inputfiles:
            f.write(f"{path}\n")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
