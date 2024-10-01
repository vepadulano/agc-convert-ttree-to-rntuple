#!/usr/bin/env python

"""Command line tool to convert AGC nanoAODs to RNTuple"""

import os
from pathlib import Path
from pprint import pprint
from typing import Iterable
import shlex
import subprocess
import multiprocessing

import ROOT

INPUT_FILES = [f for f in Path("/data/AGC/ttree-zlib-condensed-2x/nanoAOD").rglob("*") if f.is_file() ]


def check_same_entries(outputfile: Path, inputfiles: list[Path]):
    input_entries = 0
    for fn in inputfiles:
        with ROOT.TDirectory.TContext(), ROOT.TFile.Open(str(fn)) as f:
            tree = f.Get("Events")
            input_entries += tree.GetEntries()

    with ROOT.TDirectory.TContext(), ROOT.TFile.Open(str(outputfile)) as out:
        tree = out.Get("Events")
        output_entries = tree.GetEntries()

    if output_entries != input_entries:
        raise RuntimeError(f"{output_entries=}!={input_entries=} for files:\n\t{inputfiles=}\n\t{outputfile=}")
    else:
        print(f"\n{output_entries=}=={input_entries=} for files:\n\t{inputfiles=}\n\t{outputfile=}\n")

    entries_fn = os.path.join(CHECK_ENTRIES_DIR, str(hash(outputfile)) + "__" + str(output_entries))

    with open(entries_fn, "w") as f:
        f.write("")

def check_equality(haddinputs, inputfiles):
    flatinputs = [f for l in haddinputs for f in l]
    assert all(a == b for a, b in zip(flatinputs, inputfiles)), f"{a}, {b}"

def check_all_files_present(args_alldirs):
    all_paths_flat = [path for args in args_alldirs for path in args[0]]
    assert len(all_paths_flat) == len(INPUT_FILES), f"{len(all_paths_flat)=},{len(INPUT_FILES)=}"
    for haddfile, inputfile  in zip(all_paths_flat, INPUT_FILES):
        assert haddfile == inputfile, f"{haddfile=},{inputfile=}"

def get_entries(path: Path, dataset_name = "Events"):
    with ROOT.TDirectory.TContext(), ROOT.TFile.Open(str(path)) as f:
        dataset = f.Get(dataset_name)
        if isinstance(dataset, ROOT.TTree):
            return dataset.GetEntries()
        elif isinstance(dataset, ROOT.Experimental.RNTuple):
            reader = ROOT.Experimental.RNTupleReader.Open(dataset)
            return reader.GetNEntries()
        
        raise RuntimeError("Did not recognize dataset type")

def main():    
#    inputfiles = [f for f in Path("/data/AGC/ttree-zlib-condensed-2x/nanoAOD").rglob("*") if f.is_file() ]
    inputfiles = [f for f in Path("/data/AGC/rntuple-zstd-condensed-2x/nanoAOD").rglob("*") if f.is_file() ]
    inputdirs = [d for d in Path("/data/AGC/rntuple-zstd-condensed-2x/nanoAOD").rglob("*") if d.is_dir() ]
    with open("dataset_nanoaod_entries_rntuple-zstd-condensed-2x.txt", "a") as f:
        f.write(f"directory,nfiles,nentries\n")
    for inputdir in inputdirs:
        dirfiles = [f for f in inputdir.rglob("*") if f.is_file()]
        direntries = sum(get_entries(fn) for fn in dirfiles)
        with open("dataset_nanoaod_entries_rntuple-zstd-condensed-2x.txt", "a") as f:
            f.write(f"{inputdir},{len(dirfiles)},{direntries}\n")

    entries_total = sum(get_entries(fn) for fn in inputfiles)
    with open("dataset_nanoaod_entries_rntuple-zstd-condensed-2x.txt", "a") as f:
        f.write(f"\nTotal: nfiles={len(inputfiles)},nentries={entries_total}\n")

    assert entries_total == 940160174, f"{entries_total=}!=940160174"

if __name__ == "__main__":
    raise SystemExit(main())
