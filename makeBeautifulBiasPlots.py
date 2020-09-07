import ROOT
import numpy
from array import array
import os, sys
import optparse
import numpy
#sys.path.append("/home/dschaefer/scripts/")
from  CMS_lumi import *
import tdrstyle
tdrstyle.setTDRStyle()

#arser = optparse.OptionParser()
#parser.add_option("-v","--variable",dest="variable",help="variable name to be used for example tau21, softdopmass",default='')
#(options,args) = parser.parse_args()
ROOT.gStyle.SetOptStat(0)

N=45

def beautify(graph,color,marker,title):
    graph.SetLineColor(color)
    graph.SetMarkerStyle(marker)
    graph.SetMarkerColor(color)
    graph.GetXaxis().SetTitle("Dijet invariant mass [GeV]")
    graph.GetYaxis().SetTitle(title)
    graph.GetYaxis().SetTitleSize(0.05)
    graph.GetYaxis().SetTitleOffset(1.1)
    graph.GetXaxis().SetTitleSize(0.05)
    graph.GetXaxis().SetTitleOffset(0.9)
    graph.GetXaxis().SetLabelSize(0.05)
    graph.GetYaxis().SetLabelSize(0.05)
    graph.GetXaxis().SetNdivisions(10)
    graph.GetYaxis().SetNdivisions(6,5,0)
    graph.GetXaxis().SetNdivisions(5,5,0)
    graph.SetMaximum(0.25)
    graph.SetMinimum(-0.25)
    return graph


def get_canvas(cname):

 H_ref = 600 
 W_ref = 600 
 W = W_ref
 H  = H_ref

 iPeriod = 0

 # references for T, B, L, R
 T = 0.08*H_ref
 B = 0.12*H_ref 
 L = 0.12*W_ref
 R = 0.04*W_ref

 canvas = ROOT.TCanvas(cname,cname,50,50,W,H)
 canvas.SetFillColor(0)
 canvas.SetBorderMode(0)
 canvas.SetFrameFillStyle(0)
 canvas.SetFrameBorderMode(0)
 canvas.SetLeftMargin( L/W )
 canvas.SetRightMargin( R/W )
 canvas.SetTopMargin( T/H )
 canvas.SetBottomMargin( B/H )
 canvas.SetTickx()
 canvas.SetTicky()
 
 return canvas

def getLegend(graphs,names):
    #l = ROOT.TLegend(0.3,0.7,0.9,0.3)
    l = ROOT.TLegend(0.55,0.86,0.9,0.7)
    l.SetTextFont(82)
    counter=0
    for g in graphs:
        l.AddEntry(g,names[counter],"lp")
        counter+=1
    return l



if __name__=="__main__":
    #filenames=["biasTest_fullBkg_pythiaHPHP_expSig3_moreSyst.root","biasTest_fullBkg_pythiaHPLP_expSig3_moreSyst.root","biasTest_fullBkg_pythiaLPLP_expSig3_moreSyst.root"]
    #names=["pythia HPHP toys","pythia HPLP toys","pythia LPLP toys"]
    
    
    #filenames=["biasTest_fullBkg_madgraphHPHP_expSig3_moreSyst.root","biasTest_fullBkg_herwigHPHP_expSig3_moreSyst.root","biasTest_fullBkg_NLOHPHP_expSig3_moreSyst.root","biasTest_fullBkg_pythiaHPHP_expSig3_moreSyst.root" ]
    #names=["herwig HPHP toys","madgraph HPHP toys","NLO HPHP toys",'pythia HPHP toys']
    
    ##filenames=["biasTest_fullBkg_herwigHPHP_expSig3_moreSyst.root","biasTest_fullBkg_herwigHPLP_expSig3_moreSyst.root","biasTest_fullBkg_herwigLPLP_expSig3_moreSyst.root" ]
    
    #filenames=["biasTest_fullBkg_herwigHPHP_expSig3_v3_moreSyst.root","biasTest_fullBkg_madgraphHPHP_expSig3_v3_moreSyst.root","biasTest_fullBkg_NLOHPHP_expSig3_v3_moreSyst.root","biasTest_fullBkg_pythiaHPHP_expSig3_v3_moreSyst.root" ]
    #names=["herwig HPHP toys","madgraph HPHP toys","NLO HPHP toys", "pythia HPHP toys"]
 

    
#    filenames=["biasTest_fullBkg_herwigHPLP_expSig3_moreSyst.root","biasTest_fullBkg_madgraphHPLP_expSig3_moreSyst.root","biasTest_fullBkg_NLOHPLP_expSig3_moreSyst.root","biasTest_fullBkg_pythiaHPLP_expSig3_moreSyst.root" ]
#    names=["herwig HPLP toys","madgraph HPLP toys","NLO HPLP toys", "pythia HPLP toys"]
    
    
    filenames=["biasTest_HPHP_ZprimeWW_pythia_2sigma.root","biasTest_HPLP_ZprimeWW_pythia_2sigma.root" ]
    names=["PYTHIA8","PYTHIA8"]
    label="pythia"
    
    
    #filenames=["biasTest_HPHP_ZprimeWW_herwig.root","biasTest_HPLP_ZprimeWW_herwig.root" ]
    #names=["HERWIG++","HERWIG++"]
    #label="herwig"
    
    
    #filenames=["biasTest_HPHP_ZprimeWW_madgraph.root","biasTest_HPLP_ZprimeWW_madgraph.root" ]
    #names=["MADGRAPH","MADGRAPH"]
    #label="madgraph"
    
    
    #filenames=["biasTest_HPHP_ZprimeWW_powheg_2sigma.root","biasTest_HPLP_ZprimeWW_powheg_2sigma.root" ]
    #names=["POWHEG","POWHEG"]
    #label="powheg"
#    filenames=["biasTest_HPLP_trig2016_BulkGWW_madgraph.root","biasTest_HPLP_trig2016_BulkGWW_herwig.root"]#,"biasTest_HPHP_trig2016_BulkGWW_NLO.root"]
#    names=["madgraph sample","herwig sample"]#,"powheg NLO sample"]
    graphs=[]
    color=[ROOT.kBlue,ROOT.kRed,ROOT.kGreen+2,ROOT.kBlue+2,ROOT.kBlack]
    marker=[20,22,26,27]
    title="relative bias (%)"
    c=0
    for filename in filenames:
        f = ROOT.TFile(filename,"READ")
        graphs.append(f.Get("rel_bias"))
        graphs[-1].SetName("rel_bias_"+filename)
        graphs[-1] = beautify(graphs[-1],color[c],marker[c],title)
        c+=1
    
    c = get_canvas("cbias")
    for g in range(0,len(graphs)):
        if g==0:
            graphs[g].Draw("AP")
        else:
            graphs[g].Draw("P")
            
    l = getLegend(graphs,["HPHP category", "HPLP categroy"])
    l.SetTextFont(42)
    l.SetTextSize(0.04)
    l.Draw("same")
    line1 = ROOT.TLine()
    line1.SetLineStyle(3)
    line1.DrawLine(900,0.1,4800,0.1)
    line1.DrawLine(900,-0.1,4800,-0.1)
    line1.DrawLine(900,0.,4800,0.)
    
    
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.15,0.86,"#font[52]{Simulation}")
    text.DrawLatexNDC(0.15,0.80,"#font[62]{"+names[0]+"}")
    #cmslabel_sim(c,'2016',10)
    c.Update()
    c.SaveAs("biastest_"+label+".pdf")
    c.SaveAs("biastest_"+label+".png")
    
    
