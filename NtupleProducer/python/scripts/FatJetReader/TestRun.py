#!/usr/bin/env python
# encoding: utf-8

# File        : Reader.py
# Author      : Zhenbin Wu
# Contact     : zhenbin.wu@gmail.com
# Date        : 2017 Sep 26
#
# Description : 

from __future__ import print_function
from __future__ import division
from rootpy.io import root_open
from rootpy.tree import Tree,TreeChain
from rootpy.interactive import wait
from rootpy.plotting import Hist,Canvas
from rootpy.plotting.style import get_style
from AK8JetReader import AK8JetReader
from GenJetReader import GenJetReader
from collections import defaultdict
from Ploter import *
import rootpy.stl as stl
import rootpy
import argparse
import ROOT
import pprint
import glob
import pickle


def GetTree(f, treename):
    folder = getattr(f, treename, None)
    if folder is not None:
        return folder.tree

def Test():
    tt = Tree()
    tt.glob()

def LoadTree():
    global treemap
    global ak8map
    global genmap
    for k, fname in filename.items():
        t = {}
        ak8map[k] = {}
        for g, v in treename.items():
            t[g] = ROOT.TChain('%s/tree' % v)
            for j in glob.glob(fname):
                t[g].Add(j)
            if g != 'gen':
                ak8map[k][g] = AK8JetReader(t[g], v)
            if g == 'gen':
                genmap[k] = GenJetReader(t[g], v)
        treemap[k] = t

if __name__ == "__main__":
    ROOT.gROOT.SetBatch()
    folder = "/eos/uscms/store/user/benwu/Phase2L1/FatJet/Nov10SeedJet_v4/"
    filename = {
        # "QCD_PU0"     : "%s/QCD_PU0*.root"       % folder,
        "QCD_PU140"   : "%s/QCD_PU140*.root"     % folder,
        # "TTbar_PU140" : "%s/TTbar_PU140*.root"   % folder,
        # "TTbar_PU0"   : "%s/TTbar_PU0*.root"     % folder,
        # "MinBias_PU140" : "%s/MinBias_PU140_*.root"   % folder,
    }

    treename     = {
        'gen'        : 'GenJet',
        # 'ak8TKVtx'   : 'myak8TKVtx',
        # 'ak8TK'      : 'myak8TK',
        # 'ak8Puppi'   : 'myak8Puppi',
        # 'ak8PF'      : 'myak8PF',
        # 'ak8Calo'    : 'myak8Calo',
        # 'ak8RawCalo' : 'myak8RawCalo',
        'AK_PF4'      : 'myak4PF',
        'SISCone_PF4'      : 'mysc4PF',
        'Seed2_PF4'      : 'Seed2_PF',
        'Seed3_PF4'      : 'Seed3_PF',
    }

    # Create a map of TTree
    treemap = defaultdict(dict)
    ak8map = defaultdict(dict)
    genmap = defaultdict(dict)
    LoadTree()

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('process', nargs='*', default='TTbar_PU0', help='Select the process for run')
    args = parser.parse_args()

    processes = args.process
    
    for process in processes:
        for i in xrange(treemap[process].values()[0].GetEntries()):
            if i % 500 == 0 :
                print("Processed %d" % i)
            if i > 20000 :
                break
            ## No Accessing to Tchain friend in PyROOT :-(
            [ tr.GetEntry(i) for tr in  treemap[process].values() ]

            # genmap[process].Run()
            # genTops = genmap[process].topjets
            # genWs = genmap[process].Wjets
            # genLeps = genmap[process].Lepjets
            for tr in ak8map[process].keys():
                ak8map[process][tr].Run()

            akj1 = ak8map[process]['AK_PF4'].GetJet(1)
            akj2 = ak8map[process]['AK_PF4'].GetJet(2)
            akj3 = ak8map[process]['AK_PF4'].GetJet(3)
            akj4 = ak8map[process]['AK_PF4'].GetJet(4)
            for tr in ak8map[process].keys():
                ak8map[process][tr].PlotRelation(1, akj1)
                ak8map[process][tr].PlotRelation(2, akj2)
                ak8map[process][tr].PlotRelation(3, akj3)
                ak8map[process][tr].PlotRelation(4, akj4)


                # ak8map[process][tr].PlotTopMatchedJet(genTops, genLeps)
                # ak8map[process][tr].PlotWMatchedJet(genWs, genLeps)

    # Getting back the historgram
    histmap = defaultdict(dict)
    for process in processes:
            histmap[process]["Gen"] = genmap[process].GetHist()
            for tr in  ak8map[process].keys():
                histmap[process][tr] = ak8map[process][tr].GetHist()

    pprint.pprint(histmap)
    pickle.dump(histmap, open("%s.p" % args.process[0], "wb"))
