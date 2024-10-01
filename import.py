import os
from pathlib import Path
from pprint import pprint
import multiprocessing
import ROOT

def import_single_file(treename: str, inputfile: Path, outputfile: Path, compression_settings=505):
    """
    Import a TTree with name `treename` from `inputfile` to an RNTuple with the same name to `outputfile`. The default compression setting is ZSTD level 5 (as suggested by the docs).
    """

    importer = ROOT.Experimental.RNTupleImporter.Create(str(inputfile), treename, str(outputfile))

    wrtopts = importer.GetWriteOptions()
    wrtopts.SetCompression(compression_settings)

    importer.SetWriteOptions(wrtopts)
    importer.SetIsQuiet(True)
    importer.Import()

def import_sequential(treename, inputfiles, outputfiles):
    nfiles = 0
    for i, o in zip(inputfiles, outputfiles):
        nfiles += 1
        print(f"\n\nStarting import {nfiles}\n\tinput: {i}\n\toutput: {o}\n\n")
        import_single_file(treename, i, o)

def import_multiprocess(treename, inputfiles, outputfiles):
    with multiprocessing.Pool(64) as pool:
        pool.starmap(import_single_file, zip([treename] * len(inputfiles), inputfiles, outputfiles))

def main():

    treename = "Events"
    input_rootdir = "/data/AGC/ttree-zlib-condensed-2x"
    output_rootdir = "/data/AGC/rntuple-zstd-condensed-2x"

    inputdirs = [ p for p in Path(input_rootdir).rglob("*") if p.is_dir()]
    outputdirs = [ Path(str(p).replace(os.path.basename(input_rootdir), os.path.basename(output_rootdir))) for p in inputdirs]
    for d in outputdirs:
        if not os.path.exists(d):
            d.mkdir(parents=True)

    inputfiles = [ p for p in Path(input_rootdir).rglob("*") if p.is_file()]
    outputfiles = [ Path(str(p).replace(os.path.basename(input_rootdir), os.path.basename(output_rootdir))) for p in inputfiles]

    import_multiprocess(treename, inputfiles, outputfiles)


if __name__ == "__main__":
    raise SystemExit(main())
