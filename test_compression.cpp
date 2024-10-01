#include <TFile.h>
#include <TTree.h>

#include <memory>

int main(){
    auto *treename{"Events"};
    auto *filename{"/data/agc-nanoaod/ttree-zstd/nanoAOD/ST_s-channel_4f_InclusiveDecays_13TeV-amcatnlo-pythia8/cmsopendata2015_single_top_s_chan_19394_PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1_00000_0000.root"};
    std::unique_ptr<TFile> f{TFile::Open(filename)};
    std::unique_ptr<TTree> t{f->Get<TTree>(treename)};
    t->SetBranchStatus("*", 1);
    for (decltype(t->GetEntries()) i = 0; i < 1000; i++)
    {
        t->GetEntry(i);
    }
}
