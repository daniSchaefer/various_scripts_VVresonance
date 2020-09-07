#time combine -M GoodnessOfFit /portal/ekpbms2/home/dschaefer/DiBoson3D/workspace_JJ_BulkGWW_13TeV.root --algo=saturated -t 10 -s -1 --toysFreq

import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
import CMS_lumi 
import tdrstyle
tdrstyle.setTDRStyle()

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetLegendBorderSize(0)


parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output ROOT File",default='')
parser.add_option("-f","--firstfile",dest="firstfile",help="Input ROOT File",default='')
parser.add_option("-s","--secondfile",dest="secondfile",help="Input ROOT File",default='')
parser.add_option("-l","--label",dest="label",help="label",default='')


(options,args) = parser.parse_args()

def getCanvas(w=600,h=600):
    c1 = ROOT.TCanvas("c","",w,h)
    c1.SetBottomMargin(0.15)
    c1.SetTopMargin(0.08)
    c1.SetRightMargin(0.08)
    return c1




def getLimit(filename):
    f=ROOT.TFile(filename)
    limit=f.Get("limit")
    data=[]
    for event in limit:
        if event.quantileExpected<0:            
            data.append(event.limit)  #*0.01
    return data


def calcPValue(func,v,vmin,vmax):
    p = func.Integral(v,vmax)/func.Integral(vmin,vmax)
    return p 


if __name__=="__main__":
    
    ldist = getLimit(options.firstfile)
    l     = getLimit(options.secondfile)
    
    #print ldist
    print l

    ldist.sort()
    histo = ROOT.TH1F("dist","",100,ldist[0],max(l[0],ldist[-1]))
    histo.SetLineColor(ROOT.kBlack)
    histo.SetLineWidth(2)
    histo.GetXaxis().SetTitle("value of test-statistic")
    histo.GetYaxis().SetTitle("number of toys")
    histo.GetYaxis().SetTitleOffset(1.4)
    histo.GetXaxis().SetNdivisions(5,5,0)
    histo.GetYaxis().SetRangeUser(0,500)
    for i in ldist:
        histo.Fill(i)
        
        
    histo.Fit("gaus","LM")
     
     
    print " fit mean "+str(histo.GetMean())+" obs "+str(l) 
     
    c = getCanvas()
    #histo.SetNdivisions(6)
    histo.SetStats(False)
    histo.Draw("hist")
    fdit = histo.GetFunction("gaus")
    fdit.SetLineColor(ROOT.kBlue)
    fdit.SetLineWidth(2)
    fdit.Draw("same")
    
    pv = calcPValue(fdit,l[0],ldist[0],max(l[0],ldist[-1]))
    y = histo.Integral()/50.
    p = ROOT.TLine(l[0],0,l[0],y)
    p.SetLineColor(ROOT.kRed)
    p.SetLineWidth(4)
    p.Draw("same")
    leg = ROOT.TLegend(0.50,0.91,0.85,0.7)
    leg.SetHeader("background-only fit, p-val "+str(round(pv,2)))
    leg.SetTextFont(42)
    leg.SetTextSize(0.03)
    
    name = "observed value"
    if options.secondfile.find("PYTHIA")!=-1:
        name = "observed PYTHIA"
    if options.secondfile.find("HERWIG")!=-1:
        name = "observed HERWIG++"    
    if options.secondfile.find("MADGRAPH")!=-1:
        name = "observed MADGRAPH"
    if options.secondfile.find("POWHEG")!=-1:
        name = "observed POWHEG"
    leg.AddEntry(histo,"test-statistic","l")
    leg.AddEntry(fdit,"fit ","l")
    leg.AddEntry(p,name,"l")
    leg.Draw("same")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.2,0.75,options.label)
    CMS_lumi.text = ""
    CMS_lumi.extraText ="Simulation"
    CMS_lumi.cmslabel_ncms(c,"2016+2017",10)
    c.SaveAs("gof_"+options.output+".pdf")
    
    
    
    print pv
    
