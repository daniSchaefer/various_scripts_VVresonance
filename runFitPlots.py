import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
from array import array

ROOT.gErrorIgnoreLevel = ROOT.kWarning

ROOT.gStyle.SetOptStat(0)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)
colors = [ROOT.kBlack,ROOT.kPink-1,ROOT.kAzure+1,ROOT.kAzure+3,210,210,ROOT.kMagenta,ROOT.kOrange,ROOT.kViolet,ROOT.kMagenta,ROOT.kOrange,ROOT.kViolet]



def getListFromRange(xyzrange):
    r=[]
    a,b = xyzrange.split(",")
    r.append(float(a))
    r.append(float(b))
    return r


def getListOfBins(hist,dim):
    axis =0
    N = 0
    if dim =="x":
        axis= hist.GetXaxis()
        N = hist.GetNbinsX()
    if dim =="y":
        axis = hist.GetYaxis()
        N = hist.GetNbinsY()
    if dim =="z":
        axis = hist.GetZaxis()
        N = hist.GetNbinsZ()
    if axis==0:
        return {}
    
    mmin = axis.GetXmin()
    mmax = axis.GetXmax()
    bins ={}
    for i in range(1,N+1): bins[i] = axis.GetBinCenter(i) 
    
    return bins


def getListOfBinsLowEdge(hist,dim):
    axis =0
    N = 0
    if dim =="x":
        axis= hist.GetXaxis()
        N = hist.GetNbinsX()
    if dim =="y":
        axis = hist.GetYaxis()
        N = hist.GetNbinsY()
    if dim =="z":
        axis = hist.GetZaxis()
        N = hist.GetNbinsZ()
    if axis==0:
        return {}
    
    mmin = axis.GetXmin()
    mmax = axis.GetXmax()
    r=[]
    for i in range(1,N+2): r.append(axis.GetBinLowEdge(i)) 
    
    return array("d",r)


def getListOfBinsWidth(hist,dim):
    axis =0
    N = 0
    if dim =="x":
        axis= hist.GetXaxis()
        N = hist.GetNbinsX()
    if dim =="y":
        axis = hist.GetYaxis()
        N = hist.GetNbinsY()
    if dim =="z":
        axis = hist.GetZaxis()
        N = hist.GetNbinsZ()
    if axis==0:
        return {}
    
    mmin = axis.GetXmin()
    mmax = axis.GetXmax()
    r ={}
    for i in range(0,N+2):
        #v = mmin + i * (mmax-mmin)/float(N)
        r[i] = axis.GetBinWidth(i) 
    return r 

    
def reduceBinsToRange(Bins,r):
    if r[0]==0 and r[1]==-1:
        return Bins
    result ={}
    for key, value in Bins.iteritems():
        if value >= r[0] and value <=r[1]:
            result[key]=value
    return result


def MakePlots(histos,hdata,axis,nBins,options):
    extra1 = ''
    extra2 = ''
    htitle = ''
    xtitle = ''
    ymin = 0
    ymax = 0
    xrange = options.xrange
    yrange = options.yrange
    zrange = options.zrange
    if options.xrange == '0,-1': xrange = '55,215'
    if options.yrange == '0,-1': yrange = '55,215'
    if options.zrange == '0,-1': zrange = '1000,5000'
    if axis=='z':
     htitle = "Z-Proj. x : "+options.xrange+" y : "+options.yrange
     xtitle = "m_{jj} [GeV]"
     ymin = 0.02
     ymax = hdata.GetMaximum()*10
     extra1 = xrange.split(',')[0]+' < m_{jet1} < '+ xrange.split(',')[1]+' GeV'
     extra2 = yrange.split(',')[0]+' < m_{jet2} < '+ yrange.split(',')[1]+' GeV'
    elif axis=='x':
     htitle = "X-Proj. y : "+options.yrange+" z : "+options.zrange
     xtitle = "m_{jet1} [GeV]"
     ymin = 0.001
     ymax = hdata.GetMaximum()*1.3
     extra1 = yrange.split(',')[0]+' < m_{jet2} < '+ yrange.split(',')[1]+' GeV'
     extra2 = zrange.split(',')[0]+' < m_{jj} < '+ zrange.split(',')[1]+' GeV'
    elif axis=='y':
     htitle = "Y-Proj. x : "+options.xrange+" z : "+options.zrange
     xtitle = "m_{jet2} [GeV]"
     ymin = 0.001
     ymax = hdata.GetMaximum()*1.3
     extra1 = xrange.split(',')[0]+' < m_{jet1} < '+ xrange.split(',')[1]+' GeV'
     extra2 = zrange.split(',')[0]+' < m_{jj} < '+ zrange.split(',')[1]+' GeV'
                   
    leg = ROOT.TLegend(0.88,0.65,0.7,0.88)
    c = ROOT.TCanvas("c","c")
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    if axis == 'z': pad1.SetLogy()
    pad1.SetBottomMargin(0.01)    
    pad1.Draw()
    pad1.cd()	 
    histos[0].SetMinimum(ymin)
    histos[0].SetMaximum(ymax) 
    histos[0].SetLineColor(colors[0])
    histos[0].SetLineStyle(2)
    histos[0].SetLineWidth(2)
    histos[0].SetTitle(htitle)
    histos[0].GetXaxis().SetTitle(xtitle)
    histos[0].GetYaxis().SetTitleOffset(0.95)
    histos[0].GetYaxis().SetTitle("events")
    histos[0].GetYaxis().SetTitleOffset(0.95)
    histos[0].GetYaxis().SetTitle("events")
    histos[0].GetYaxis().SetTitleSize(0.06)
    histos[0].GetYaxis().SetLabelSize(0.06)
    histos[0].GetYaxis().SetNdivisions(5)
    histos[0].Draw("hist")
    leg.AddEntry(histos[0],"Pre fit pdf","l")
    
    histos[1].SetLineColor(colors[1])
    histos[1].SetLineWidth(2)
    histos[1].Draw('HISTsame')
    leg.AddEntry(histos[1],"Post fit pdf","l")
    
    for i in range(2,len(histos)):
        histos[i].SetLineColor(colors[i])
        histos[i].Draw("histsame")
        name = histos[i].GetName().split("_")
        leg.AddEntry(histos[i],name[2],"l")

    hdata.SetMarkerStyle(20)
    hdata.SetMarkerColor(ROOT.kBlack)
    hdata.SetLineColor(ROOT.kBlack)
    hdata.SetMarkerSize(0.7)
    hdata.Draw("samePE")
    leg.AddEntry(hdata,"MC simulation","lp")
        
    leg.SetLineColor(0)
    leg.Draw("same")
    
    chi2 = getChi2proj(histos[1],hdata)
    print "Projection %s: Chi2/ndf = %.2f/%i"%(axis,chi2[0],chi2[1]),"= %.2f"%(chi2[0]/chi2[1])," prob = ",ROOT.TMath.Prob(chi2[0],chi2[1])

    pt = ROOT.TPaveText(0.18,0.06,0.54,0.17,"NDC")
    pt.SetTextFont(62)
    pt.SetTextSize(0.04)
    pt.SetTextAlign(12)
    pt.SetFillColor(0)
    pt.SetBorderSize(0)
    pt.SetFillStyle(0)
    pt.AddText("Chi2/ndf = %.2f/%i = %.2f"%(chi2[0],chi2[1],chi2[0]/chi2[1]))
    pt.AddText("Prob = %.3f"%ROOT.TMath.Prob(chi2[0],chi2[1]))
    pt.Draw()

    pt2 = ROOT.TPaveText(0.18,0.70,0.53,0.83,"NDC")
    pt2.SetTextFont(62)
    pt2.SetTextSize(0.04)
    pt2.SetTextAlign(12)
    pt2.SetFillColor(0)
    pt2.SetBorderSize(0)
    pt2.SetFillStyle(0)
    pt2.AddText(extra1)
    pt2.AddText(extra2)
    pt2.Draw()
    
    c.cd()
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
    pad2.SetTopMargin(0.1)
    pad2.SetBottomMargin(0.4)
    pad2.SetGridy()
    pad2.Draw()
    pad2.cd()
    graphs = addPullPlot(hdata,histos[0],histos[1],nBins)
    #graphs[0].Draw("AP")
    graphs[1].Draw("AB")
    print "save output as "+options.output+"PostFit"+options.label+"_"+htitle.replace(' ','_')+".pdf"
    c.SaveAs(options.output+"PostFit"+options.label+"_"+htitle.replace(' ','_')+".png")
    c.SaveAs(options.output+"PostFit"+options.label+"_"+htitle.replace(' ','_')+".pdf")
    c.SaveAs(options.output+"PostFit"+options.label+"_"+htitle.replace(' ','_')+".root")




def getMV(binnumber):
    i=0
    for xk, xv in xBins_redux.iteritems():
         for yk, yv in yBins_redux.iteritems():
             for zk,zv in zBins_redux.iteritems():
                 if i==binnumber:
                     return [xv,yv,zv]
                 i+=1


#def groupBinsInMjet1Mjet2Plane(seeds,res):
    #groupsx =[]
    #groupsy =[]
    #i=0
    #if 215*res >= 2.:
        #print "try summing over mjet bins"
        #for seed in seeds:
            #for seed2 in seeds:
                #groupsx.append([])
                #groupsy.append([])
                #for xk, xv in xBins_redux.iteritems():
                    #for yk, yv in yBins_redux.iteritems():
                        #if xBinslowedge[xk] >= seed*(1-res) and xBinslowedge[xk] <= seed*(1+res):
                            #if yBinslowedge[yk] >= seed2*(1-res) and yBinslowedge[yk] <= seed2*(1+res):
                                ##print yBinslowedge[yk]
                                #groupsx[i].append(xv)
                                #groupsy[i].append(yv)
            #i+=1
    #else:
        #i2=0
        #print " use input binning for chi2"
        #for xk, xv in xBins_redux.iteritems():
           #groupsx.append([xv])
           #i2+=1
        #for yk, yv in yBins_redux.iteritems():
           #groupsy.append([yv])
           #i+=1    
    #return [groupsx,groupsy]
            

def smearOverResolution(mj1,mj2,zbin,pdf,data,norm,res,datahist=0):
    d=0
    p=0
    e=0
    #if zbin==1:
        #print "start smearing for zbin "+str(zbin)
        #print mj1 
        #print mj2 
        #print "1-res "+str(mj1*(1-res))
        #print "1+res "+str(mj1*(1+res))
        #print xBinslowedge[5]
        #print "smear over " 
    for xk, xv in xBins_redux.iteritems():
        if xBinslowedge[xk] < mj1*(1-res) or xBinslowedge[xk] > mj1*(1+res):
            continue
        for yk, yv in yBins_redux.iteritems():
            if yBinslowedge[yk] < mj2*(1-res) or yBinslowedge[yk] > mj2*(1+res):
                continue
            MJ1.setVal(xv)
            MJ2.setVal(yv)
            #if zbin==1:
                #print str(xv)+" , " +str(yv)
            d += data.weight(argset)
            binV = zBinsWidth[zbin]*xBinsWidth[xk]*yBinsWidth[yk]
            p += pdf.getVal(argset)*binV*norm
            e += pow(datahist.GetBinError(xk,yk,zbin),1/2.)
    
    return [d,p,ROOT.TMath.Sqrt(e)]

    

#def getChi2(pdf,data,norm,listOf_mj1,listOf_mj2,option="",res=0.1,datahist=0):
    #pr=[]
    #dr=[]
    #error_dr=[]
    #testbins = []
    #for xv in listOf_mj1:
        #for yv in listOf_mj2:
             #for zk,zv in zBins_redux.iteritems():
                 #MJJ.setVal(zv)
                 #l = smearOverResolution(xv,yv,zk,pdf,data,norm,res,datahist)
                 #dr.append(l[0])
                 #pr.append(l[1])
                 #error_dr.append(l[2])
    #ndof = 0
    #nb =0
    #chi2 = 0
    ##print bins
    #for i in range(0,len(pr)):
        #if dr[i] < 0.1e-10:
            ##print i
            #continue
        #if ROOT.TMath.Abs(dr[i] - pr[i])/ROOT.TMath.Sqrt(dr[i]) > 10:
            #print " bin  "+str(getMV(i)) + " data  " +str(dr[i])+ " kernel "+str(pr[i]) + " diff "+ str((dr[i] - pr[i])/ROOT.TMath.Sqrt(dr[i]))
        #ndof+=1
        ##chi2+= pow((dr[i] - pr[i]),2)/pow(error_dr[i],2)
        #if option=="" or option=="BakerCousins":
            #chi2+= 2*( pr[i] - dr[i] + dr[i]* ROOT.TMath.Log(dr[i]/pr[i]))
        #if option=="Neyman":
            #chi2+= pow((dr[i] - pr[i]),2)/pow(error_dr[i],2)
        #if option=="Pearson":
            #chi2+= pow((dr[i] - pr[i]),2)/pr[i]
    #return [chi2,ndof-1]
    
    
    
def getChi2(pdf,data,norm,workspace,option="",datahist=0):
    MJ1= workspace.var("MJ1");
    MJ2= workspace.var("MJ2");
    MJJ= workspace.var("MJJ");
    del workspace
    
    argset = ROOT.RooArgSet();
    argset.add(MJJ);
    argset.add(MJ2);
    argset.add(MJ1);
    pr=[]
    dr=[]
    error_dr=[]
    for xk, xv in xBins_redux.iteritems():
         MJ1.setVal(xv)
         for yk, yv in yBins_redux.iteritems():
             MJ2.setVal(yv)
             for zk,zv in zBins_redux.iteritems():
                 MJJ.setVal(zv)
                 binV = zBinsWidth[zk]*xBinsWidth[xk]*yBinsWidth[yk]
                 dr.append(data.weight(argset))
                 if datahist!=0:    
                    error_dr.append(datahist.GetBinError(xk,yk,zk))
                 else:
                     error_dr.append(ROOT.TMath.Sqrt(data.weight(argset)))
                 pr.append( pdf.getVal(argset)*binV*norm)
                 if error_dr[-1]==0:
                     continue
                 #if pow(dr[-1] - pr[-1],2)/error_dr[-1] > 10:
                 #   print "mjet1  "+str(xv) + " mjet2 "+ str(yv)+" mjj "+str(zv)+ " data  " +str(dr[-1])+ " kernel "+str(pr[-1]) + " diff "+ str((dr[-1] - pr[-1])) +"      error data "+str(error_dr[-1])  
    ndof = 0
    chi2 = 0
    for i in range(0,len(pr)):
        if dr[i] < 10e-10:
            continue
        ndof+=1
        if option=="" or option=="BakerCousins":
            chi2+= 2*( pr[i] - dr[i] + dr[i]* ROOT.TMath.Log(dr[i]/pr[i]))
        if option=="Neyman":
            if error_dr[i] ==0.0:
                print "error is zero !?"
                continue
            c = pow((dr[i] - pr[i]),2)/pow(error_dr[i],1)
            chi2+= c
        if option=="Pearson":
            chi2+= pow((dr[i] - pr[i]),2)/pr[i]
        if option=="Neyman2":
            chi2+= pow((dr[i] - pr[i]),2)/pow(dr[i],1)
    return [chi2,ndof]


def setHistoErrorsToSQRT(hist):
    for i in range(1,hist.GetNbinsX()+1):
        hist.SetBinError(i,ROOT.TMath.Sqrt(hist.GetBinContent(i)))
    return hist

def doZprojection(pdfs,data,norm_nonres,norm_wres, norm_zres,norm_s,Binslowedge,Bins_redux,binWidths,workspace,options):
    zBinslowedge = Binslowedge
    xBinsWidth = binWidths[0]
    yBinsWidth = binWidths[1]
    zBinsWidth = binWidths[2]
    xBins_redux = Bins_redux[0]
    yBins_redux = Bins_redux[1]
    zBins_redux = Bins_redux[2]
    
    # get variables from workspace 
    MJ1= workspace.var("MJ1");
    MJ2= workspace.var("MJ2");
    MJJ= workspace.var("MJJ");
    del workspace
    
    argset = ROOT.RooArgSet();
    argset.add(MJJ);
    argset.add(MJ2);
    argset.add(MJ1);
    # do some z projections
    h=[]
    lv=[]
    test=[]
    dh = ROOT.TH1F("dh","dh",len(zBinslowedge)-1,zBinslowedge)
    neventsPerBin = {}
    for zk,zv in zBins_redux.iteritems():
        neventsPerBin[zk]=0 
    for p in pdfs:
        h.append( ROOT.TH1F("h_"+p.GetName(),"h_"+p.GetName(),len(zBinslowedge)-1,zBinslowedge))
        lv.append({})
    for i in range(0,len(pdfs)):
        for zk,zv in zBins_redux.iteritems():
            lv[i][zv]=0 
    for zk,zv in zBins_redux.iteritems():
        MJJ.setVal(zv)
        for yk, yv in yBins_redux.iteritems():
             MJ2.setVal(yv)
             for xk, xv in xBins_redux.iteritems():
                 MJ1.setVal(xv)
		 neventsPerBin[zk] += data.weight(argset)
                 i=0
                 binV = zBinsWidth[zk]*xBinsWidth[xk]*yBinsWidth[yk]
                 
                 for p in pdfs:

                    #if "pdfdata" in p.GetName():
                            #lv[i][zv] += p.weight(argset)#p.evaluate()*binV
                    #else:
                        #if "Jets" in p.GetName() or "Signal" in p.GetName():
                            ##print ' "integrate" over analytical function'
                            #nn=10
                            #for n in range(0,nn):
                                #w = zBinsWidth[zk]
                                #step = w/float(nn)
                                #MJJ.setVal(zv+n*step)
                                #if zv+n*step >= zv+w:
                                    #continue
                                #lv[i][zv]+= p.getVal(argset)*binV/w*step
                        #else:
                            #lv[i][zv] += p.getVal(argset)*binV
                    lv[i][zv] += p.getVal(argset)*binV
                    i+=1
    #print 'z projection '
    for i in range(0,len(pdfs)):
        for zk,zv in zBins_redux.iteritems():
           if "nonRes" in str(pdfs[i].GetName()):
	     print "nonRes: ",pdfs[i].GetName()
	     h[i].Fill(zv,lv[i][zv]*norm_nonres)
	   if "Wjet" in str(pdfs[i].GetName()):
	     print "Res: ",pdfs[i].GetName()
	     print norm_wres
	     h[i].Fill(zv,lv[i][zv]*norm_wres)
           if "Zjet" in str(pdfs[i].GetName()):
	     print "Res: ",pdfs[i].GetName()
	     print norm_zres
	     h[i].Fill(zv,lv[i][zv]*norm_wres)  
           if "model_b" in str(pdfs[i].GetName()):
	     print "all bkg contributions: ",pdfs[i].GetName()
	     h[i].Fill(zv,lv[i][zv]*(norm_wres+norm_zres+norm_nonres))
           if "model_s" in str(pdfs[i].GetName()):
	     print "full model : ",pdfs[i].GetName()
	     h[i].Fill(zv,lv[i][zv]*(norm_wres+norm_zres+norm_nonres+norm_s)) 
           if "sig" in str(pdfs[i].GetName()):
	     print "signal model : ",pdfs[i].GetName()
	     h[i].Fill(zv,lv[i][zv]*(norm_s))
    
    #htot = ROOT.TH1F("htot","htot",len(zBinslowedge)-1,zBinslowedge)
    #htot.Add(h[1])
    #htot.Add(h[2])
    #hfinals = []
    #hfinals.append(h[0])
    #hfinals.append(htot)
    #hfinals.append(h[2])
    #for i in range(3,len(h)): hfinals.append(h[i])
    for b,v in neventsPerBin.iteritems(): dh.SetBinContent(b,v)
    dh.SetBinErrorOption(ROOT.TH1.kPoisson)
    MakePlots(h,dh,'z',zBinslowedge,options)


def doXprojection(pdfs,data,norm_nonres,norm_wres,norm_zres,norm_s,Binslowedge,Bins_redux,binWidths,workspace,options):
    xBinslowedge = Binslowedge
    xBinsWidth = binWidths[0]
    yBinsWidth = binWidths[1]
    zBinsWidth = binWidths[2]
    xBins_redux = Bins_redux[0]
    yBins_redux = Bins_redux[1]
    zBins_redux = Bins_redux[2]
    
    # get variables from workspace 
    MJ1= workspace.var("MJ1");
    MJ2= workspace.var("MJ2");
    MJJ= workspace.var("MJJ");
    del workspace
    
    argset = ROOT.RooArgSet();
    argset.add(MJJ);
    argset.add(MJ2);
    argset.add(MJ1);
    h=[]
    lv=[]
    proj = ROOT.TH1F("px","px",len(xBinslowedge)-1,xBinslowedge)
    neventsPerBin = {}
    for xk,xv in xBins_redux.iteritems():
        neventsPerBin[xk]=0
    for p in pdfs:
        h.append( ROOT.TH1F("hx_"+p.GetName(),"hx_"+p.GetName(),len(xBinslowedge)-1,xBinslowedge))
        lv.append({})
    for xk, xv in xBins_redux.iteritems():
         MJ1.setVal(xv)
         for i in range(0,len(pdfs)):
            lv[i][xv]=0
         for yk, yv in yBins_redux.iteritems():
             MJ2.setVal(yv)
             for zk,zv in zBins_redux.iteritems():
                 MJJ.setVal(zv)
                 i=0
                 binV = zBinsWidth[zk]*xBinsWidth[xk]*yBinsWidth[yk]
		 neventsPerBin[xk] += data.weight(argset)
                 for p in pdfs:
                     #if "postfit" in p.GetName():
                         ##test = p.createProjection(argset).getVal(argset)
                         ##lv[i][xv] += test*binV
                         ##print test
                         #if "data" in p.GetName():
                            #lv[i][xv] += p.weight(argset)#p.evaluate()*binV
                         #else:
                             #lv[i][xv] += p.evaluate()*binV
                         ##lv[i][xv] += p.expectedEvents(argset)*binV
                         ##print p.expectedEvents(argset)*binV
                         ##print "evalueate "+str( lv[i][xv])
                         ##print "getVal "+str(p.getVal(argset)*binV)
                         
                     #else:
                        #if "Jets" in p.GetName() or "jets" in p.GetName() or "Signal" in p.GetName():
                            #print ' "integrate" over analytical function'
                        #nn=500
                        #for n in range(0,nn):
                        #        w = xBinsWidth[xk]
                        #        step = w/float(nn)
                        #        MJ1.setVal(xv+n*step)
                        #        if xv+n*step >= xv+w:
                        #            continue
                        #        lv[i][xv]+= p.getVal(argset)*(binV/w)*step
                        #else:
                        #    lv[i][xv] += p.getVal(argset)*binV
                    #i+=1
                    lv[i][xv] += p.getVal(argset)*binV
                    i+=1
    for i in range(0,len(pdfs)):
        for key, value in lv[i].iteritems():
            if "nonRes" in str(pdfs[i].GetName()): h[i].Fill(key,value*norm_nonres)
	    if "Wjet" in str(pdfs[i].GetName()): h[i].Fill(key,value*norm_wres)
	    if "Zjet" in str(pdfs[i].GetName()): h[i].Fill(key,value*norm_zres)
            if "model_b" in str(pdfs[i].GetName()): h[i].Fill(key,value*(norm_nonres+norm_wres+norm_zres))
            if "model_s" in str(pdfs[i].GetName()): h[i].Fill(key,value*(norm_nonres+norm_wres+norm_zres+norm_s))

    #htot = ROOT.TH1F("htot","htot",len(xBinslowedge)-1,xBinslowedge)
    #htot.Add(h[1])
    #htot.Add(h[2])
    #hfinals = []
    #hfinals.append(h[0])
    #hfinals.append(htot)
    #for i in range(3,len(h)): hfinals.append(h[i])
    for b,v in neventsPerBin.iteritems(): proj.SetBinContent(b,v)
    proj.SetBinErrorOption(ROOT.TH1.kPoisson)    
    MakePlots(h,proj,'x',xBinslowedge,options)    
    

def doYprojection(pdfs,data,norm_nonres,norm_wres,norm_zres,norm_s,Binslowedge,Bins_redux,binWidths,workspace,options):
    yBinslowedge = Binslowedge
    xBinsWidth = binWidths[0]
    yBinsWidth = binWidths[1]
    zBinsWidth = binWidths[2]
    xBins_redux = Bins_redux[0]
    yBins_redux = Bins_redux[1]
    zBins_redux = Bins_redux[2]
    
    # get variables from workspace 
    MJ1= workspace.var("MJ1");
    MJ2= workspace.var("MJ2");
    MJJ= workspace.var("MJJ");
    del workspace
    
    argset = ROOT.RooArgSet();
    argset.add(MJJ);
    argset.add(MJ2);
    argset.add(MJ1);
    h=[]
    lv=[]
    proj = ROOT.TH1F("py","py",len(yBinslowedge)-1,yBinslowedge)
    neventsPerBin = {}
    for yk,yv in yBins_redux.iteritems():
        neventsPerBin[yk]=0
    for p in pdfs:
        h.append( ROOT.TH1F("hy_"+p.GetName(),"hy_"+p.GetName(),len(yBinslowedge)-1,yBinslowedge))
        lv.append({})
    for yk, yv in yBins_redux.iteritems():
         MJ2.setVal(yv)
         for i in range(0,len(pdfs)):
            lv[i][yv]=0
         for xk, xv in xBins_redux.iteritems():
             MJ1.setVal(xv)
             for zk,zv in zBins_redux.iteritems():
                 MJJ.setVal(zv)
                 i=0
                 #proj.Fill(yv,data.weight(argset))
		 neventsPerBin[yk] += data.weight(argset)
                 binV = zBinsWidth[zk]*xBinsWidth[xk]*yBinsWidth[yk]
                 for p in pdfs:
                    #if "pdfdata" in p.GetName():
                            #lv[i][yv] += p.weight(argset)#p.evaluate()*binV
                    #else:
                        #if "Jets" in p.GetName() or "Signal" in p.GetName():
                            ##print ' "integrate" over analytical function'
                            #nn=100
                            #for n in range(0,nn):
                                #w = yBinsWidth[yk]
                                #step = w/float(nn)
                                #MJ2.setVal(yv+n*step)
                                #if yv+n*step >= yv+w:
                                    #continue
                                #lv[i][yv]+= p.getVal(argset)*(binV/w)*step
                        #else:
                            #lv[i][yv] += p.getVal(argset)*binV
                    #i+=1

                    lv[i][yv] += p.getVal(argset)*binV
                    i+=1
    for i in range(0,len(pdfs)):
        for key, value in lv[i].iteritems():
            if "nonRes" in str(pdfs[i].GetName()): h[i].Fill(key,value*norm_nonres)
	    if "Wjet" in str(pdfs[i].GetName()): h[i].Fill(key,value*norm_wres)
	    if "Zjet" in str(pdfs[i].GetName()): h[i].Fill(key,value*norm_zres)
            if "model_b" in str(pdfs[i].GetName()): h[i].Fill(key,value*(norm_nonres+norm_wres+norm_zres))
            if "model_s" in str(pdfs[i].GetName()): h[i].Fill(key,value*(norm_nonres+norm_wres+norm_zres+norm_s))

    htot = ROOT.TH1F("htot","htot",len(yBinslowedge)-1,yBinslowedge)
    #htot.Add(h[1])
    #htot.Add(h[2])
    #hfinals = []
    #hfinals.append(h[0])
    #hfinals.append(htot)
    #for i in range(3,len(h)): hfinals.append(h[i])
    for b,e in neventsPerBin.iteritems(): proj.SetBinContent(b,e)
    proj.SetBinErrorOption(ROOT.TH1.kPoisson)    
    MakePlots(h,proj,'y',yBinslowedge,options)  

 

def addPullPlot(hdata,hprefit,hpostfit,nBins):
    #print "make pull plots: (data-fit)/sigma_data"
    N = hdata.GetNbinsX()
    gpost = ROOT.TGraph(0)
    gpre  = ROOT.TGraph(0)
    for i in range(1,N+1):
        m = hdata.GetXaxis().GetBinCenter(i)
        if hdata.GetBinContent(i) == 0:
            continue
        ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/hdata.GetBinError(i)
        yprefit  = (hdata.GetBinContent(i) - hprefit.GetBinContent(i))/hdata.GetBinError(i)
        gpost.SetPoint(i-1,m,ypostfit)
        gpre.SetPoint(i-1,m,yprefit)
    #gpost.Divide(hdata,hpostfit,"pois")
    #gpre.Divide(hdata,hprefit,"pois")
    gpost.SetLineColor(colors[1])
    gpre.SetLineColor(colors[0])
    gpost.SetMarkerColor(colors[1])
    gpre.SetMarkerColor(colors[0])
    gpost.SetFillColor(ROOT.kBlue)
    gpost.SetMarkerSize(1)
    gpre.SetMarkerSize(1)
    gpre.SetMarkerStyle(4)
    gpost.SetMarkerStyle(3)
    
    #gt = ROOT.TH1F("gt","gt",hdata.GetNbinsX(),hdata.GetXaxis().GetXmin(),hdata.GetXaxis().GetXmax())
    gt = ROOT.TH1F("gt","gt",len(nBins)-1,nBins)
    gt.SetTitle("")
    gt.SetMinimum(-3.999);
    gt.SetMaximum(3.999);
    gt.SetDirectory(0);
    gt.SetStats(0);
    gt.SetLineStyle(0);
    gt.SetMarkerStyle(20);
    gt.GetXaxis().SetTitle(hprefit.GetXaxis().GetTitle());
    gt.GetXaxis().SetLabelFont(42);
    gt.GetXaxis().SetLabelOffset(0.02);
    gt.GetXaxis().SetLabelSize(0.15);
    gt.GetXaxis().SetTitleSize(0.15);
    gt.GetXaxis().SetTitleOffset(1);
    gt.GetXaxis().SetTitleFont(42);
    gt.GetYaxis().SetTitle("#frac{data-fit}{#sigma}");
    gt.GetYaxis().CenterTitle(True);
    gt.GetYaxis().SetNdivisions(205);
    gt.GetYaxis().SetLabelFont(42);
    gt.GetYaxis().SetLabelOffset(0.007);
    gt.GetYaxis().SetLabelSize(0.15);
    gt.GetYaxis().SetTitleSize(0.15);
    gt.GetYaxis().SetTitleOffset(0.3);
    gt.GetYaxis().SetTitleFont(42);
    gt.GetXaxis().SetNdivisions(505)
    #gpre.SetHistogram(gt);
    gpost.SetHistogram(gt);       
    return [gpre,gpost] 
 

def builtFittedPdf(pdfs,coefficients):
    result = RooAddPdf(pdfs,coefficients)
    return result


def getChi2fullModel(pdf,data,norm,workspace):
    MJ1= workspace.var("MJ1");
    MJ2= workspace.var("MJ2");
    MJJ= workspace.var("MJJ");
    del workspace
    
    argset = ROOT.RooArgSet();
    argset.add(MJJ);
    argset.add(MJ2);
    argset.add(MJ1);
    pr=[]
    dr=[]
    for xk, xv in xBins.iteritems():
         MJ1.setVal(xv)
         for yk, yv in yBins.iteritems():
             MJ2.setVal(yv)
             for zk,zv in zBins.iteritems():
                 MJJ.setVal(zv)
                 dr.append(data.weight(argset))
                 binV = zBinsWidth[zk]*xBinsWidth[xk]*yBinsWidth[yk]
                 pr.append( pdf.getVal(argset)*binV*norm)
    ndof = 0
    chi2 = 0
    for i in range(0,len(pr)):
        if dr[i] < 10e-10:
            continue
        ndof+=1
        #chi2+= pow((dr[i] - pr[i]),2)/pr[i]
        chi2+= 2*( pr[i] - dr[i] + dr[i]* ROOT.TMath.Log(dr[i]/pr[i]))

    return [chi2,ndof]

def getChi2proj(histo_pdf,histo_data):
    pr=[]
    dr=[]
    for b in range(1,histo_pdf.GetNbinsX()+1):
     dr.append(histo_data.GetBinContent(b))
     pr.append(histo_pdf.GetBinContent(b))
    
    ndof = 0
    chi2 = 0
    for i in range(0,len(pr)):
        if dr[i] < 10e-10:
            continue
        if pr[i] < 10e-10:
            continue
        ndof+=1
        #chi2+= pow((dr[i] - pr[i]),2)/pr[i]
	#print i,dr[i],pr[i],(dr[i] - pr[i]),pow((dr[i] - pr[i]),2)/pr[i],(dr[i] - pr[i])/histo_data.GetBinError(i+1)
        chi2+= 2*( pr[i] - dr[i] + dr[i]* ROOT.TMath.Log(dr[i]/pr[i]))

    return [chi2,ndof]

def getVJetsPdf():

 wRes=ROOT.RooWorkspace("wRes","wRes")
 wRes.factory(options.var+varBins[options.var])
 wRes.var(options.var).SetTitle(varName[options.var])    

if __name__=="__main__":
     
     parser = optparse.OptionParser()
     parser.add_option("-o","--output",dest="output",help="Output folder name",default='')
     parser.add_option("-n","--name",dest="name",help="Input workspace",default='workspace.root')
     parser.add_option("-i","--input",dest="input",help="Input nonRes histo",default='JJ_HPHP.root')
     parser.add_option("-x","--xrange",dest="xrange",help="set range for x bins in projection",default="0,-1")
     parser.add_option("-y","--yrange",dest="yrange",help="set range for y bins in projection",default="0,-1")
     parser.add_option("-z","--zrange",dest="zrange",help="set range for z bins in projection",default="0,-1")
     parser.add_option("-p","--projection",dest="projection",help="choose which projection should be done",default="xyz")
     parser.add_option("-d","--data",dest="data",action="store_true",help="make also postfit plots",default=True)
     parser.add_option("-l","--label",dest="label",help="add extra label such as pythia or herwig",default="")
     parser.add_option("--log",dest="log",help="write fit result to log file",default="fit_results.log")
     parser.add_option("--pdfz",dest="pdfz",help="name of pdfs lie PTZUp etc",default="")
     parser.add_option("--pdfx",dest="pdfx",help="name of pdfs lie PTXUp etc",default="")
     parser.add_option("--pdfy",dest="pdfy",help="name of pdfs lie PTYUp etc",default="")
    
     
     (options,args) = parser.parse_args()
     finMC = ROOT.TFile(options.input,"READ");
     hinMC = finMC.Get("nonRes");
     purity = options.input.replace('.root','').split('_')[-1] 
     sig = "BulkGWW"
                        
     #################################################
     xBins= getListOfBins(hinMC,"x")
     xBinslowedge = getListOfBinsLowEdge(hinMC,'x')
     xBinsWidth   = getListOfBinsWidth(hinMC,"x")
     print "x bins:"
     print xBins
     print "x bins low edge:"
     print xBinslowedge
     print "x bins width:"
     print xBinsWidth
     
     #################################################
     print
     yBins= getListOfBins(hinMC,"y")
     yBinslowedge = getListOfBinsLowEdge(hinMC,'y')     
     yBinsWidth   = getListOfBinsWidth(hinMC,"y")
     print "y bins:"
     print yBins
     print "y bins low edge:"
     print yBinslowedge
     print "y bins width:"
     print yBinsWidth
     
     #################################################
     print 
     zBins= getListOfBins(hinMC,"z")
     zBinslowedge = getListOfBinsLowEdge(hinMC,'z')
     zBinsWidth   = getListOfBinsWidth(hinMC,"z")
     print "z bins:"
     print zBins
     print "z bins low edge:"
     print zBinslowedge
     print "z bins width:"
     print zBinsWidth
            
     #################################################                
     print 
     print "open file " +options.name
     f = ROOT.TFile(options.name,"READ")
     workspace = f.Get("w")
     f.Close()


     workspace.Print()

     model = workspace.pdf("model_b") 
     data = workspace.data("data_obs")
     data.Print()
     print
     print "Observed number of events:",data.sumEntries()
     args  = model.getComponents()
     print "Expected number of QCD events:",(args["pdf_binJJ_"+purity+"_13TeV_bonly"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_proc_nonRes"].getVal()
     print "Expected number of V+jets events:",(args["pdf_binJJ_"+purity+"_13TeV_bonly"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_proc_Vjet"].getVal()
     print 
         
     #################################################
     print
     fitresult = model.fitTo(data,ROOT.RooFit.SumW2Error(not(options.data)),ROOT.RooFit.Minos(0),ROOT.RooFit.Verbose(0),ROOT.RooFit.Save(1),ROOT.RooFit.NumCPU(8))   
     fitresult.Print() 
     if options.log!="":
     	 params = fitresult.floatParsFinal()
     	 paramsinit = fitresult.floatParsInit()
     	 paramsfinal = ROOT.RooArgSet(params)
     	 paramsfinal.writeToFile(options.output+options.log)
     	 logfile = open(options.output+options.log,"a::ios::ate")
     	 logfile.write("#################################################\n")
     	 for k in range(0,len(params)):
     	     pf = params.at(k)
	     print pf.GetName(), pf.getVal(), pf.getError(), "%.2f"%(pf.getVal()/pf.getError())
     	     if not("nonRes" in pf.GetName()):
     		 continue
     	     pi = paramsinit.at(k)
     	     r  = pi.getMax()-1
     	     #logfile.write(pf.GetName()+" & "+str((pf.getVal()-pi.getVal())/r)+"\\\\ \n")
     	 logfile.close()

     #################################################
     print            
     # try to get kernel Components 
            
     print 
     print "Prefit nonRes pdf:"
     pdf_nonres_shape_prefit = args["nonResNominal_JJ_"+purity+"_13TeV"]
     pdf_nonres_shape_prefit.Print()
     print
     print "Postfit nonRes pdf:"
     pdf_nonres_shape_postfit  = args["shapeBkg_nonRes_JJ_"+purity+"_13TeV"]
     pdf_nonres_shape_postfit.Print()
     pdf_nonres_shape_postfit.funcList().Print()
     pdf_nonres_shape_postfit.coefList().Print()
     print
     print "Postfit V+jets res pdf:"
     pdf_res_shape_postfit  = args["shapeBkg_Vjet_JJ_"+purity+"_13TeV"]
     pdf_res_shape_postfit.Print()
     print
     print "Full post-fit pdf:"     
     pdf_shape_postfit  = args["pdf_binJJ_"+purity+"_13TeV_bonly_nuis"]
     pdf_shape_postfit.Print()
     
     allpdfsz = [] #let's have always pre-fit and post-fit as firt elements here, and add the optional shapes if you want with options.pdf
     allpdfsz.append(pdf_nonres_shape_prefit)
     allpdfsz.append(pdf_nonres_shape_postfit)
     allpdfsz.append(pdf_res_shape_postfit)
     for p in options.pdfz.split(","):
         if p == '': continue
	 print "add pdf:",p
	 args[p].Print()
         allpdfsz.append(args[p])

     allpdfsx = [] #let's have always pre-fit and post-fit as firt elements here, and add the optional shapes if you want with options.pdf
     allpdfsx.append(pdf_nonres_shape_prefit)
     allpdfsx.append(pdf_nonres_shape_postfit)
     allpdfsx.append(pdf_res_shape_postfit)
     for p in options.pdfx.split(","):
         if p == '': continue
	 print "add pdf:",p
	 args[p].Print()
         allpdfsx.append(args[p])

     allpdfsy = [] #let's have always pre-fit and post-fit as firt elements here, and add the optional shapes if you want with options.pdf
     allpdfsy.append(pdf_nonres_shape_prefit)
     allpdfsy.append(pdf_nonres_shape_postfit)
     allpdfsy.append(pdf_res_shape_postfit)
     for p in options.pdfy.split(","):
         if p == '': continue
	 print "add pdf:",p
	 args[p].Print()
         allpdfsy.append(args[p])
	 	 	
     print
     norm_nonres = (args["pdf_binJJ_"+purity+"_13TeV_bonly"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_proc_nonRes"].getVal()
     norm_res = (args["pdf_binJJ_"+purity+"_13TeV_bonly"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_proc_Vjet"].getVal()
     norm_s = (args["pdf_binJJ_"+purity+"_13TeV_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_proc_"+sig].getVal()
     print "QCD normalization after fit "+str(norm_nonres)
     print "V+jets normalization after fit "+str(norm_res)
     print
     
     #################################################
     
     x = getListFromRange(options.xrange)
     y = getListFromRange(options.yrange)
     z = getListFromRange(options.zrange)     
     
     xBins_redux = reduceBinsToRange(xBins,x)
     yBins_redux = reduceBinsToRange(yBins,y)
     zBins_redux = reduceBinsToRange(zBins,z)
     Bins_redux=[xBins_redux,yBins_redux,zBins_redux]
     binWidths =[xBinsWidth,yBinsWidth,zBinsWidth]
     print "x bins reduced:"
     print xBins_redux
     print "y bins reduced:"
     print yBins_redux
     print "z bins reduced:"
     print zBins_redux
     print 

     #################################################     
     #make projections onto MJJ axis
     if options.projection =="z": doZprojection(allpdfsz,data,norm_nonres,norm_res,norm_s,zBinslowedge,Bins_redux,binWidths,workspace,options)
         
     #make projections onto MJ1 axis
     if options.projection =="x": doXprojection(allpdfsx,data,norm_nonres,norm_res,norm_s,xBinslowedge,Bins_redux,binWidths,workspace,options)
                  
     #make projections onto MJ2 axis
     if options.projection =="y": doYprojection(allpdfsy,data,norm_nonres,norm_res,norm_s,yBinslowedge,Bins_redux,binWidths,workspace,options)
         
     if options.projection =="xyz":
        doZprojection(allpdfsz,data,norm_nonres,norm_res,norm_s,zBinslowedge,Bins_redux,binWidths,workspace,options)
	doXprojection(allpdfsx,data,norm_nonres,norm_res,norm_s,xBinslowedge,Bins_redux,binWidths,workspace,options)
	doYprojection(allpdfsy,data,norm_nonres,norm_res,norm_s,yBinslowedge,Bins_redux,binWidths,workspace,options)
     
     #################################################   
     #calculate chi2  
     norm=norm_nonres+norm_res+norm_s
     chi2 = getChi2fullModel(pdf_nonres_shape_postfit,data,norm,workspace)
     print "Chi2/ndof: %.2f/%.2f"%(chi2[0],chi2[1])," = %.2f"%(chi2[0]/chi2[1])," prob = ",ROOT.TMath.Prob(chi2[0], int(chi2[1]))
     
     
    #listOf_mj1 = []#[55,67,82,100,122,149,182,222]
    #listOf_mj2 = listOf_mj1

    #x=55
    #res=0.1
    #while(x < 230):
        #listOf_mj1.append(x)
        #x=x*(1+res)/(1-res)
     #chi2, ndof = getChi2(pdf_shape_postfit,data,norm,workspace,listOf_mj1,listOf_mj1,"",res,hinMC)
     #print "chi2 " +str( chi2)
     #print "ndof " +str(ndof)
     #print "chi2/ndof " +str(chi2/ndof)
     #if ndof ==0:
         #sys.exit()
     #print "probability "+str(ROOT.TMath.Prob(chi2,ndof))
     #print "neyman"
     #chi2,ndof = getChi2(pdf_shape_postfit,data,norm,workspace,"Neyman",hinMC)
     ##chi2, ndof = getChi2(pdf_shape_postfit,data,norm,workspace,listOf_mj1,listOf_mj1,"Neyman",res,hinMC)
     #print "chi2 " +str( chi2)
     #print "ndof " +str(ndof)
     #print "chi2/ndof " +str(chi2/ndof)
     #print "neyman2"
     ##chi2,ndof = getChi2(pdf_shape_postfit,data,norm,workspace,"Neyman2",hinMC)
     ##print "chi2 " +str( chi2)
     ##print "ndof " +str(ndof)
     ##print "chi2/ndof " +str(chi2/ndof)
     ##print "pearson"
     #chi2,ndof = getChi2(pdf_shape_postfit,data,norm,workspace,"Pearson",hinMC)
     ##chi2, ndof = getChi2(pdf_shape_postfit,data,norm,workspace,listOf_mj1,listOf_mj1,"Pearson",res,hinMC)
     #print "chi2 " +str( chi2)
     #print "ndof " +str(ndof)
     #print "chi2/ndof " +str(chi2/ndof)

