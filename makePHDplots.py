import ROOT
import os,sys
import CMS_lumi
ROOT.gROOT.ProcessLine(".x tdrstyle.cc")
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetLegendBorderSize(0)


def getCanvas(w=800,h=600):
 H_ref = 600 
 W_ref = 600 
 W = W_ref
 H  = H_ref

 iPeriod = 0

 # references for T, B, L, R
 T = 0.09*H_ref
 B = 0.15*H_ref 
 L = 0.2*W_ref
 R = 0.18*W_ref
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
    h1.SetLineColor(color)
    h1.SetMarkerColor(color)
    # h1.SetFillColor(color)
    h1.SetLineWidth(3)
    h1.SetLineStyle(linestyle)
    h1.SetMarkerStyle(markerstyle)
    #h1.GetXaxis().SetTextSize(0.04)
    h1.GetXaxis().SetLabelSize(0.05)
    h1.GetYaxis().SetLabelSize(0.05)
    h1.GetYaxis().SetTitleOffset(1.5)
    h1.GetXaxis().SetTitleOffset(1.2)
    h1.GetYaxis().SetTitleSize(0.05)
    h1.GetXaxis().SetTitleSize(0.05)
    
def getLegend(x1=0.5809045,y1=0.6363636,x2=0.9022613,y2=0.87020979):
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

def getPavetext():
  addInfo = ROOT.TPaveText(0.3010112,0.2066292,0.4202143,0.3523546,"NDC")
  addInfo.SetFillColor(0)
  addInfo.SetLineColor(0)
  addInfo.SetFillStyle(0)
  addInfo.SetBorderSize(0)
  addInfo.SetTextFont(42)
  addInfo.SetTextSize(0.040)
  addInfo.SetTextAlign(12)
  return addInfo


def fitGauss(histo,xmin,xmax,color=ROOT.kRed):
    gauss = ROOT.TF1(histo.GetName()+"fit","gaus",xmin,xmax)
    gauss.SetLineColor(color)
    histo.Fit(gauss,"","",xmin,xmax)
    return gauss

if __name__=="__main__":
    
    f = ROOT.TFile("/portal/ekpbms2/home/dschaefer/DiBoson3D/2016/JJ_nonRes_COND2D_HPLP_l1.root","READ")
    
    histo = f.Get("histo_nominal")
    histo.Scale(100)
    histo.GetXaxis().SetNdivisions(7,0,5)
    histo.GetYaxis().SetNdivisions(6,0,5)
    histo.GetXaxis().SetTitle("m_{jet1} [GeV]")
    histo.GetYaxis().SetTitle("Dijet mass [GeV]" )
    histo.GetZaxis().SetTitle("arbitrary scale" )
    histo.GetYaxis().SetTitleOffset(1.55)
    histo.GetXaxis().SetTitleOffset(1.15)
    
    c = getCanvas(600,600)
    histo.Draw("colz")
    
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.199,0.92,"#font[52]{Simulation}")
    c.SaveAs("2D_histo_l1_HPLP.pdf")
    
    f = ROOT.TFile("/portal/ekpbms2/home/dschaefer/DiBoson3D/2016/JJ_nonRes_COND2D_HPLP_l2.root","READ")
    
    histo = f.Get("histo_nominal")
    histo.Scale(100)
    histo.GetXaxis().SetNdivisions(7,0,5)
    histo.GetYaxis().SetNdivisions(6,0,5)
    histo.GetXaxis().SetTitle("m_{jet2} [GeV]")
    histo.GetYaxis().SetTitle("Dijet mass [GeV]" )
    histo.GetZaxis().SetTitle("arbitrary scale" )
    histo.GetYaxis().SetTitleOffset(1.55)
    histo.GetXaxis().SetTitleOffset(1.15)
    
    c = getCanvas(600,600)
    histo.Draw("colz")
    
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.199,0.92,"#font[52]{Simulation}")
    c.SaveAs("2D_histo_l2_HPLP.pdf")
    
    f2 = ROOT.TFile("/portal/ekpbms2/home/dschaefer/DiBoson3D/2016/JJ_nonRes_MVV_HPLP.root","READ")
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.15)
    c.SetTopMargin(0.1)
    finalHistogram = f2.Get("histo_nominal")
    histogram_pt_up = f2.Get("histo_nominal_PTUp")
    histogram_pt_down = f2.Get("histo_nominal_PTDown")
    histogram_opt_up = f2.Get("histo_nominal_OPTUp")
    histogram_opt_down = f2.Get("histo_nominal_OPTDown")
    
    finalHistogram.SetLineColor(ROOT.kBlue)
    finalHistogram.GetYaxis().SetTitle("arbitrary units")
    finalHistogram.GetYaxis().SetTitleOffset(1.15)
    finalHistogram.GetXaxis().SetTitleOffset(1.1)
    finalHistogram.GetXaxis().SetTitle("Dijet mass [GeV]")
    finalHistogram.GetXaxis().SetLabelSize(0.05)
    finalHistogram.GetYaxis().SetLabelSize(0.04)
    finalHistogram.GetXaxis().SetTitleSize(0.06)
    finalHistogram.GetYaxis().SetTitleSize(0.06)
    finalHistogram.GetXaxis().SetNdivisions(5,0,5)
    finalHistogram.GetYaxis().SetNdivisions(5,0,5)
    finalHistogram.SetLineWidth(2)

    sf = finalHistogram.Integral()
    histogram_pt_up     .Scale(sf/histogram_pt_up.Integral())
    histogram_pt_down   .Scale(sf/histogram_pt_down.Integral())
    histogram_opt_up    .Scale(sf/histogram_opt_up.Integral())
    histogram_opt_down  .Scale(sf/histogram_opt_down.Integral())
    finalHistogram.Draw("hist")
    #stack.Draw("histsame")
    histogram_pt_up.SetLineColor(ROOT.kRed)
    histogram_pt_up.SetLineWidth(2)
    histogram_pt_up.Draw("histsame")
    histogram_pt_down.SetLineColor(ROOT.kRed)
    histogram_pt_down.SetLineWidth(2)
    histogram_pt_down.Draw("histsame")
    histogram_opt_up.SetLineColor(ROOT.kGreen)
    histogram_opt_up.SetLineWidth(2)
    histogram_opt_up.Draw("histsame")
    histogram_opt_down.SetLineColor(ROOT.kGreen)
    histogram_opt_down.SetLineWidth(2)
    histogram_opt_down.Draw("histsame")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.14,0.92,"#font[52]{Simulation}")
    data = f2.Get("mvv_nominal")
    data.Scale(sf/data.Integral())
    data.SetMarkerColor(ROOT.kBlack)
    data.SetMarkerStyle(7)
    data.Draw("same")
    c.SetLogy()


    l = getLegend(0.5)#0.17,0.15,0.5,0.33)
    purity = "HPLP"
    l.SetHeader("QCD multijet, "+purity)
    l.AddEntry(data,"Simulation","lp")
    l.AddEntry(finalHistogram,"Template","l")
    l.AddEntry(histogram_pt_up,"#propto m_{jj} up/down","l")
    l.AddEntry(histogram_opt_up,"#propto 1/m_{jj} up/down","l")
    l.Draw("same")

    c.SaveAs("debug_mVV_kernels_QCD_"+purity+".pdf")
    
    
    
    f3 = ROOT.TFile("/portal/ekpbms2/home/dschaefer/DiBoson3D/2016/JJ_nonRes_detectorResponse.root","READ")
    f3 = ROOT.TFile("/portal/ekpbms2/home/dschaefer/CMSSW_8_1_0/src/CMGTools/VVResonances/interactive/JJ_2016_nonRes_detectorResponse.root","READ")
    scaleX = f3.Get("scalexHisto")
    scaleY = f3.Get("scaleyHisto")
    resY = f3.Get("resyHisto")
    resX = f3.Get("resxHisto")
    dataX = f3.Get("dataX")
    dataY = f3.Get("dataY")
    dataX.SetName("tmpX")
    dataY.SetName("tmpY")
    
    dataX_res = dataX.ProjectionX("xres")
    dataX_scale= dataX.ProjectionY("xscale")
    
    dataY_res = dataY.ProjectionX("yres")
    dataY_scale= dataY.ProjectionY("yscale")
    
    f4 = ROOT.TFile("/portal/ekpbms2/home/dschaefer/DiBoson3D/2017/JJ_nonRes_detectorResponse.root","READ")
    f4 = ROOT.TFile("/portal/ekpbms2/home/dschaefer/CMSSW_8_1_0/src/CMGTools/VVResonances/interactive/JJ_herwig_nonRes_detectorResponse.root","READ")
    scaleX_17 = f4.Get("scalexHisto")
    scaleY_17 = f4.Get("scaleyHisto")
    resY_17 = f4.Get("resyHisto")
    resX_17 = f4.Get("resxHisto")
    
    dataX_17 = f4.Get("dataX")
    dataY_17 = f4.Get("dataY")
    
    
    dataX_res_17 = dataX_17.ProjectionX("xres17")
    dataX_scale_17 = dataX_17.ProjectionY("xscale17")
    
    dataY_res_17 = dataY_17.ProjectionX("yres17")
    dataY_scale_17 = dataY_17.ProjectionY("yscale17")
    
    
    
    scaleX.GetXaxis().SetRangeUser(200,2500)
    beautify(scaleX,ROOT.kBlue)
    scaleX.GetXaxis().SetTitle("Gen p_{T} [GeV]")
    scaleX.GetYaxis().SetTitle("m_{VV} scale")
    beautify(scaleX_17,ROOT.kGreen+2)
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.15)
    c.SetTopMargin(0.1)
    
    scaleX.Draw("histoE1")
    scaleX_17.Draw("histoE1same")
    l = getLegend(0.45)#0.17,0.15,0.5,0.33)
    l.SetHeader("QCD multijet simulation ")
    l.AddEntry(scaleX,"2016 simulation","l")
    l.AddEntry(scaleX_17,"2017 simulation","l")
    l.Draw("same")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.14,0.92,"#font[52]{Simulation}")
    c.SaveAs("detector_scale_mvv.pdf")
    
    
    resX.GetXaxis().SetRangeUser(200,2500)
    beautify(resX,ROOT.kBlue)
    resX.GetXaxis().SetTitle("Gen p_{T} [GeV]")
    resX.GetYaxis().SetTitle("m_{VV} resolution")
    resX.GetYaxis().SetTitleOffset(1.98)
    beautify(resX_17,ROOT.kGreen+2)
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.2)
    c.SetTopMargin(0.1)
    resX.Draw("histoE1")
    resX_17.Draw("histoE1same")
    l = getLegend(0.45)#0.17,0.15,0.5,0.33)
    l.SetHeader("QCD multijet simulation ")
    l.AddEntry(resX,"2016 simulation","l")
    l.AddEntry(resX_17,"2017 simulation","l")
    l.Draw("same")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.195,0.92,"#font[52]{Simulation}")
    c.SaveAs("detector_res_mvv.pdf")
    
    
    
    
    scaleY.GetXaxis().SetRangeUser(200,2500)
    beautify(scaleY,ROOT.kBlue)
    scaleY.GetXaxis().SetTitle("Gen p_{T} [GeV]")
    scaleY.GetYaxis().SetTitle("m_{jet} scale")
    scaleY.GetYaxis().SetRangeUser(0.93,1.05)
    beautify(scaleY_17,ROOT.kGreen+2)
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.15)
    c.SetTopMargin(0.1)
    scaleY.Draw("histoE1")
    scaleY_17.Draw("histoE1same")
    l = getLegend(0.45)#0.17,0.15,0.5,0.33)
    l.SetHeader("QCD multijet simulation ")
    l.AddEntry(scaleY,"2016 simulation","l")
    l.AddEntry(scaleY_17,"2017 simulation","l")
    l.Draw("same")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.14,0.92,"#font[52]{Simulation}")
    c.SaveAs("detector_scale_mjet.pdf")
    
    
    resY.GetXaxis().SetRangeUser(200,2500)
    beautify(resY,ROOT.kBlue)
    resY.GetXaxis().SetTitle("Gen p_{T} [GeV]")
    resY.GetYaxis().SetTitle("m_{jet} resolution")
    resY.GetYaxis().SetTitleOffset(1.98)
    beautify(resY_17,ROOT.kGreen+2)
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.2)
    c.SetTopMargin(0.1)
    resY.Draw("histoE1")
    resY_17.Draw("histoE1same")
    l = getLegend(0.45)#0.17,0.15,0.5,0.33)
    l.SetHeader("QCD multijet simulation ")
    l.AddEntry(resY,"2016 simulation","l")
    l.AddEntry(resY_17,"2017 simulation","l")
    l.Draw("same")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.195,0.92,"#font[52]{Simulation}")
    c.SaveAs("detector_res_mjet.pdf")
    
    
    dataX_scale.GetYaxis().SetRangeUser(0,1)
    dataX_scale.Scale(1/dataX_scale.Integral())
    dataX_scale_17.Scale(1/dataX_scale_17.Integral())
    dataX_scale_17.GetYaxis().SetRangeUser(0,0.2)
    beautify(dataX_scale,ROOT.kBlue)
    dataX_scale_17.GetXaxis().SetTitle("m_{VV}^{reco}/m_{VV}^{gen}")
    dataX_scale_17.GetYaxis().SetTitle("arbitrary units")
    dataX_scale_17.GetYaxis().SetTitleOffset(1.98)
    dataX_scale_17.GetYaxis().SetNdivisions(5,0,5)
    dataX_scale_17.GetXaxis().SetNdivisions(5,0,5)
    dataX_scale_17.SetMarkerStyle(1)
    beautify(dataX_scale_17,ROOT.kGreen+2)
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.2)
    c.SetTopMargin(0.1)
    gauss16 = fitGauss(dataX_scale,0.8,1.2)
    dataX_scale.Draw("histo")
    
    gauss17 = fitGauss(dataX_scale_17,0.8,1.2,ROOT.kBlack)
    print gauss17
    print gauss16
    print dataX_scale
    print dataX_scale_17
    dataX_scale_17.Draw("hist")
    dataX_scale.Draw("histsame")
    gauss17.Draw("same")
    gauss16.Draw("same")
    l = getLegend(0.45)#0.17,0.15,0.5,0.33)
    l.SetHeader("QCD multijet simulation ")
    l.AddEntry(dataX_scale,"2016 simulation","l")
    l.AddEntry(gauss16,"2016 fit","l")
    l.AddEntry(dataX_scale_17,"2017 simulation","l")
    l.AddEntry(gauss17,"2017 fit","l")
    l.Draw("same")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.195,0.92,"#font[52]{Simulation}")
    c.SaveAs("detector_mvvreco_mvvgen_res.pdf")
    
    
    dataX_res.GetYaxis().SetRangeUser(0,1)
    dataY_scale.Scale(1/dataY_scale.Integral())
    dataY_scale_17.Scale(1/dataY_scale_17.Integral())
    dataY_scale.GetYaxis().SetRangeUser(0,0.1)
    beautify(dataY_scale,ROOT.kBlue)
    dataY_scale.GetXaxis().SetTitle("m_{jet}^{reco}/m_{jet}^{gen}")
    dataY_scale.GetYaxis().SetTitle("arbitrary units")
    dataY_scale.GetYaxis().SetTitleOffset(1.98)
    dataY_scale.GetYaxis().SetNdivisions(5,0,5)
    dataY_scale.GetXaxis().SetNdivisions(5,0,5)
    beautify(dataY_scale_17,ROOT.kGreen+2)
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.2)
    c.SetTopMargin(0.1)
    dataY_scale.Draw("histo")
    gauss16 = fitGauss(dataY_scale,0.8,1.1)
    gauss16.Draw("same")
    dataY_scale_17.Draw("histosame")
    gauss17 = fitGauss(dataY_scale_17,0.8,1.1,ROOT.kBlack)
    gauss17.Draw("same")
    l = getLegend(0.45)#0.17,0.15,0.5,0.33)
    l.SetHeader("QCD multijet simulation ")
    l.AddEntry(dataY_scale,"2016 simulation","l")
    l.AddEntry(gauss16,"2016 fit","l")
    l.AddEntry(dataY_scale_17,"2017 simulation","l")
    l.AddEntry(gauss17,"2017 fit","l")
    l.Draw("same")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.195,0.92,"#font[52]{Simulation}")
    c.SaveAs("detector_mjetreco_mjetgen_res.pdf")
    
    
    
    
    dirnew = "/portal/ekpbms2/home/dschaefer/CMGToolsForStat10X/CMSSW_10_2_10/src/CMGTools/VVResonances/interactive/"
    f = ROOT.TFile(dirnew+"debug_JJ_j2WprimeWZ_2016_MVV.json.root","READ")
    
    corr = f.Get("corr_mean")
 
 
    corr.GetXaxis().SetTitle("jet-1 mass [GeV]")
    corr.GetYaxis().SetTitle("jet-2 mass [GeV]")
    corr.GetYaxis().SetTitleOffset(1.3)
    corr.GetYaxis().SetNdivisions(5,0,5)
    corr.GetXaxis().SetNdivisions(5,0,5)
    c = getCanvas()
    #c.SetRightMargin(0.04)
    #c.SetLeftMargin(0.2)
    #c.SetTopMargin(0.1)
    corr.Draw("colz")   
    
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.195,0.92,"#font[52]{Simulation}")
    c.SaveAs("corr_mean.pdf")
    
    corr = f.Get("corr_sigma")
    corr.GetXaxis().SetTitle("jet-1 mass [GeV]")
    corr.GetYaxis().SetTitle("jet-2 mass [GeV]")
    corr.GetYaxis().SetTitleOffset(1.3)
    corr.GetYaxis().SetNdivisions(5,0,5)
    corr.GetXaxis().SetNdivisions(5,0,5)
    c = getCanvas()
    #c.SetRightMargin(0.04)
    #c.SetLeftMargin(0.2)
    #c.SetTopMargin(0.1)
    corr.Draw("colz")   
    
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.195,0.92,"#font[52]{Simulation}")
    c.SaveAs("corr_sigma.pdf")
    
    
    
    
    
    f2 = ROOT.TFile("/portal/ekpbms2/home/dschaefer/DiBoson3D/2016/JJ_WJets_MVV_HPLP.root","READ")
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.15)
    c.SetTopMargin(0.1)
    finalHistogram = f2.Get("histo_nominal")
    histogram_pt_up = f2.Get("histo_nominal_PTUp")
    histogram_pt_down = f2.Get("histo_nominal_PTDown")
    histogram_opt_up = f2.Get("histo_nominal_OPTUp")
    histogram_opt_down = f2.Get("histo_nominal_OPTDown")
    
    finalHistogram.SetLineColor(ROOT.kBlue)
    finalHistogram.GetYaxis().SetTitle("arbitrary units")
    finalHistogram.GetYaxis().SetTitleOffset(1.15)
    finalHistogram.GetXaxis().SetTitleOffset(1.1)
    finalHistogram.GetXaxis().SetTitle("Dijet mass [GeV]")
    finalHistogram.GetXaxis().SetLabelSize(0.05)
    finalHistogram.GetYaxis().SetLabelSize(0.04)
    finalHistogram.GetXaxis().SetTitleSize(0.06)
    finalHistogram.GetYaxis().SetTitleSize(0.06)
    finalHistogram.GetXaxis().SetNdivisions(5,0,5)
    finalHistogram.GetYaxis().SetNdivisions(5,0,5)
    finalHistogram.SetLineWidth(2)

    sf = finalHistogram.Integral()
    histogram_pt_up     .Scale(sf/histogram_pt_up.Integral())
    histogram_pt_down   .Scale(sf/histogram_pt_down.Integral())
    histogram_opt_up    .Scale(sf/histogram_opt_up.Integral())
    histogram_opt_down  .Scale(sf/histogram_opt_down.Integral())
    finalHistogram.Draw("hist")
    #stack.Draw("histsame")
    histogram_pt_up.SetLineColor(ROOT.kRed)
    histogram_pt_up.SetLineWidth(2)
    histogram_pt_up.Draw("histsame")
    histogram_pt_down.SetLineColor(ROOT.kRed)
    histogram_pt_down.SetLineWidth(2)
    histogram_pt_down.Draw("histsame")
    histogram_opt_up.SetLineColor(ROOT.kGreen)
    histogram_opt_up.SetLineWidth(2)
    histogram_opt_up.Draw("histsame")
    histogram_opt_down.SetLineColor(ROOT.kGreen)
    histogram_opt_down.SetLineWidth(2)
    histogram_opt_down.Draw("histsame")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.14,0.92,"#font[52]{Simulation}")
    data = f2.Get("mvv_nominal")
    data.Scale(sf/data.Integral())
    data.SetMarkerColor(ROOT.kBlack)
    data.SetMarkerStyle(10)
    data.Draw("same E1 X0")
    c.SetLogy()


    l = getLegend(0.5)#0.17,0.15,0.5,0.33)
    purity = "HPLP"
    l.SetHeader("W+jets + t#bar{t}, "+purity)
    l.AddEntry(data,"Simulation","pe")
    l.AddEntry(finalHistogram,"Template","l")
    l.AddEntry(histogram_pt_up,"#propto m_{jj} up/down","l")
    l.AddEntry(histogram_opt_up,"#propto 1/m_{jj} up/down","l")
    l.Draw("same")

    c.SaveAs("debug_mVV_kernels_Wjets_"+purity+".pdf")
    
    
    
    f2 = ROOT.TFile("/portal/ekpbms2/home/dschaefer/DiBoson3D/2016/JJ_ZJets_MVV_HPHP.root","READ")
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.15)
    c.SetTopMargin(0.1)
    finalHistogram = f2.Get("histo_nominal")
    histogram_pt_up = f2.Get("histo_nominal_PTUp")
    histogram_pt_down = f2.Get("histo_nominal_PTDown")
    histogram_opt_up = f2.Get("histo_nominal_OPTUp")
    histogram_opt_down = f2.Get("histo_nominal_OPTDown")
    
    finalHistogram.SetLineColor(ROOT.kBlue)
    finalHistogram.GetYaxis().SetTitle("arbitrary units")
    finalHistogram.GetYaxis().SetTitleOffset(1.15)
    finalHistogram.GetXaxis().SetTitleOffset(1.1)
    finalHistogram.GetXaxis().SetTitle("Dijet mass [GeV]")
    finalHistogram.GetXaxis().SetLabelSize(0.05)
    finalHistogram.GetYaxis().SetLabelSize(0.04)
    finalHistogram.GetXaxis().SetTitleSize(0.06)
    finalHistogram.GetYaxis().SetTitleSize(0.06)
    finalHistogram.GetXaxis().SetNdivisions(5,0,5)
    finalHistogram.GetYaxis().SetNdivisions(5,0,5)
    finalHistogram.SetLineWidth(2)

    sf = finalHistogram.Integral()
    histogram_pt_up     .Scale(sf/histogram_pt_up.Integral())
    histogram_pt_down   .Scale(sf/histogram_pt_down.Integral())
    histogram_opt_up    .Scale(sf/histogram_opt_up.Integral())
    histogram_opt_down  .Scale(sf/histogram_opt_down.Integral())
    finalHistogram.Draw("hist")
    #stack.Draw("histsame")
    histogram_pt_up.SetLineColor(ROOT.kRed)
    histogram_pt_up.SetLineWidth(2)
    histogram_pt_up.Draw("histsame")
    histogram_pt_down.SetLineColor(ROOT.kRed)
    histogram_pt_down.SetLineWidth(2)
    histogram_pt_down.Draw("histsame")
    histogram_opt_up.SetLineColor(ROOT.kGreen)
    histogram_opt_up.SetLineWidth(2)
    histogram_opt_up.Draw("histsame")
    histogram_opt_down.SetLineColor(ROOT.kGreen)
    histogram_opt_down.SetLineWidth(2)
    histogram_opt_down.Draw("histsame")
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.14,0.92,"#font[52]{Simulation}")
    data = f2.Get("mvv_nominal")
    data.Scale(sf/data.Integral())
    data.SetMarkerColor(ROOT.kBlack)
    data.SetMarkerStyle(10)
    data.Draw("same E1 X0")
    c.SetLogy()


    l = getLegend(0.5)#0.17,0.15,0.5,0.33)
    purity = "HPHP"
    l.SetHeader("Z+jets, "+purity)
    l.AddEntry(data,"Simulation","pe")
    l.AddEntry(finalHistogram,"Template","l")
    l.AddEntry(histogram_pt_up,"#propto m_{jj} up/down","l")
    l.AddEntry(histogram_opt_up,"#propto 1/m_{jj} up/down","l")
    l.Draw("same")

    c.SaveAs("debug_mVV_kernels_Zjets_"+purity+".pdf")
    
    
    f = ROOT.TFile("JJ_WJets_NP.root","READ")
    f1 = ROOT.TFile("JJ_noKfactor_WJets_NP.root","READ")
    f2 = ROOT.TFile("JJ_ZJets_NP.root","READ")
    f3 = ROOT.TFile("JJ_noKfactor_ZJets_NP.root","READ")
    c = getCanvas()
    c.SetRightMargin(0.04)
    c.SetLeftMargin(0.15)
    c.SetTopMargin(0.1)
    c.SetLogy()
    h1 = f.Get("WJets")
    h1.SetName("WJETSweight")
    h1noW = f1.Get("WJets")
    h1noWp = h1noW.ProjectionZ()
    h1noWp.SetName("Wjetsnoweights")
    h1p = h1.ProjectionZ()
    h2noW = f3.Get("ZJets")
    h2noWp = h2noW.ProjectionZ()
    h2noWp.SetName("Zjetsnoweights")
    h2 = f2.Get("ZJets")
    h2p = h2.ProjectionZ()
    
    #h1p.Scale(1/h1p.Integral())
    #h2p.Scale(1/h2p.Integral())
    #h1noWp.Scale(1/h1noWp.Integral())
    #h2noWp.Scale(1/h2noWp.Integral())
    
   
    h1p.GetYaxis().SetTitle("arbitrary units")
    h1p.GetYaxis().SetTitleOffset(1.15)
    h1p.GetXaxis().SetTitleOffset(1.1)
    h1p.GetXaxis().SetTitle("Dijet mass [GeV]")
    h1p.GetXaxis().SetLabelSize(0.05)
    h1p.GetYaxis().SetLabelSize(0.04)
    h1p.GetXaxis().SetTitleSize(0.06)
    h1p.GetYaxis().SetTitleSize(0.06)
    h1p.GetXaxis().SetNdivisions(5,0,5)
    h1p.GetYaxis().SetNdivisions(5,0,5)
    h1p.SetLineWidth(2)
    h2p.SetLineWidth(2)
    h1noWp.SetLineWidth(2)
    h2noWp.SetLineWidth(2)
    
    
    
    l = getLegend(0.4,0.65,0.7)
    l.AddEntry(h1p,"W+jets, k-factor+EWK","l")
    l.AddEntry(h1noWp,"W+jets","l")
    l.AddEntry(h2p,"Z+jets, k-factor+EWK","l")
    l.AddEntry(h2noWp,"Z+jets","l")
    #h1p.SetMaximum(500)
    #h1p.SetMinimum(0.0004)
   
      
    h1p.Draw("hist")
    l.Draw("same")
    h2p.SetLineColor(ROOT.kRed)
    h2p.Draw("histsame")
    h1noWp.SetLineColor(ROOT.kBlue)
    h1noWp.Draw("histsame")
    h2noWp.SetLineColor(ROOT.kOrange)
    h2noWp.Draw("histsame")
    c.SaveAs("test.pdf")
    
