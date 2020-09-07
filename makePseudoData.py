import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
from array import array
import copy



def generateBKG(histo,nEvents,binsxy,binsz,args):
    hout = ROOT.TH3F('data','data',len(binsxy)-1,binsxy,len(binsxy)-1,binsxy,len(binsz)-1,binsz)
    hout.FillRandom(histo,int(nEvents))
    data = ROOT.RooDataHist ("toydata", "toydata",args,hout)
    return data

def generateSignal(pdf,args,nEvents):
    if nEvents<=0: return None
    print nEvents
    print pdf 
    print args
    signal = pdf.generate(args,int(round(nEvents,0)))
    return signal

def getSignalFromFile(rfile,nEvents,name):
    hsig = rfile.Get(name)
    hsig.Scale(nEvents/hsig.Integral())
    return hsig

def addVJetsComponent(resbkg,resbkg_events,htmp,args):
    i=0
    for vjets in resbkg:
        if type(vjets) is ROOT.TH3D:
            print 'generate toy from MC '+ vjets.GetName()+' generating events '+str(int(resbkg_events[i]))
            htmp.FillRandom(vjets,int(resbkg_events[i]))
            #vjets.Scale(resbkg_events[i]/vjets.Integral())
            htmp.Add(vjets)
            i+=1
        else:
            v = vjets.generate(args,resbkg_events[i])
            print 'generate toy from pdf '+ vjets.GetName()+' generating events '+str(int(resbkg_events[i]))
            for e in range(0,int(v.sumEntries())):
                a = v.get(e)
                it = a.createIterator()
                var = it.Next()
                x=[]
                while var:
                    x.append(var.getVal())
                    var = it.Next()
                htmp.Fill(x[0],x[1],x[2])
                #print "x "+str(x[0])+" y "+str(x[1])+" z "+str(x[2])
            i+=1
    return htmp
    

def generateToy(histo,nEvents_bkg,resbkg,resbkg_events,binsxy,binsz,pdf,nEvents_sig,args):
    print "bins xy "+str(len(binsxy)) + " bins z "+str(len(binsz))
    hout = ROOT.TH3F('data','data',len(binsxy)-1,binsxy,len(binsxy)-1,binsxy,len(binsz)-1,binsz)
    htmp = ROOT.TH3F('tmp','tmp',len(binsxy)-1,binsxy,len(binsxy)-1,binsxy,len(binsz)-1,binsz)
    print "nevents "+str(nEvents)
    hout.FillRandom(histo,int(nEvents))
    print "Integral1 "+str(hout.Integral())
    htmp = addVJetsComponent(resbkg,resbkg_events,htmp,args)
    print "add number of events "+str(htmp.Integral())
    hout.Add(htmp)
    
    print "Integral "+str(hout.Integral())
    #print nEvents_sig
    #sig = generateSignal(pdf,args,nEvents_sig)
    
    #if sig!=None:
        #print "signal "+str(sig.sumEntries())
        #for i in range(0,int(sig.sumEntries())):
            #a = sig.get(i)
            #it = a.createIterator()
            #var = it.Next()
            #x=[]
            #while var:
                #x.append(var.getVal())
                #var = it.Next()
            ##print x
            #hout.Fill(x[0],x[1],x[2])
            ##print "x "+str(x[0])+" y "+str(x[1])+" z "+str(x[2])
    return hout
    
def generateSignalToy(sigfile,nEvents_sig,sig_name):
    print sigfile
    hout = ROOT.TH3F('data','data',len(binsxy)-1,binsxy,len(binsxy)-1,binsxy,len(binsz)-1,binsz)
    print hout
    hsig = getSignalFromFile(sigfile,nEvents_sig,sig_name)
    hout.Add(hsig)
    print hsig
    print "make signal from histo"
    return hout
 

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
 
    
if __name__=="__main__":
     
     Parser = optparse.OptionParser()
     Parser.add_option("-o","--output",dest="output",help="Output folder name",default='')
     Parser.add_option("-k","--kernel",dest="kernel",help="Input ROOT File name for toy generation",default='JJ_nonRes_3D_HPHP.root')
     Parser.add_option("--norm",dest="norm",help="Input ROOT File name for normalisation",default='JJ_nonRes_HPHP.root')
     Parser.add_option("-l","--label",dest="label",help="add extra label such as pythia or herwig",default="")
     Parser.add_option("--lumi",dest="lumi",action="store",help="set luminosity ",default=35900.)
     Parser.add_option("--useKernel",dest="qcdBkgHisto",help="Name of kernel histo to be used for qcd background",default='histo')
     Parser.add_option("--data",dest="data",help="file to get normalization of real data ",default="")
     Parser.add_option("--workspace",dest="workspace",help="use workspace with this name ",default="")
     Parser.add_option("--purity",dest="purity",help="use this purity ",default="VV_HPHP")
     Parser.add_option("--period",dest="period",help="use this run period ",default="2016")
     Parser.add_option("--which",dest="whichbkg",help="option allows to make pseudodata of vjets background only : allowed are 'all','vjets' and 'sigonly'",default="all")
     
     (options,args) = Parser.parse_args()
     print options
     lumi = options.lumi
     period = options.period
         
     #if period == "2017":
     #   lumi = 41367.
     
     if ROOT.gRandom >=0: del ROOT.gRandom
     ROOT.gRandom = ROOT.TRandom3(0)
     #seed = os.environ["RANDOM"]
     ROOT.gRandom.SetSeed(0) 
     ROOT.RooRandom.randomGenerator().SetSeed(ROOT.gRandom.GetSeed())
     print ROOT.gRandom  
     print ROOT.gRandom.GetSeed()
     
     #fdata =  ROOT.TFile(options.data,"READ")
    
     #datanorm = (fdata.Get("data")).Integral()
    
     purity = options.purity
     sig = "BulkGWW"
     if options.label.find("Wprime")!=-1:
         sig = "WprimeWZ"
     
    
     ############################# extract TH3 histos to generate toys from #############
     if options.whichbkg.find("sigonly")==-1:
     
        forToys = ROOT.TFile(options.kernel,"READ")
        bkg_histo = forToys.Get(options.qcdBkgHisto )
        forBkgNormalisation = ROOT.TFile(options.norm,"READ")
        bkghisto_forNorm = forBkgNormalisation.Get("nonRes")
        
        binsxy = getListOfBinsLowEdge(bkghisto_forNorm,"x")
        binsz  = getListOfBinsLowEdge(bkghisto_forNorm,"z")
        xBins  = getListOfBins(bkghisto_forNorm,"x")
        zBins  = getListOfBins(bkghisto_forNorm,"z")
        xBinsWidth   = getListOfBinsWidth(bkghisto_forNorm,"x")
        zBinsWidth   = getListOfBinsWidth(bkghisto_forNorm,"z")
        
        binWidths=[xBinsWidth,xBinsWidth,zBinsWidth]
        
     
        print bkg_histo
        print bkghisto_forNorm
        print forBkgNormalisation
        print forToys
     
     
        f = ROOT.TFile(options.workspace,"READ")
        workspace = f.Get("w")
        ## get variables from workspace 
        MJ1= workspace.var("MJ1");
        MJ2= workspace.var("MJ2");
        MJJ= workspace.var("MJJ");
        
        ### set a fit Range ########################
        #MJJ.setRange("R1",1856,5000) 
        args_ws = ROOT.RooArgSet(MJ1,MJ2,MJJ)
    
        MX = workspace.var("MH")
        MX.setVal(3000)
        
        signal = workspace.pdf("shapeSig_"+sig+"_JJ_"+purity+"_13TeV_"+period)
        
        
        ##### use shapes from WS for V+jets and ttbar components ########
        #wjet = workspace.pdf("shapeBkg_Wjets_JJ_"+purity+"_13TeV_"+period)
        #zjet = workspace.pdf("shapeBkg_Zjets_JJ_"+purity+"_13TeV_"+period)
        #ttjet = workspace.pdf("shapeBkg_TTJets_JJ_"+purity+"_13TeV_"+period)       
        
        #norm_wjet = (workspace.obj("n_exp_binJJ_"+purity+"_13TeV_"+period+"_proc_Wjets")).getVal()
        #norm_zjet = ( workspace.obj("n_exp_binJJ_"+purity+"_13TeV_"+period+"_proc_Zjets")).getVal()
        #norm_ttjet = ( workspace.obj("n_exp_binJJ_"+purity+"_13TeV_"+period+"_proc_TTJets")).getVal()*1000
        
        ############## use mc for V+jets toys ##############
        fmcWjets = ROOT.TFile("ttbarmodeling/JJ_2016_WJets_"+purity+".root","READ")
        wjet = fmcWjets.Get("WJets")
        fmcZjets = ROOT.TFile("ttbarmodeling/JJ_2016_ZJets_"+purity+".root","READ")
        zjet = fmcZjets.Get("ZJets")
        fmcttjet = ROOT.TFile("ttbarmodeling/JJ_2016_TTJets_"+purity+".root","READ")
        print  "ttbarmodeling/JJ_2016_TTJets_"+purity+".root"
        ttjet = fmcttjet.Get("TTJets")
        
        norm_wjet = wjet.Integral()*float(lumi)
        norm_zjet = zjet.Integral()*float(lumi)
        norm_ttjet = ttjet.Integral()*float(lumi)
        
        print "norm ttjets ", norm_ttjet
        print "norm wjets ", norm_wjet
        print "norm zjets ", norm_zjet
        print ttjet.Integral()
        
        
        
            
        nEvents = bkghisto_forNorm.Integral()*float(lumi)
        print nEvents
        print "for normalisation"
        print bkghisto_forNorm.Integral()
        print norm_wjet
        print norm_zjet
        print "done"
        
        if options.whichbkg.find("sig")==-1:
     
            if options.whichbkg.find("vjets")!=-1 or options.whichbkg.find("Vjets")!=-1:
                nEvents = 0.
            if options.whichbkg.find("ttbar")!=-1 or options.whichbkg.find("TTbar")!=-1:
                nEvents = 0.
                norm_wjet = 0.
                norm_zjet = 0.
            print "test Integral "+str(bkghisto_forNorm.Integral())
            print lumi
            print forBkgNormalisation.Get("nonRes").Integral()
            print "number of events to be generated for the background "+str(nEvents)   
                
            
            
            print "test " +str(nEvents) 
            if options.whichbkg.find("qcd")!=-1:
                print " make toy with qcd only"
                pseudodata = generateToy(bkg_histo,nEvents,[wjet,zjet,ttjet],[0,0,0],binsxy,binsz,None,0,args_ws)
            else:
                pseudodata = generateToy(bkg_histo,nEvents,[wjet,zjet,ttjet],[norm_wjet,norm_zjet,norm_ttjet],binsxy,binsz,None,0,args_ws)
            pseudodata.SetName("data_obs")
            
            outfile = ROOT.TFile(options.output,"RECREATE")
            #pseudodata.Scale(datanorm/pseudodata.Integral())
            pseudodata.Write()
            
            print lumi
        
        outfile.Close()
        
     else: 
            print "create toy containing only signal! "
            signals =  ["WprimeWH"] #["ZprimeZH" ,"ZprimeWW","BulkGZZ","BulkGWW","WprimeWZ"]
            masses = ["4000","2000"]
            categories= ["VH_HPHP","VH_HPLP","VH_LPHP","VV_HPHP","VV_HPLP"]
            
            for signal in signals:
                for mass in masses:
                    for category in categories:
                        outfilename = "/work/dschaefer/CMGToolsForStat10X/CMSSW_10_2_10/src/CMGTools/VVResonances/interactive/results_2016/pseudodata_sigOnly_2016_"+signal+"_"+category+"_M"+mass+".root"
                        rfile = "/work/dschaefer/CMGToolsForStat10X/CMSSW_10_2_10/src/CMGTools/VVResonances/interactive/results_2016/JJ_2016_"+signal+"_sigonly_M"+mass+"_"+category+".root"
                    
                        # JJ_2016_ZprimeWW_sigonly_M2000_VH_HPHP.root
                        f = ROOT.TFile(rfile,"READ")
                        
                        sighist_forNorm = f.Get("sigonly_M"+str(mass))
                        binsxy = getListOfBinsLowEdge(sighist_forNorm,"x")
                        binsz  = getListOfBinsLowEdge(sighist_forNorm,"z")
                        xBins  = getListOfBins(sighist_forNorm,"x")
                        zBins  = getListOfBins(sighist_forNorm,"z")
                        xBinsWidth   = getListOfBinsWidth(sighist_forNorm,"x")
                        zBinsWidth   = getListOfBinsWidth(sighist_forNorm,"z")
                        
                        binWidths=[xBinsWidth,xBinsWidth,zBinsWidth]
                            
                        
                        pseudodata = generateSignalToy(f,500.,"sigonly_M"+str(mass))
                        print pseudodata
                        pseudodata.SetName("data_obs")
                    
                        outfile = ROOT.TFile(outfilename,"RECREATE")
                        pseudodata.Write()
                        outfile.Close()
                        print "generated output file :" +outfilename
            
     
