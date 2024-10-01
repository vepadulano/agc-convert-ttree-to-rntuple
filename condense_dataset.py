import os
from pathlib import Path
from pprint import pprint
from typing import Iterable
import shlex
import subprocess
import multiprocessing

import ROOT

INPUT_DIRS = [d for d in Path("/data/AGC/events-ttree-zlib/nanoAOD").rglob("*") if d.is_dir() ]
INPUT_FILES = [f for f in Path("/data/AGC/events-ttree-zlib/nanoAOD").rglob("*") if f.is_file() ]

CHECK_ENTRIES_DIR = os.path.join(os.getcwd(), "entries_files")

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

def condense_files(inputfiles: list[Path], outputfile: Path, target_dir: Path):
    targetfile = os.path.join(target_dir, outputfile)
    subprocess.run(shlex.split(f"hadd {targetfile} {' '.join([str(f) for f in inputfiles])}"), check=True)
    check_same_entries(targetfile, inputfiles)

def check_equality(haddinputs, inputfiles):
    flatinputs = [f for l in haddinputs for f in l]
    assert all(a == b for a, b in zip(flatinputs, inputfiles)), f"{a}, {b}"

def check_all_files_present(args_alldirs):
    all_paths_flat = [path for args in args_alldirs for path in args[0]]
    assert len(all_paths_flat) == len(INPUT_FILES), f"{len(all_paths_flat)=},{len(INPUT_FILES)=}"
    for haddfile, inputfile  in zip(all_paths_flat, INPUT_FILES):
        assert haddfile == inputfile, f"{haddfile=},{inputfile=}"

def main():

    outputdirs = [ Path(str(p).replace("/data/AGC/events-ttree-zlib", "/data/AGC/ttree-zlib-condensed-2x")) for p in INPUT_DIRS]
    for d in outputdirs:
        if not os.path.exists(d):
            d.mkdir(parents=True)

    args_alldirs = []
    for inputdir, outputdir in zip(INPUT_DIRS, outputdirs):
        inputfiles: list[Path] = [ p for p in inputdir.rglob("*") if p.is_file() ]
        haddinputs: list[Path] = [inputfiles[i:i+2] for i in range(0,len(inputfiles),2)]
        basename = str(haddinputs[0][0].name).rsplit('-',1)[0] + "_{0:04d}.root"
        outputs: list[Path] = [Path(basename.format(i)) for i in range(len(haddinputs))]

        check_equality(haddinputs, inputfiles)

        args_alldirs.extend([
            (inputs, outputfile, outputdir) for inputs, outputfile in zip(haddinputs, outputs)           
        ]
        )

    check_all_files_present(args_alldirs)

    with multiprocessing.Pool(64) as pool:
        pool.starmap(condense_files, args_alldirs)

    entries_total = sum(int(fn.split("__")[1]) for fn in os.listdir(CHECK_ENTRIES_DIR))
    # Check number of total entries in the dataset
    assert entries_total == 823970761, f"{entries_total=}!=823970761"

if __name__ == "__main__":
    raise SystemExit(main())
