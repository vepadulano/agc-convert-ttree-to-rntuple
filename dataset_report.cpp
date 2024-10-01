#include <TFile.h>
#include <TTree.h>
#include <ROOT/TThreadExecutor.hxx>
#include <ROOT/RNTupleInspector.hxx>
#include <ROOT/RPageStorage.hxx>
#include <ROOT/RNTupleDescriptor.hxx>

#include <memory>
#include <vector>
#include <utility>
#include <iostream>
#include <fstream>

std::vector<std::pair<ROOT::Experimental::NTupleSize_t, ROOT::Experimental::NTupleSize_t>>
get_clusters(ROOT::Experimental::RNTupleDescriptor &desc)
{
    std::vector<std::pair<ROOT::Experimental::NTupleSize_t, ROOT::Experimental::NTupleSize_t>> clusterBoundaries;
    clusterBoundaries.reserve(desc.GetNClusters());
    auto clusterId = desc.FindClusterId(0, 0);
    while (clusterId != ROOT::Experimental::kInvalidDescriptorId)
    {
        const auto &clusterDesc = desc.GetClusterDescriptor(clusterId);
        clusterBoundaries.emplace_back(clusterDesc.GetFirstEntryIndex(),
                                       clusterDesc.GetFirstEntryIndex() + clusterDesc.GetNEntries());
        clusterId = desc.FindNextClusterId(clusterId);
    }
    return clusterBoundaries;
}

void checks(std::string_view ntuplename, std::string_view ntuplefile)
{
    auto inspector = ROOT::Experimental::RNTupleInspector::Create(ntuplename, ntuplefile);

    auto descriptor = inspector->GetDescriptor();

    std::cout << "Number of clusters: " << descriptor->GetNClusters() << "\n";

    auto clusters = get_clusters(*descriptor);

    std::cout << "Cluster boundaries:\n\t{";
    for (auto &&[begin, end] : clusters)
        std::cout << "(" << begin << "," << end << ")";
    std::cout << "}\n";
}

void fill_line(std::string_view ntuplename, std::string_view ntuplefile, std::string &line)
{
    auto inspector = ROOT::Experimental::RNTupleInspector::Create(ntuplename, ntuplefile);

    auto compsize = inspector->GetCompressedSize();

    auto descriptor = inspector->GetDescriptor();

    auto nclusters = descriptor->GetNClusters();

    auto clusters = get_clusters(*descriptor);

    line = ntuplefile;
    line += "," + std::to_string(compsize) + "," + std::to_string(nclusters);
}

template <typename T>
void print_vector(const std::vector<T> &vec, std::string_view vecname = "")
{
    std::string_view name{vecname.empty() ? "vector" : vecname};
    std::cout << "Printing " << name << ":\n\t{";
    for (auto &&v : vec)
        std::cout << v << ",";
    std::cout << "}\n";
}

template <typename T>
void print_vector_newline(const std::vector<T> &vec, std::string_view vecname = "")
{
    std::string_view name{vecname.empty() ? "vector" : vecname};
    std::cout << "Printing " << name << ":\n";
    for (auto &&v : vec)
        std::cout << v << "\n";
}

std::vector<std::string> parse_dataset_filenames(std::string_view data)
{
    std::ifstream inputfile{data.data()};
    std::vector<std::string> filenames;
    if (!inputfile)
        throw std::runtime_error(std::string("Error opening file '") + data.data() + "'.");
    std::string line;
    while (std::getline(inputfile, line))
    {
        filenames.push_back(line);
    }
    return filenames;
}

std::vector<std::string> generate_filenames()
{
    std::string_view ntuplename{"Events"};
    std::string_view input{"filelist.txt"};
    auto &&filenames = parse_dataset_filenames(input);
    std::vector<std::string> xrootdpaths(filenames.size());
    std::generate(xrootdpaths.begin(), xrootdpaths.end(), [n = 0, &filenames]() mutable
                  { return "root://eospublic.cern.ch//eos/root-eos/AGC/rntuple/nanoAOD/" + filenames[n++]; });
    return xrootdpaths;
}

int main()
{
/*    std::string_view ntuplename{"Events"};
    auto xrootdpaths = generate_filenames();

    std::vector<std::string> lines(5);

    ROOT::TThreadExecutor pool;
    auto fun = [&ntuplename, &xrootdpaths, &lines](std::size_t file_idx)
    { fill_line(ntuplename, xrootdpaths[file_idx], lines[file_idx]); };
    pool.Foreach(fun, std::vector<std::size_t>({0,1,2,3,4}));

    print_vector_newline(lines, "lines");
  */
   checks("Events", "/data/AGC/condensed-rntuple-zstd/nanoAOD/ST_s-channel_4f_InclusiveDecays_13TeV-amcatnlo-pythia8/cmsopendata2015_single_top_s_chan_19394_PU25nsData2015v1_76X_mcRun2_asymptotic_v12_0002.root");
   checks("Events","/data/agc-nanoaod/rntuple/nanoAOD/ST_s-channel_4f_InclusiveDecays_13TeV-amcatnlo-pythia8/cmsopendata2015_single_top_s_chan_19394_PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1_00000_0000.root");
}
