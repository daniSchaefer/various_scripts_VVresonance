import sys
import os
path = os.environ['ROOT_INCLUDE_PATH']
#print path
#find origin of lhapdf package for given CMSWW version by looking into the ROOT_INCLUDE_PATH and then for lhapdf. then locate the python library!
#sys.path.append("/cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/lhapdf/6.1.6-giojec/lib/python2.7/site-packages/")
#lhepdf version 6.2 from CMSSW_9_4_0
sys.path.append("/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.2.1-fmblme/lib/python2.7/site-packages/")
import ROOT
import lhapdf


print lhapdf.version()


### Getting a PDF member object
#p = lhapdf.mkPDF("CT10", 0)
#p = lhapdf.mkPDF("CT10/0")
### Gluon PDF querying at x=0.001, Q2=10000
#print p.xfxQ2(21, 1e-3, 1e4)


def initializePDFset(pdfset,NUMBER):
    pdfobj = lhapdf.mkPDF(pdfset,NUMBER)
    return pdfobj

def calculatePDFweight(PDFx,PDFweight,PDFqScale,PDFid,pdfobj,pdfnominal):
    weight =[] 
    if len(PDFx) !=2:
        print "pdfx vector is emtpy or too large!"
        return weight
    x1 = PDFx[0]
    x2 = PDFx[1]
    Q  = PDFqScale
    id_x1 = PDFid[0]
    id_x2 = PDFid[1]
    # initialze current pdf weights:
    
    w_x1  =   PDFweight[0]
    w_x2  =   PDFweight[1]
    #if w_x1 ==0 or w_x2==0 :
    w_x1 = pdfnominal.xfxQ(id_x1,x1, Q)
    w_x2 = pdfnominal.xfxQ(id_x2,x2, Q)
        #print "pdf weights are 0"
        #pdfobj = lhapdf.mkPDF(pdfset,0)
        #w_x1 = pdfobj.xfxQ(id_x1,x1,Q)
        #w_x2 = pdfobj.xfxQ(id_x2,x2,Q)

    w_x1new = 1
    w_x2new = 1

   # print " flavour 1 : " + str( id_x1 )+ " flavour 2 : "+str( id_x2 )

    #for  n in range(0,NUMBER):
    w_x1new = pdfobj.xfxQ(id_x1,x1, Q)
    w_x2new = pdfobj.xfxQ(id_x2,x2, Q)
    weight.append( w_x1new*w_x2new/(w_x1*w_x2))
    weight.append(w_x1new*w_x2new)
    weight.append(w_x1*w_x2)
    return weight   


def selectJets(puppi_pt,puppi_eta,puppi_tightID,puppi_N):
    if puppi_N < 2:
        return [0]
    if puppi_tightID[0]==0:
        return [0]
    jets = []
    for i in range(0,puppi_N):
        if puppi_pt[i] <= 200: continue
        if abs(puppi_eta[i]) >= 2.5: continue
        if puppi_tightID[i] == 0: continue
        jets.append(i)
    if len(jets)<2:
        return [0]
    if abs(puppi_eta[jets[0]]-puppi_eta[jets[1]]) > 1.3: 
        return [0]
    return [jets[0],jets[1]]


def makeLV(pt,eta,phi,e,j1,j2):
    W1 = ROOT.TLorentzVector()
    W1.SetPtEtaPhiE(pt[j1],eta[j1],phi[j1],e[j1])
    W2 = ROOT.TLorentzVector()
    W2.SetPtEtaPhiE(pt[j2],eta[j2],phi[j2],e[j2])
    return [W1+W2,W1,W2]

def massCut(X,sdmass1,sdmass2):
    if X.M() < 1000:
        return 0
    if sdmass1 > 215:
        return 0
    if sdmass1 < 55:
        return 0
    if sdmass2 > 215:
        return 0
    if sdmass2 < 55:
        return 0
    return 1



def ApplyPuppiSoftdropMassCorrections(puppiJet,m_puppisd_corr,sdmass):
 genCorr = m_puppisd_corr[0].Eval(puppiJet.Pt());
 recoCorr = 1;
 if abs(puppiJet.Eta()) <= 1.3: recoCorr = m_puppisd_corr[1].Eval(puppiJet.Pt())
 else: recoCorr = m_puppisd_corr[2].Eval(puppiJet.Pt())
 return sdmass*genCorr*recoCorr


def tau21Cuts(tau21_jet1,tau21_jet2,mass1,mass2,pt1,pt2,cat):
    if cat.find("HPHP")!=-1:
        if (tau21_jet1 +(0.082*ROOT.TMath.Log(mass1*mass1/pt1))) < 0.57 and (tau21_jet2 +(0.082*ROOT.TMath.Log(mass2*mass2/pt2))) < 0.57:
            return 1
    if cat.find("HPLP")!=-1:
        if (tau21_jet1 +(0.082*ROOT.TMath.Log(mass1*mass1/pt1))) > 0.98 or (tau21_jet2 +(0.082*ROOT.TMath.Log(mass2*mass2/pt2))) > 0.98:
            return 0
        if (tau21_jet1 +(0.082*ROOT.TMath.Log(mass1*mass1/pt1))) >= 0.57 and (tau21_jet2 +(0.082*ROOT.TMath.Log(mass2*mass2/pt2))) < 0.57:
            return 1
        if (tau21_jet1 +(0.082*ROOT.TMath.Log(mass1*mass1/pt1))) < 0.57 and (tau21_jet2 +(0.082*ROOT.TMath.Log(mass2*mass2/pt2))) >= 0.57:
            return 1
    return 0

if __name__=="__main__":
    tree = ROOT.TChain("ntuplizer/tree")
    for f in sys.argv[1].split(","):
        #rootfile = ROOT.TFile(sys.argv[1],"READ")
        tree.Add(f)
    print "running over file "+sys.argv[1]
    
    sd_mass_weights_file = ROOT.TFile("puppiCorr.root","READ")
    w0 = sd_mass_weights_file.Get("puppiJECcorr_gen")
    w1 = sd_mass_weights_file.Get("puppiJECcorr_reco_0eta1v3")
    w2 = sd_mass_weights_file.Get("puppiJECcorr_reco_1v3eta2v5")
    sd_mass_weights = [w0,w1,w2]
    
    #tree = rootfile.Get("ntuplizer/tree")
    N = 101#initializePDFset("NNPDF31_lo_as_0130")
    
    unweightedEvents=0
    
    HPHP_hsdmass=[]
    HPHP_hdijetmass=[]
    
    HPLP_hsdmass=[]    
    HPLP_hdijetmass=[]

    
    eventsAll = []
    eventsPassed = []
    eventsPassed_HPHP = []
    eventsPassed_HPLP = []
    for n in range(0,N):
        eventsAll.append(0)
        eventsPassed.append(0)
        eventsPassed_HPHP.append(0)
        eventsPassed_HPLP.append(0)
        tmp = ROOT.TH1F("HPHP_hsdmass_"+str(n),"HPHP_hsdmass_"+str(n),80,55,215)
        HPHP_hsdmass.append(tmp)
        
        tmp = ROOT.TH1F("HPHP_hdijetmass_"+str(n),"HPHP_hdijetdmass_"+str(n),511,500,6500)
        HPHP_hdijetmass.append(tmp)
        
        
        tmp = ROOT.TH1F("HPLP_hsdmass_"+str(n),"HPLP_hsdmass_"+str(n),80,55,215)
        HPLP_hsdmass.append(tmp)
        
        tmp = ROOT.TH1F("HPLP_hdijetmass_"+str(n),"HPLP_hdijetdmass_"+str(n),511,500,6500)
        HPLP_hdijetmass.append(tmp)
        
        pdfsetname = "NNPDF31_nnlo_hessian_pdfas"
        if  sys.argv[2].find("91200")!=-1:
            pdfsetname="PDF4LHC15_nnlo_100_pdfas"
        if  sys.argv[2].find("315000")!=-1: 
            pdfsetname="NNPDF31_lo_as_0118"
        if  sys.argv[2].find("315200")!=-1:    
            pdfsetname="NNPDF31_lo_as_0130"
            
    pdfnominal = initializePDFset("NNPDF31_nnlo_hessian_pdfas",0)
    for n in range(0,N):
        pdf = initializePDFset(pdfsetname,n) #NNPDF31_nnlo_hessian_pdfas #PDF4LHC15_nnlo_100_pdfas
        #for t in tree:
        for event in tree:
            w = calculatePDFweight(event.PDF_x,event.PDF_xPDF,event.qScale,event.PDF_id,pdf,pdfnominal)
#            if event.genWeight < 0 and w[2] > 0:
 #                   print "genweight smaller 0! while pdfweight is not! skip this event"
  #                  continue
            if n==0:
               unweightedEvents+=1
                #print "event " +str(unweightedEvents)
            #if event.PDF_xPDF[0] ==0:print "event has 0 pdf weight"; continue
            
            
            
            #print w
            #if event.genWeight <0:
                #print "event "+str(unweightedEvents)
                #print w[0]
                #print w[0]*event.genWeight
            #print w
            finalweight = abs(w[0]*event.genWeight)
            eventsAll[n] += finalweight #event.puweight*
            
            #if w[0]*event.genWeight <0:
                #print "attention negative weight!"
                #if w[0]<0:
                    #print "pdf weight smaller 0!"
                    #if w[1] <0:
                        #print "new pdfweight is smaller 0!"
                    #if w[2]<0:
                        #print "old pdfweight is smaller 0!"
                    
            
            #selections for 2017 variables (default jet collection is puppi jets):
            jets = selectJets(event.jetAK8_pt,event.jetAK8_eta,event.jetAK8_IDTight,event.jetAK8_N)
            if len(jets) < 2:
                #print len(jets)
                continue
            [X,W1,W2] = makeLV(event.jetAK8_pt,event.jetAK8_eta,event.jetAK8_phi,event.jetAK8_e,jets[0],jets[1])
            sdmassCorr1 = ApplyPuppiSoftdropMassCorrections(W1,sd_mass_weights,event.jetAK8_softdrop_mass[jets[0]])
            sdmassCorr2 = ApplyPuppiSoftdropMassCorrections(W2,sd_mass_weights,event.jetAK8_softdrop_mass[jets[1]])
            if massCut(X,sdmassCorr1,sdmassCorr2)==1:
                eventsPassed[n]+= finalweight
            if event.jetAK8_tau1[jets[0]] == 0:
                print "tau1 jet1 is 0!"
                continue
            if event.jetAK8_tau1[jets[1]] == 0:
                print "tau1 jet2 is 0!"
                continue
            if  tau21Cuts(event.jetAK8_tau2[jets[0]]/event.jetAK8_tau1[jets[0]],event.jetAK8_tau2[jets[1]]/event.jetAK8_tau1[jets[1]],sdmassCorr1,sdmassCorr2,W1.Pt(),W2.Pt(),"HPHP")==1:
                if massCut(X,sdmassCorr1,sdmassCorr2)==1:
                    eventsPassed_HPHP[n]  += finalweight
                HPHP_hsdmass[n].Fill(sdmassCorr1,finalweight)
                HPHP_hsdmass[n].Fill(sdmassCorr2,finalweight)
                HPHP_hdijetmass[n].Fill(X.M(),finalweight)
                
                
            if  tau21Cuts(event.jetAK8_tau2[jets[0]]/event.jetAK8_tau1[jets[0]],event.jetAK8_tau2[jets[1]]/event.jetAK8_tau1[jets[1]],sdmassCorr1,sdmassCorr2,W1.Pt(),W2.Pt(),"HPLP")==1:
                if massCut(X,sdmassCorr1,sdmassCorr2)==1:
                    eventsPassed_HPLP[n]  += finalweight
                HPLP_hsdmass[n].Fill(sdmassCorr1,finalweight)
                HPLP_hsdmass[n].Fill(sdmassCorr2,finalweight)
                HPLP_hdijetmass[n].Fill(X.M(),finalweight)
                
    print eventsAll
    
    acceptance=[]
    print "acceptance "
    for i in range(0,len(eventsAll)):
        acceptance.append( eventsPassed[i]/float(eventsAll[i]))
        print acceptance[i]
    print "maximum acceptance "+str(max(acceptance))
    
    
    
    eff_HPHP=[]
    print "eff_HPHP "
    for i in range(0,len(eventsAll)):
        eff_HPHP.append( eventsPassed_HPHP[i]/float(eventsAll[i]))
        print eff_HPHP[i]
    print "maximum eff_HPHP "+str(max(eff_HPHP))
    
    
    eff_HPLP=[]
    print "eff_HPLP "
    for i in range(0,len(eventsAll)):
        eff_HPLP.append( eventsPassed_HPLP[i]/float(eventsAll[i]))
        print eff_HPLP[i]
    print "maximum eff_HPLP "+str(max(eff_HPLP))
    
    
    #for i in range(0,len(eventsAll)):
        #acceptance[i]=acceptance[i]/float(acceptance[0]) -1
        #eff_HPHP[i]=eff_HPHP[i]/float(eff_HPHP[0])       -1
        #eff_HPLP[i]=eff_HPLP[i]/float(eff_HPLP[0])       -1
    #print "maximum acceptance difference % *100 "+str(max(acceptance)*100)
    #print "maximum eff HPHP difference % *100 "+str(max(eff_HPHP)*100)
    #print "maximum eff HPLP difference % *100 "+str(max(eff_HPLP)*100)
    
    logfile = open(sys.argv[2],"w")
    logfile.write("prossesed root file : "+str(sys.argv[1])+"\n")
    logfile.write("processed events: "+str(unweightedEvents)+"\n")
    logfile.write("all events weighted :  all passed events : passed events HPHP : passed events HPLP \n")
    for i in range(0,len(eventsAll)):
        logfile.write(str(eventsAll[i] ) +"  :  "+ str(eventsPassed[i]) +"  :  "+ str(eventsPassed_HPHP[i]) +"  :  "+str(eventsPassed_HPLP[i])+"\n") 
    logfile.close()
    
    
    output_rootfile = ROOT.TFile.Open(sys.argv[2].replace(".txt",".root"),"RECREATE")
    for n in range(0,N):
        HPHP_hsdmass    [n].Write()
        HPHP_hdijetmass [n].Write()
        HPLP_hsdmass    [n].Write()
        HPLP_hdijetmass [n].Write()
    
    output_rootfile.Close()
    
    
   #   lumiBlock;
   #   eventNumber;
   #   runNumber;
   #   PV_filter;
   #   passFilter_CSCHalo;
   #   passFilter_HBHELoose;
   #   passFilter_HBHEIso;
   #   passFilter_EEBadSc; // not used
   #   passFilter_chargedHadronTrackResolution;
   #   passFilter_muonBadTrack;
   #   passFilter_ECALDeadCell;
   #

# for leptons :
#if(! FoundNoLeptonOverlap(goodElectrons,goodMuons,myjet.tlv()) ) continue;
    
