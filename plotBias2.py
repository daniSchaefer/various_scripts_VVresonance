import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
import numpy
from array import array


def makePlot(shapes,outname,graphs_all,label,purity):
     colors = ["#00008B","#F4A460","#8A2BE2","#FF00FF","#FFB6C1"]
     markers = [10,12,15]*3
     c = getCanvas() 
     l = getLegend(0.45,0.89,0.8,0.65)
     
     N=0
     for k in shapes:
        beautify(graphs_all[k],colors[N],1,markers[N])
        if N==0:
             graphs_all[k].Draw("ap")
        else: graphs_all[k].Draw("psame")
        l.AddEntry(graphs_all[k],getLabel(k),"pe")
        N+=1
     l.Draw("same")
     line = ROOT.TLine(950,0,4700,0)
     line.SetLineStyle(2)
     line.Draw("same")
     line1 = ROOT.TLine(950,1,4700,1)
     line1.SetLineStyle(2)
     line1.Draw("same")
     line2 = ROOT.TLine(950,-1,4700,-1)
     line2.SetLineStyle(2)
     line2.Draw("same")
     text = ROOT.TLatex()
     text.DrawLatexNDC(0.15,0.8,"#font[62]{"+label+"}")
     text.DrawLatexNDC(0.15,0.75,"#font[42]{"+purity+"}")
     c.SaveAs(outname)

def getCanvas(w=600,h=600):
 H_ref = 600 
 W_ref = 600 
 W = W_ref
 H  = H_ref

 iPeriod = 0

 # references for T, B, L, R
 T = 0.09*H_ref
 B = 0.15*H_ref 
 L = 0.12*W_ref
 R = 0.1*W_ref
 cname = "c"
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


def beautify(h1,color,linestyle=1,markerstyle=8):
    h1.SetLineColor(ROOT.TColor().GetColor(color))
    h1.SetMarkerColor(ROOT.TColor().GetColor(color))
    # h1.SetFillColor(color)
    h1.SetLineWidth(3)
    h1.SetLineStyle(linestyle)
    h1.SetMarkerStyle(markerstyle)
    #h1.GetXaxis().SetTextSize(0.04)
    h1.GetXaxis().SetLabelSize(0.05)
    h1.GetYaxis().SetLabelSize(0.04)
    h1.GetYaxis().SetTitleOffset(1.1)
    h1.GetXaxis().SetTitleOffset(1.2)
    h1.GetYaxis().SetTitleSize(0.05)
    h1.GetXaxis().SetTitleSize(0.05)
    h1.SetMaximum(2.99)
    h1.SetMinimum(-2.1)
    if h1.GetName().find("nonRes")!=-1:
        h1.SetMaximum(6)
        h1.SetMinimum(-2)
    #if h1.GetName().find("norm")!=-1:
        #h1.SetMaximum(0.5)
        #h1.SetMinimum(-0.5)
    if h1.GetName().find("jets")!=-1 and h1.GetName().find("norm")==-1:
        h1.SetMaximum(0.5)
        h1.SetMinimum(-0.5)
    if h1.GetName().find("jets")!=-1 and h1.GetName().find("norm")==-1:
        h1.SetMaximum(0.5)
        h1.SetMinimum(-0.5) 
               
    
    h1.GetXaxis().SetNdivisions(6,0,5)
    h1.GetXaxis().SetLabelOffset(0.02)
    h1.GetXaxis().SetTitle("m_{X} [GeV]")
    h1.GetYaxis().SetTitle("(#theta - #theta_{in})/#sigma_{#theta,in}")
    
def getLegend(x1=0.109045,y1=0.8363636,x2=0.8022613,y2=0.87020979):
  legend = ROOT.TLegend(x1,y1,x2,y2)
  legend.SetTextSize(0.04)
  legend.SetLineColor(0)
  legend.SetShadowColor(0)
  legend.SetLineStyle(1)
  legend.SetLineWidth(1)
  legend.SetFillColor(0)
  legend.SetFillStyle(0)
  legend.SetMargin(0.35)
  legend.SetTextFont(42)
  return legend


def getLabel(var):
    if var.find("nonRes_PT_")!=-1:
        return "#propto m_{jj}"
    if var.find("nonRes_OPT_")!=-1:
        return "#propto 1/m_{jj}"
    if var.find("nonRes_OPT3_")!=-1:
        return "#propto m_{jj} turn on"
    if var.find("nonRes_altshape2_")!=-1:
        return "MG+Pythia"
    if var.find("nonRes_altshape_")!=-1:
        return "Herwig++"
    
    if var.find("CMS_VV_JJ_nonRes_norm")!=-1:
        return "QCD multijet norm"
    if var.find("CMS_VV_JJ_Wjets_norm")!=-1:
        return "W+jets, t#bar{t} norm"
    if var.find("CMS_VV_JJ_Zjets_norm")!=-1:
        return "Z+jet norm"
    
    if var.find("CMS_pdf")!=-1:
        return "PDF and #mu_{F}, #mu_{R}"
    if var.find("CMS_lumi")!=-1:
        return "luminosity"
    if var.find("CMS_VV_JJ_tau21_eff")!=-1:
        return "#tau_{21} efficiency"
    if var.find("CMS_tau21_PtDependence")!=-1:
        return "#tau_{21} p_{T}-dependence"
    if var.find("CMS_VV_JJ_Wjets_PTZ_"+purity)!=-1:
        return "W+jets #propto m_{jj}"
    if var.find("CMS_VV_JJ_Wjets_OPTZ_"+purity)!=-1:
        return "W+jets #propto 1/m_{jj}"
    if var.find("CMS_VV_JJ_Zjets_PTZ_"+purity)!=-1:
        return "Z+jets #propto m_{jj}"
    if var.find("CMS_VV_JJ_Zjets_OPTZ_"+purity)!=-1:
        return "Z+jets #propto 1/m_{jj}"
    if var.find("CMS_scale_prunedj")!=-1:
        return "jet mass scale"
    if var.find("CMS_res_prunedj")!=-1:
        return "jet mass resolution"
    if var.find("CMS_scale_j")!=-1:
        return "dijet mass scale"
    if var.find("CMS_res_j")!=-1:
        return "dijet mass resolution"

def readLog(logfile,variable):
    f = open(logfile,"r")
    r=[]
    e_r =[]
    for line in f.readlines():
        if variable+" =" in line or variable+"=" in line:

            if line.find("event")==-1:
                if line.split(variable+" =")[1].split(" - ")[0].find("e")!=-1:
                    num = line.split(variable+" =")[1].split(" - ")[0]
                    num1,num2 = num.split("e")
                    exp=1.
                    if int(num2)<0:
                        for i in range(0,ROOT.TMath.Abs(int(num2))):
                            exp=exp/10.
                    else:
                        for i in range(0,ROOT.TMath.Abs(int(num2))):
                            exp=exp*10.
                         
                    r.append(float(num1)*exp)
                    e_r.append(float(line.split(" + ")[1].split("L")[0]))
                    continue
            if variable.find("CMS")==-1 and line.find("event")==-1:
                r .append(float(line.split(variable+" =")[1].split("-")[0]))
                if variable.find("r_in")==-1:
                    e_r.append(float(line.split(" + ")[1].split("L")[0]))
                continue
            if variable.find("events injected")!=-1: 
                r.append(float(line.split(variable+" = ")[1]))
                continue
            if variable.find("ef")!=-1 and variable.find("CMS")==-1: 
                print variable
                r.append(float(line.split(variable+"=")[1].split("#")[0]))
                continue
            if variable.find("CMS")!=-1:
                r.append(float(line.split(variable+" = ")[1].split(" - ")[0]))
                #print r[-1]
                e_r.append(float(line.split(" + ")[1].split("L")[0]))
                continue
    return [r,e_r]

def getHist(var):
    if var.find("nonRes_norm")!=-1:
        return ROOT.TH1F("h"+var+"_"+mass,"h"+var+"_"+mass,1000,-0.5,0.5)
    if var.find("PT")!=-1 or var.find("altshape")!=-1:
        return ROOT.TH1F("h"+var+"_"+mass,"h"+var+"_"+mass,1000,-10,20)
    return ROOT.TH1F("h"+var+"_"+mass,"h"+var+"_"+mass,1000,-2,2)

if __name__=="__main__":
        label = sys.argv[1]   #"fullBkg_pythiaLPLP_expSig3_moreSyst"
        purity = "HPLP"
        if label.find("HPLP")!=-1:
            purity = "HPLP"
        variables =["CMS_VV_JJ_nonRes_PT_"+purity,"CMS_VV_JJ_nonRes_OPT_"+purity,"CMS_VV_JJ_nonRes_OPT3_"+purity,"CMS_VV_JJ_nonRes_altshape_"+purity,"CMS_VV_JJ_nonRes_altshape2_"+purity,"CMS_VV_JJ_nonRes_norm","CMS_VV_JJ_Wjets_norm","CMS_VV_JJ_Zjets_norm","CMS_pdf","CMS_lumi","CMS_VV_JJ_tau21_eff","CMS_tau21_PtDependence","CMS_VV_JJ_Wjets_PTZ_"+purity,"CMS_VV_JJ_Wjets_OPTZ_"+purity,"CMS_VV_JJ_Zjets_PTZ_"+purity,"CMS_VV_JJ_Zjets_OPTZ_"+purity,"CMS_scale_prunedj","CMS_res_prunedj","CMS_scale_j","CMS_res_j"]
        graphs_all = {}
        all_vars = {}
        epsilon={"CMS_VV_JJ_nonRes_PT_"+purity:0,"CMS_VV_JJ_nonRes_OPT_"+purity:40,"CMS_VV_JJ_nonRes_OPT3_"+purity:80,"CMS_VV_JJ_nonRes_altshape_"+purity:120,"CMS_VV_JJ_nonRes_altshape2_"+purity:160,"CMS_VV_JJ_nonRes_norm":0,"CMS_VV_JJ_Wjets_norm":40,"CMS_VV_JJ_Zjets_norm":80,"CMS_pdf":0,"CMS_lumi":40,"CMS_VV_JJ_tau21_eff":80,"CMS_tau21_PtDependence":120,"CMS_VV_JJ_Wjets_PTZ_"+purity:0,"CMS_VV_JJ_Wjets_OPTZ_"+purity:40,"CMS_VV_JJ_Zjets_PTZ_"+purity:80,"CMS_VV_JJ_Zjets_OPTZ_"+purity:120,"CMS_scale_prunedj":0,"CMS_res_prunedj":40,"CMS_scale_j":80,"CMS_res_j":120}
        
        for var in variables:
            graphs_all[var]= (ROOT.TGraphErrors())
            graphs_all[var].SetName(var+"_graph")

        indir = "res/"
        for filename in os.listdir(indir):
            if filename.find(".log")==-1:
                    continue
            if filename.find("Bias")==-1:
                continue
            if filename.find(label)==-1:
                continue
            mass = filename.split("_M")[1]
            mass = mass.split(".log")[0]
            if mass.find("_toy")!=-1:
                mass = mass.split("_")[0]
            mass_vars = {}
            for var in variables:
                mass_vars[var]=[[],[]]
            if mass not in all_vars.keys():
                all_vars[mass]=mass_vars
            #print filename
            #print readLog(indir+filename,"r_in")[0][0]
            #print readLog(indir+filename,"r")
            for var in variables:
                tmp = readLog(indir+filename,var)
                for i in range(0,len(tmp[0])):
                    all_vars[mass][var][0].append(tmp[0][i])
                    all_vars[mass][var][1].append(tmp[1][i])
                
        print all_vars
        print len(all_vars["1200"][variables[0]][0]) 
        N=0
        for mass in sorted(all_vars.keys()):
            for var in variables:
                htmp = getHist(var) 
                for i in range(0,len(all_vars[mass][var][0])):
                    inval = 0
                    if var.find("OPT3")!=-1: inval=0.111
                    if var.find("nonRes_norm")!=-1: inval=0.5 # the qcd expectation is scaled by 0.8 -> oversampling factor of qcd with respect to data i did not do this for the toys so it needs to be taken out
                    if var.find("CMS")!=-1 and var.find("nonRes")!=-1: sigma_in = 0.333
                    if var.find("CMS")!=-1 and var.find("jets")!=-1: sigma_in = 0.1
                    if var.find("CMS")!=-1 and var.find("lumi")!=-1: sigma_in = 0.025
                    if var.find("CMS")!=-1 and var.find("pdf")!=-1: sigma_in = 0.03
                    if var.find("CMS")!=-1 and var.find("jets_norm")!=-1: sigma_in = 0.2
                    if var.find("CMS")!=-1 and var.find("nonRes_norm")!=-1: sigma_in = 0.5
                    if var.find("CMS_scale_prunedj")!=-1 : sigma_in = 0.02
                    if var.find("CMS_res_prunedj")!=-1 : sigma_in = 0.08
                    if var.find("CMS_scale_j")!=-1 : sigma_in = 0.012
                    if var.find("CMS_res_j")!=-1 : sigma_in = 0.08
                    if var.find("CMS_VV_JJ_tau21_eff")!=-1 : sigma_in = 0.13
                    if var.find("CMS_tau21_PtDependence")!=-1 : sigma_in = ((1+0.06*numpy.log(float(mass)/2/300))*(1+0.07*numpy.log(float(mass)/2/300)))
                    #htmp.Fill((all_vars[mass][var][0][i]-inval)/all_vars[mass][var][1][i])
                    #if var.find("altshape_")!=-1: inval=10
                    #if var.find("norm")!=-1:
                        #htmp.Fill((all_vars[mass][var][0][i]-inval))
                    #else:
                        #htmp.Fill((all_vars[mass][var][0][i]/all_vars[mass][var][1][i]-inval))
                    htmp.Fill((all_vars[mass][var][0][i]-inval)/sigma_in)
                c=ROOT.TCanvas("c","c",400,400)
                htmp.Draw()
                c.SaveAs(htmp.GetName()+".pdf")
                print "save as "+htmp.GetName()+".pdf"
                graphs_all[var].SetPoint(N,int(mass)+epsilon[var],htmp.GetMean())
                graphs_all[var].SetPointError(N,0,htmp.GetRMS())
                print "set point "+str(N)+" "+mass+"  "+str(htmp.GetMean())
            N+=1
        label = "PYTHIA" 
        if sys.argv[1].find("herwig")!=-1: label = "HERWIG"
        if sys.argv[1].find("madgraph")!=-1: label = "MADGRAPH"
        if sys.argv[1].find("powheg")!=-1: label = "POWHEG"
        qcdshapes=["CMS_VV_JJ_nonRes_PT_"+purity,"CMS_VV_JJ_nonRes_OPT_"+purity,"CMS_VV_JJ_nonRes_OPT3_"+purity,"CMS_VV_JJ_nonRes_altshape_"+purity,"CMS_VV_JJ_nonRes_altshape2_"+purity]
        makePlot(qcdshapes,"pull_QCD_shape"+label+".pdf",graphs_all,label,purity)
        
        normalizations=["CMS_VV_JJ_nonRes_norm","CMS_VV_JJ_Wjets_norm","CMS_VV_JJ_Zjets_norm"]
        makePlot(normalizations,"pull_normBkg"+label+".pdf",graphs_all,label,purity)
        
        normalizations=["CMS_pdf","CMS_lumi","CMS_VV_JJ_tau21_eff","CMS_tau21_PtDependence"]
        makePlot(normalizations,"pull_normSignal"+label+".pdf",graphs_all,label,purity)
            
        qcdshapes=["CMS_VV_JJ_Wjets_PTZ_"+purity,"CMS_VV_JJ_Wjets_OPTZ_"+purity,"CMS_VV_JJ_Zjets_PTZ_"+purity,"CMS_VV_JJ_Zjets_OPTZ_"+purity]
        makePlot(qcdshapes,"pull_Vjets_shape"+label+".pdf",graphs_all,label,purity)
        
        qcdshapes=["CMS_scale_prunedj","CMS_res_prunedj","CMS_scale_j","CMS_res_j"]
        makePlot(qcdshapes,"pull_signal_shape"+label+".pdf",graphs_all,label,purity)
        #print all_vars["1200"]["CMS_VV_JJ_nonRes_norm"]
