#!/usr/bin/env python
# encoding: utf-8

# File        : Ploter.py
# Author      : Zhenbin Wu
# Contact     : zhenbin.wu@gmail.com
# Date        : 2017 Sep 29
#
# Description : 


import pickle
import glob
import pprint
import numpy as np
import matplotlib.pyplot as plt
import pandas
from rootpy.plotting import Hist,Legend, Canvas
from rootpy.plotting.utils import draw
from rootpy.interactive import wait
import tdrstyle
from itertools import compress
import rootpy
import re
import ROOT
from collections import defaultdict


#============================================================================#
#--------------------------     Drawing Config     --------------------------#
#============================================================================#
PyMarkers = [20, 21, 22, 23, 29, 33, 34]
PyColors = [
    ROOT.TColor.GetColor(228,26,28),
    ROOT.TColor.GetColor(55,126,184),
    ROOT.TColor.GetColor(77,175,74),
    ROOT.TColor.GetColor(152,78,163),
    ROOT.TColor.GetColor(255,127,0),
    # ROOT.TColor.GetColor(255,255,51),
    ROOT.TColor.GetColor(166,86,40),
    ROOT.TColor.GetColor(247,129,191),
    ROOT.TColor.GetColor(153,153,153),
    ROOT.kBlack,
    ROOT.kRed,
    ROOT.kBlue,
    ROOT.kGreen-2,
    ROOT.kOrange,
    ROOT.kCyan,
    ROOT.kMagenta,
    ROOT.kYellow,
    ROOT.kGreen,
    ROOT.kGray,
    ROOT.kSpring,
    ROOT.kTeal,
    ROOT.kAzure,
    ROOT.kViolet,
    ROOT.kPink
]


def walk_dict(idict, slic, depth, name=""):
    global retdict
    for key in idict.keys():
        pat = slic[depth]
        if pat == '*':
            pat = '.*'
        pat = "^" + pat +"$" ## Make sure exact match
        if re.match(pat, key) is None:
            continue
        if isinstance(idict[key], dict):
            walk_dict(idict[key], slic, depth+1, "%s_%s" % (name, key))
        else:
            retdict["%s_%s"% (name, key)] = idict[key]

def SliceDict(idict, sel):
    slic = sel.split(':')
    walk_dict(idict, slic, 0)
    ## Remove leading _
    for k, v in retdict.items():
        newk = k[1:]
        retdict[newk] = retdict.pop(k)
    return retdict


def CorrectLegend(plotdict):
    newdict = {}
    newleg = {}
    for k in plotdict.keys():
        newleg[k] = k.split("_")

    coms = None
    remlist = []
    for k in newleg.values():
        if coms is None:
            coms = k
            remlist= [True]*(len(k))
            continue
        for i in range(len(k)):
            if coms[i] != k[i]:
                remlist[i] = False
                remlist.append(i)

    recoms = list(compress(coms, remlist))

    for k in plotdict.keys():
        newk = list(compress(newleg[k], np.logical_not(remlist)))
        plotdict['_'.join(newk)] = plotdict.pop(k)
    return '_'.join(recoms)


def UpdateColor(hists):
    xtitle = hists[0].GetXaxis().GetTitle()
    ytitle =  hists[0].GetYaxis().GetTitle()
    for i in range(len(hists)):
        hists[i].SetLineColor(PyColors[i])
        hists[i].SetMarkerColor(PyColors[i])
        if hists[i].GetNbinsX() < 10:
            hists[i].SetMarkerSize(2)
            hists[i].SetMarkerStyle(PyMarkers[i] if i <= len(PyMarkers) else i)
        else:
            hists[i].SetLineWidth(3)
            hists[i].legendstyle = 'l'
            # hists[i].SetMarkerSize(1)
    return xtitle, ytitle

def PlotComp(plotdict, comname):
    tdrstyle.setTDRStyle()
    canvas = Canvas(width=700, height=500)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.10)
    canvas.SetRightMargin(0.05)

    hists = []
    for k,v in plotdict.items():
        v.SetTitle(k)
        hists.append(rootpy.asrootpy(v))
    xtitle, ytitle = UpdateColor(hists)
    if "Rate" in comname:
        draw(hists[:], xtitle=xtitle, ytitle=ytitle, ylimits=(1, 100000), logy=True)
        line = ROOT.TLine(0, 42, 1000, 42)
        line.SetLineWidth(2)
        line.SetLineColor(2)
        line.SetLineStyle(2)
        line.Draw()
        line = ROOT.TLine(0, 21, 1000, 21)
        line.SetLineColor(1)
        line.SetLineStyle(2)
        line.Draw()
    else:
        draw(hists[:], xtitle=xtitle, ytitle=ytitle, logy=False)

    ## Legend
    legend = Legend(hists, leftmargin=0.55, margin=0.2)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextFont(62)
    legend.SetTextSize(0.045)
    legend.Draw()
    ## Title
    label = ROOT.TText(0.15, 0.92, comname)
    label.SetTextFont(43)
    label.SetTextSize(25)
    label.SetNDC()
    label.Draw()
    canvas.Modified()
    canvas.Update()
    canvas.SaveAs("plots/%s.png" % comname)
    canvas.SaveAs("plots/%s.pdf" % comname)
    canvas.SaveAs("plots/%s.root" % comname)
    # wait()

def GetProcesses(p):
    return p.keys()

def GetType(p):
    return p.itervalues().next().keys()

def GetHistNames(p):
    return p.itervalues().next().itervalues().next().keys()

if __name__ == "__main__":

    ROOT.gROOT.SetBatch()
    # p = pickle.load(open('./TTbar_PU140.p', 'rb'))
    p = pickle.load(open('./QCD_PU140.p', 'rb'))
    # p = pickle.load(open('./MinBias_PU140.p', 'rb'))
    # p = pickle.load(open('./TTbar_PU0.p', 'rb'))
    print(GetProcesses(p))
    print(GetType(p))
    print(GetHistNames(p))
    # selection = "*:*:Tau32Pt200"
    for h in GetHistNames(p):
        # if "Rate" not in h:
            # continue
        selection = "*:*:%s" % h
        retdict = {}
        plotdict = SliceDict(p, selection )
        comname = CorrectLegend(plotdict)
        PlotComp(plotdict, comname)

