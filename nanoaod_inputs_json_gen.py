import ROOT

import argparse
import json
import os

PROCS_FOLDERS: list[str] = {
    "ttbar__nominal": ("TT_TuneCUETP8M1_13TeV-powheg-pythia8",),
    "ttbar__scaledown": ("TT_TuneCUETP8M1_13TeV-powheg-scaledown-pythia8",),
    "ttbar__scaleup": ("TT_TuneCUETP8M1_13TeV-powheg-scaleup-pythia8",),
    "ttbar__ME_var": ("TT_TuneCUETP8M1_13TeV-amcatnlo-pythia8",),
    "ttbar__PS_var": ("TT_TuneEE5C_13TeV-powheg-herwigpp",),
    "single_top_s_chan__nominal": ("ST_s-channel_4f_InclusiveDecays_13TeV-amcatnlo-pythia8",),
    "single_top_t_chan__nominal": ("ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1", "ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1"),
    "single_top_tW__nominal": ("ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1", "ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1"),
    "wjets__nominal": ("WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",),
}


def get_entries(filename: str, dataset_name: str) -> int:
    with ROOT.TDirectory.TContext(), ROOT.TFile.Open(filename) as f:
        dataset = f.Get("Events")
        if isinstance(dataset, ROOT.TTree):
            return dataset.GetEntries()
        elif isinstance(dataset, ROOT.Experimental.RNTuple):
            reader = ROOT.Experimental.RNTupleReader.Open(dataset)
            return reader.GetNEntries()

    raise RuntimeError(f"Could not find '{dataset_name}' in '{filename}'")


def main(basedir: str) -> None:
    json_dict = {}
    for key, folders in PROCS_FOLDERS.items():
        process, variation = key.split("__")
        nevts_total = 0
        files_info = []
        for folder in folders:
            absdir = os.path.join(basedir, folder)
            if not os.path.exists(absdir) or not os.path.isdir(absdir):
                raise RuntimeError(f"Error finding directory '{absdir}'.")
            filenames = os.listdir(absdir)
            for basename in filenames:
                filename = os.path.join(absdir, basename)
                nevts = get_entries(filename, "Events")
                nevts_total += nevts
                filename = filename.replace("/data/AGC/rntuple-zstd-condensed-2x/nanoAOD", "root://eospublic.cern.ch//eos/root-eos/AGC/rntuple-zstd-condensed-2x/nanoAOD")
                files_info.append({
                    "path": filename,
                    "nevts": nevts,
                })

        if not json_dict.get(process, False):
            json_dict[process] = {variation: {
                "nevts_total": nevts_total, "files": files_info}}
        else:
            json_dict[process][variation] = {
                "nevts_total": nevts_total, "files": files_info}

    with open("inputs.json", "w") as f:
        json.dump(json_dict, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "basedir", help="Base directory to start the data retrieval.")
    args = parser.parse_args()
    raise SystemExit(main(args.basedir))

