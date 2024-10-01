import shlex
from pathlib import Path
import subprocess

import ROOT
import multiprocessing

def recompress_single_file(inputfile, treename, outputfile, compression_settings=505):
    """
    Convert a TTree with name `treename` from `inputfile` to the same TTree with different compression settings as specified by the input argument in `outputfile`
    """
    # This does not work because of a bug in rootcp
#    subprocess.run(shlex.split(f"rootcp -c {compression_settings} {inputfile}:{treename} {outputfile}"), check=True)
    # Use CloneTree instead of rootcp
    # Try with same clustering as input file
    # Use CloneTree(0) and loop on all branches to set the compression settings
    with ROOT.TFile(inputfile) as fin, ROOT.TFile(outputfile, "recreate", "", compression_settings) as fout:
        intree = fin.Get("Events")
        outtree = intree.CloneTree(0) # nentries = 0 only clones the dataset schema
        for branch in outtree.GetListOfBranches():
            branch.SetCompressionSettings(compression_settings)
        outtree.CopyEntries(intree)
        fout.WriteObject(outtree, outtree.GetName())

def recompress_sequential(treename, inputfiles, outputfiles):
    nfiles = 0
    for i, o in zip(inputfiles, outputfiles):
        nfiles += 1
        print(f"\n\nStarting conversion {nfiles}\n\tinput: {i}\n\toutput: {o}\n\n")
        if not os.path.exists(o):
            convert_single_file(i, treename, o)
        else:
            print("\tFile exists, not overwriting it.\n")

def recompress_multiprocess(treename, inputfiles, outputfiles):
    treenames = [treename] * len(outputfiles)
    with multiprocessing.Pool(64) as pool:
        pool.starmap(convert_single_file, zip(inputfiles, treenames, outputfiles))

def main():

    treename = "Events"

    inputdirs = [ p for p in Path("/data/agc-nanoaod/rdf-cache/nanoAOD").rglob("*") if p.is_dir()]
    outputdirs = [ Path(str(p).replace("rdf-cache", "ttree-zstd")) for p in inputdirs]
    for d in outputdirs:
        if not os.path.exists(d):
            d.mkdir(parents=True)

    inputfiles = [ str(p) for p in Path("/data/agc-nanoaod/rdf-cache/nanoAOD").rglob("*") if p.is_file()]
    outputfiles = [ p.replace("rdf-cache", "ttree-zstd") for p in inputfiles]
    recompress_multiprocess(treename, inputfiles, outputfiles)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
