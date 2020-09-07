import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
from array import array
import copy
from runFitPlots import getListOfBinsLowEdge, doZprojection, getListOfBins, getListOfBinsWidth,reduceBinsToRange, doXprojection,getListFromRange, doYprojection


ROOT.gStyle.SetOptStat(0)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)
colors = [ROOT.kBlack,ROOT.kRed-2,ROOT.kRed+1,ROOT.kRed-1,ROOT.kRed+2,ROOT.kGreen-1,ROOT.kGreen-2,ROOT.kGreen+1,ROOT.kGreen+2,ROOT.kBlue]


def logFitResult(fitresult,toy, outname,events):
    #CMS_VV_JJ_nonRes_OPTXY 
    #CMS_VV_JJ_nonRes_OPTZ  
    #CMS_VV_JJ_nonRes_PTXY  
    #CMS_VV_JJ_nonRes_PTZ   
    #CMS_VV_JJ_nonRes_norm_HPHP 
    #CMS_res_j  
    #CMS_res_prunedj 
    #CMS_scale_j   
    #CMS_scale_prunedj  
    #CMS_tau21_PtDependence   
    #r             
    
    params = fitresult.floatParsFinal()
    params1 = fitresult.floatParsInit()
    paramsfinal = ROOT.RooArgSet(params)
    paramsinit = ROOT.RooArgSet(params1)
    
    logfile = open(outname,"a::ios::ate")
    logfile.write("##################### for toy number %i ############################\n"%(toy))
    #paramsfinal.writeToFile(outname)
    for k in range(0,len(params)):
        pf = params.at(k)
        pi = params1.at(k)
        r  = pi.getMax()-1
        logfile.write(pf.GetName()+" = "+str(pf.getVal())+" - "+str(pf.getErrorLo())+" + "+str(pf.getErrorHi())+" L("+str(pi.getMin())+" "+str(pi.getMax())+")\n")
    logfile.write("event fitted : ef="+str(events))
    logfile.close()



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


def addVJetsComponent(resbkg,resbkg_events,htmp,args):
    i=0
    for vjets in resbkg:
        if type(vjets) is ROOT.TH3D:
            print 'generate toy from MC '+ vjets.GetName()+' generating events '+str(resbkg_events[i])
            htmp.FillRandom(vjets,int(resbkg_events[i]))
            #htmp.Add(vjets)
            i+=1
        else:
            v = vjets.generate(args,resbkg_events[i])
            print 'generate toy from pdf '+ vjets.GetName()+' generating events '+str(resbkg_events[i])
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
    

def generateToy(histo,nEvents_bkg,resbkg,resbkg_events,binsxy,binsz,args,pdf,nEvents_sig,category):
    hout = ROOT.TH3F('data','data',len(binsxy)-1,binsxy,len(binsxy)-1,binsxy,len(binsz)-1,binsz)
    htmp = ROOT.TH3F('tmp','tmp',len(binsxy)-1,binsxy,len(binsxy)-1,binsxy,len(binsz)-1,binsz)
    hout.FillRandom(histo,int(nEvents))
    
    htmp = addVJetsComponent(resbkg,resbkg_events,htmp,args)
    print "add number of events "+str(htmp.Integral())
    hout.Add(htmp)
    print nEvents_sig
    sig = generateSignal(pdf,args,nEvents_sig)
    arglist = ROOT.RooArgList(args)
    if sig!=None:
        print "signal "+str(sig.sumEntries())
        for i in range(0,int(sig.sumEntries())):
            a = sig.get(i)
            it = a.createIterator()
            var = it.Next()
            x=[]
            while var:
                x.append(var.getVal())
                var = it.Next()
            #print x
            hout.Fill(x[0],x[1],x[2])
            #print "x "+str(x[0])+" y "+str(x[1])+" z "+str(x[2])
    print category.getIndex()
    #category.setIndex(0)
    #print category.getIndex()
    print category.getLabel()
    print arglist
    print hout
    print hout.Integral()
   # data = ROOT.RooDataHist("toydata","toydata",arglist,ROOT.RooFit.Index(category),ROOT.RooFit.Import(category.getLabel(),hout))
    data = ROOT.RooDataHist("toydata","toydata",arglist,ROOT.RooFit.Index(category),ROOT.RooFit.Import(category.getLabel(),hout)) 
    print data
    #data = ROOT.RooDataHist("toydata", "toydata",arglist,hout)
    return data
    
    
def getNominalData(histo,nEvents_bkg,resbkg,resbkg_events,binsxy,binsz,args,pdf,nEvents_sig,category):
    histo.Scale(nEvents_bkg/histo.Integral())
    i=0
    for vjets in resbkg:
        print vjets.GetName()
        print resbkg_events[i]
        vjets.Scale(resbkg_events[i])
        histo.Add(vjets)
        i+=1
        
    sig = generateSignal(pdf,args,nEvents_sig)
    arglist = ROOT.RooArgList(args)
    if sig!=None:
        print sig.sumEntries()
        for i in range(0,int(sig.sumEntries())):
            a = sig.get(i)
            it = a.createIterator()
            var = it.Next()
            x=[]
            while var:
                x.append(var.getVal())
                var = it.Next()
            #print x
            histo.Fill(x[0],x[1],x[2])
    data = ROOT.RooDataHist("data","data",arglist,ROOT.RooFit.Index(category),ROOT.RooFit.Import(category.getLabel(),histo)) 
    return data    

if __name__=="__main__":
     
     Parser = optparse.OptionParser()
     Parser.add_option("-o","--output",dest="output",help="Output folder name",default='')
     Parser.add_option("-n","--name",dest="name",help="Input ROOT File name",default='/home/dschaefer/DiBoson3D/test_kernelSmoothing_pythia/workspace_pythia_nominal.root')
     Parser.add_option("-k","--kernel",dest="kernel",help="Input ROOT File name for toy generation",default='JJ_nonRes_3D_HPHP.root')
     Parser.add_option("--norm",dest="norm",help="Input ROOT File name for normalisation",default='JJ_nonRes_HPHP_nominal.root')
     Parser.add_option("--signalStrength",dest="signalStrength",help="Input ROOT File name for extracting signal strenght parameter",default="/home/dschaefer/Limits3DFit/biasTest/scanSignalStrength.root")
     Parser.add_option("-t","--toys",dest="toys",action="store",help="set number of toys to be generated",default=1)
     Parser.add_option("-s","--expSig",dest="expSig",action="store",help="make signal toys with signal strenght corresponding to expSig sigma",default=3)
     Parser.add_option("-x","--xrange",dest="xrange",help="set range for x bins in projection",default="0,-1")
     Parser.add_option("-y","--yrange",dest="yrange",help="set range for y bins in projection",default="0,-1")
     Parser.add_option("-z","--zrange",dest="zrange",help="set range for z bins in projection",default="0,-1")
     Parser.add_option("-l","--label",dest="label",help="add extra label such as pythia or herwig",default="")
     Parser.add_option("--lumi",dest="lumi",action="store",help="set luminosity ",default=35900.)
     Parser.add_option("--mass",dest="mass",action="store",help="set mass for signal ",default=1500)
     Parser.add_option("--useKernel",dest="qcdBkgHisto",help="Name of kernel histo to be used for qcd background",default='histo')
     
     (options,args) = Parser.parse_args()
     print options
     
     period = 2017
     if options.name.find("2016")!=-1:
         period = 2016
      
     if ROOT.gRandom >=0: del ROOT.gRandom
     ROOT.gRandom = ROOT.TRandom3(0)
     #seed = os.environ["RANDOM"]
     ROOT.gRandom.SetSeed(0) 
     ROOT.RooRandom.randomGenerator().SetSeed(ROOT.gRandom.GetSeed())
     print ROOT.gRandom  
     print ROOT.gRandom.GetSeed()
     
    
     purity = "HPHP"
     if options.name.find("HPLP")!=-1:
         purity ="HPLP"
     if options.name.find("LPLP")!=-1:
         purity ="LPLP"
     sig = "BulkGWW"
     if options.label.find("Wprime")!=-1:
         sig = "WprimeWZ"
     if options.label.find("Zprime")!=-1:
         sig = "ZprimeWW"
     mass = float(options.mass)
     lumi = float(options.lumi)
    
     ############### extract needed pdfs from workspace #############################
     print "open file " +options.name
     f = ROOT.TFile(options.name,"READ")
     workspace = f.Get("w")
     #workspace.Print()
     f.Close()
     print "model b"
     model_b = workspace.pdf("model_b")
     print "model s"
     model   = workspace.pdf("model_s")
     components  = model.getComponents()
     print "postfit shape"
     pdf_shape_postfit  = components["shapeBkg_nonRes_JJ_"+purity+"_13TeV_"+str(period)]#shapeBkg_nonRes_JJ_HPHP_13TeV_2017
     print "data"
     data =  workspace.data("data_obs") #.reduce("CMS_channel==CMS_channel::JJ_"+purity+"_13TeV_"+str(period))
     norm = data.sumEntries()
     print "data normalisation "+str(norm)
     signal = workspace.pdf("shapeSig_"+sig+"_JJ_"+purity+"_13TeV_"+str(period))#shapeSig_BulkGWW_JJ_HPHP_13TeV_2017
     category = workspace.obj("CMS_channel")
     
     print "category "
     print category
    
     ## get variables from workspace 
     MJ1= workspace.var("MJ1");
     MJ2= workspace.var("MJ2");
     MJJ= workspace.var("MJJ");
     
     ### set a fit Range ########################
     #MJJ.setRange("R1",1856,5000) 
     #############################################
     args_all = ROOT.RooArgSet(category,MJ1,MJ2,MJJ)
     args_ws = ROOT.RooArgSet(MJ1,MJ2,MJJ)
  
     arglist = ROOT.RooArgList(args_ws)

     MX = workspace.var("MH")
     MX.setVal(mass)
     o_norm_sig = workspace.obj("n_exp_final_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_"+sig) #n_exp_binJJ_HPHP_13TeV_"+str(period)+"_proc_BulkGWW
     r = workspace.var("r")
     r.setMax(800)
     
     norm_sig = o_norm_sig.getVal() # norm_sig already contains a luminosity for the 2016 full dataset (norm_sig = yield*lumi) -> to scale to higher lumis use this
     print "signal normalistion "+str( norm_sig)
     
            
     
     #################################################
     
     ############################# extract TH3 histos to generate toys from #############
     
     forToys = ROOT.TFile(options.kernel,"READ")
     bkg_histo =  bkg_histo = forToys.Get(options.qcdBkgHisto )
     #forToys.Get("histo") # pythia kernels 
     #bkg_histo = forToys.Get("histo_altshape2") # for herwig kernels
     #bkg_histo = forToys.Get("histo_NLO") # for nlo MC
     #bkg_histo = forToys.Get("histo_altshapeUp")
     #bkg_histo = forToys.Get("nonRes")
     forBkgNormalisation = ROOT.TFile(options.norm,"READ")
     #nEvents = forBkgNormalisation.Get("nonRes").Integral()*lumi
     nEvents = forBkgNormalisation.Get("data_obs").Integral()
     print "number of events to be generated for the background "+str(nEvents)
     binsxy = getListOfBinsLowEdge(bkg_histo,"x")
     binsz  = getListOfBinsLowEdge(bkg_histo,"z")
     xBins  = getListOfBins(bkg_histo,"x")
     zBins  = getListOfBins(bkg_histo,"z")
     xBins_redux = reduceBinsToRange(xBins,getListFromRange(options.xrange))
     zBins_redux = reduceBinsToRange(zBins,getListFromRange(options.zrange))
     xBinsWidth   = getListOfBinsWidth(bkg_histo,"x")
     zBinsWidth   = getListOfBinsWidth(bkg_histo,"z")
     Bins_redux =[xBins_redux,xBins_redux,zBins_redux]
     binWidths=[xBinsWidth,xBinsWidth,zBinsWidth]
     ############################### get V+jets background component from MC ###############
     #print "start Vjets part "
     ##forTTbarjets = ROOT.TFile("/usr/users/dschaefer/CMSSW_7_4_7/src/CMGTools/VVResonances/interactive/JJ_ttbar_"+purity+".root","READ")
     #forWjets = ROOT.TFile("/afs/cern.ch/user/d/dschafer/forBiasTests/"+str(period)+"/JJ_WJets_"+purity+".root","READ") #JJ_WJets_HPLP.py
     #Wjets_histo = forWjets.Get("WJets")
     #Wjets_histo.Scale(lumi)
     
     #forZjets = ROOT.TFile("/afs/cern.ch/user/d/dschafer/forBiasTests/"+str(period)+"/JJ_ZJets_"+purity+".root","READ") #JJ_WJets_HPLP.py
     #Zjets_histo = forZjets.Get("ZJets")
     #Zjets_histo.Scale(lumi)
     #print Vjets_histo
     
    
     ######################### get V+jets background component from pdf ###################
     pdf_wjets_shape_postfit  = components["shapeBkg_Wjets_JJ_"+purity+"_13TeV_"+str(period)]
     pdf_zjets_shape_postfit  = components["shapeBkg_Zjets_JJ_"+purity+"_13TeV_"+str(period)]
     
     
     print "Prefit nonRes pdf:"
     pdf_nonres_shape_prefit = components["nonResNominal_JJ_"+purity+"_13TeV_"+str(period)]
     Wjets_norm = (components["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_Wjets"].getVal()
     Zjets_norm = (components["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_Zjets"].getVal()
     
     
     resbkg = [pdf_wjets_shape_postfit,pdf_zjets_shape_postfit]
     resbkg_norm = [Wjets_norm,Zjets_norm]
     #print
     
     ############################# get necessary value for the signal strenght ##########
     
     forSig = ROOT.TFile(options.signalStrength,"READ")
     exp_r = forSig.Get(str(int(mass))).Eval(float(options.expSig))
     print "expected signal strenght for "+str(options.expSig)+" sigma significance "+str(exp_r)
     logfile = open(options.output+"testBias_"+options.label+"_M"+str(int(mass))+".log","w")
     logfile.write("begin making signal + background toys with %f sigma signals and a signal mass of %i \n"%(float(options.expSig),int(mass)))
     logfile.write("nEvents_sig = "+str(round(norm_sig*exp_r,0))+"\n")
     logfile.write("effective injected r_in = "+str(round(norm_sig*exp_r,0)/norm_sig)+"\n")
     logfile.write("events injected = "+str(round(norm_sig*exp_r,0))+"\n")
     logfile.close()
     
     
     
     ############# start toy generation ######################
     print options.toys
     if int(options.toys) == -1:
        print "fit nominal shapes "
        print "bkg integral "+str(bkg_histo.Integral())
        #data = getNominalData(bkg_histo,nEvents,resbkg,resbkg_norm,binsxy,binsz,args_ws,signal,norm_sig*exp_r,category)
        print ROOT.RooFit.Index(category)
        print Vjets_histo
        print arglist
        hout = ROOT.TH3F('data','data',len(binsxy)-1,binsxy,len(binsxy)-1,binsxy,len(binsz)-1,binsz)
        hout.FillRandom(bkg_histo,int(nEvents))
        hout.Add(Vjets_histo) 
        
        data = ROOT.RooDataHist("data_test","data_test",arglist,ROOT.RooFit.Index(category),ROOT.RooFit.Import(category.getLabel(),hout)) 
        print data
        model_comp  = model.getComponents()
        r.setVal(0.0)
        #fitresult = model.fitTo(data,ROOT.RooFit.SumW2Error(True),ROOT.RooFit.Minos(0),ROOT.RooFit.Save(1) ,ROOT.RooFit.NumCPU(8))
        #logFitResult(fitresult,-1,options.output+"testBias_"+options.label+"_M"+str(int(mass))+".log")
        norm = (model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_nonRes"].getVal()
        normw = (model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_Wjets"].getVal() 
        normz = (model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_Zjets"].getVal() 
        norms = (model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_"+sig].getVal()
        
        #norm = 8276
        #normv =800
        
        #doZprojection([pdf_nonres_shape_prefit,model_b,pdf_wjets_shape_postfit,pdf_zjets_shape_postfit,model],data_toy,norm,normw,normz,norms,binsz,Bins_redux,binWidths,workspace,options)
        #doXprojection([pdf_nonres_shape_prefit,model_b,pdf_wjets_shape_postfit,pdf_zjets_shape_postfit,model],data_toy,norm,normw,normz,norms,binsxy,Bins_redux,binWidths,workspace,options)
        #doYprojection([pdf_nonres_shape_prefit,model_b,pdf_wjets_shape_postfit,pdf_zjets_shape_postfit,model],data_toy,norm,normw,normz,norms,binsxy,Bins_redux,binWidths,workspace,options)
        
       
        
     else:    
        for t in range(0,int(options.toys)):
            print "generating toy "+str(t)
            data_toy = generateToy(bkg_histo,nEvents,resbkg,resbkg_norm,binsxy,binsz,args_ws,signal,norm_sig*exp_r,category)
            print "done generating toy number "+str(t)
            fitresult = model.fitTo(data_toy,ROOT.RooFit.SumW2Error(True),ROOT.RooFit.Minos(0),ROOT.RooFit.Verbose(0),ROOT.RooFit.Save(1) ,ROOT.RooFit.NumCPU(8))
            print "done fitting "
            #fitresult = model.fitTo(data_toy,ROOT.RooFit.Verbose(1),ROOT.RooFit.Save(1))
            
            model_comp  = model.getComponents()
            
            print "model component s" 
            
            norm = (model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_nonRes"].getVal()
            normw = (model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_Wjets"].getVal() 
            normz = (model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_Zjets"].getVal()            
            norms = (model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_final_binJJ_"+purity+"_13TeV_"+str(period)+"_proc_"+sig].getVal()
           
            
            #print "n_exp  "+ str((model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["n_exp_binJJ_HPLP_13TeV_2016_proc_ZprimeWW"].getVal())
            
            #print "shapeSig norm "+ str((model_comp["pdf_binJJ_"+purity+"_13TeV_"+str(period)+"_nuis"].getComponents())["shapeSig_ZprimeWW_JJ_HPLP_13TeV_2016__norm"].getVal())
            
            #print "n_exp "+str(norms)
            
            #print "r  "+str(r.getVal())
            
            
            
            print "norm from fit "+str(norm)+ " + "+str(normw)+" + "+str(normz)+" + "+str(norms)
            
            
            #logfile.write("events fitted = "+str(round(norms*r.getVal(),0))+"\n")
            logFitResult(fitresult,t,options.output+"testBias_"+options.label+"_M"+str(int(mass))+".log",norms)
            print "log fit results "
            #workspace.Print()
            ############### norm from fit ##########################
            
            
            #doZprojection([pdf_nonres_shape_prefit,model_b,pdf_wjets_shape_postfit,pdf_zjets_shape_postfit,model,signal],data_toy,norm,normw,normz,norms,binsz,Bins_redux,binWidths,workspace,options)
            #doXprojection([pdf_nonres_shape_prefit,model_b,pdf_wjets_shape_postfit,pdf_zjets_shape_postfit,model,signal],data_toy,norm,normw,normz,norms,binsxy,Bins_redux,binWidths,workspace,options)
            #doYprojection([pdf_nonres_shape_prefit,model_b,pdf_wjets_shape_postfit,pdf_zjets_shape_postfit,model,signal],data_toy,norm,normw,normz,norms,binsxy,Bins_redux,binWidths,workspace,options)
            
            
            print " output logged in "+options.output+"testBias_"+options.label+"_M"+str(int(mass))+".log"
            #doZprojection([pdf_nonres_shape_prefit,model_b,model],data_toy,norm,0,norms,binsz,Bins_redux,binWidths,workspace,options)
            #doXprojection([pdf_nonres_shape_prefit,model_b,model],data_toy,norm,0,norms,binsxy,Bins_redux,binWidths,workspace,options)
            #doYprojection([pdf_nonres_shape_prefit,model_b,model],data_toy,norm,0,norms,binsxy,Bins_redux,binWidths,workspace,options)
            
            
         
     
