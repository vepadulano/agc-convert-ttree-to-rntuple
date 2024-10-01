import ROOT

treename = "Events"
treefile = "/data/agc-nanoaod/rdf-cache/nanoAOD/ST_s-channel_4f_InclusiveDecays_13TeV-amcatnlo-pythia8/cmsopendata2015_single_top_s_chan_19394_PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1_00000_0000.root"

with ROOT.TFile(treefile) as f:
    tree = f.Get(treename)
    branches = tree.GetListOfBranches()
    print(branches.GetEntries())
    compsettings = [branch.GetCompressionSettings() for branch in branches]

from pprint import pprint
pprint(compsettings)
