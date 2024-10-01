import os
import shlex
from pathlib import Path
import subprocess

import ROOT
import multiprocessing

def copy_events_ttree(inputfile, outputfile):
    """
    Copy the 'Events' TTree from the input file to the output file.
    """
    treename = "Events"
    subprocess.run(shlex.split(f"rootcp {inputfile}:{treename} {outputfile}"), check=True)

def main():

    inputdirs = [ p for p in Path("/data/agc-nanoaod/rdf-cache/nanoAOD").rglob("*") if p.is_dir()]
    outputdirs = [ Path(str(p).replace("/data/agc-nanoaod/rdf-cache", "/data/AGC/events-zlib")) for p in inputdirs]
    for d in outputdirs:
        if not os.path.exists(d):
            d.mkdir(parents=True)

    inputfiles = [ str(p) for p in Path("/data/agc-nanoaod/rdf-cache/nanoAOD").rglob("*") if p.is_file()]
    outputfiles = [ p.replace("/data/agc-nanoaod/rdf-cache", "/data/AGC/events-zlib") for p in inputfiles]
    with multiprocessing.Pool(64) as pool:
        pool.starmap(copy_events_ttree, zip(inputfiles, outputfiles))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
