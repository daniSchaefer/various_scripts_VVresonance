import ROOT
import sys
import os
import optparse
import numpy



parser = optparse.OptionParser()
parser.add_option("-s","--signal",dest="signal",default='',help="Type of signal sample")
parser.add_option("-m","--masspoints",dest="masspoints",default='2000',help="which masspoints to use")
parser.add_option("-p","--pdfset",dest="pdfset",default="unknown",help="document pdfset used for the reweighting")

(options,args) = parser.parse_args()

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

def getMasspoints(points):
    l = points.split(",")
    res =[]
    for m in l:
        res.append(int(m))
    return res



def reader(f):
    lines = [line.rstrip('\n') for line in f]
    nall =[]
    nacc =[]
    nHPHP=[]
    nHPLP=[]
    for l in lines:
        if l.find("a")!=-1 or l.find("p")!=-1:
            continue
        n = l.split(" : ")
        nall.append(float(n[0]))
        nacc.append(float(n[1]))
        nHPHP.append(float(n[2]))
        nHPLP.append(float(n[3]))
    return [nall,nacc,nHPHP,nHPLP]


def writeResults(logfile,results,index):
    logfile.write("\\begin{tabular}{lccc} \n")
    logfile.write("mass         &    mean  acceptance   &   standard deviation   &   std % \\\\ \n")
    for m in sorted(results.keys()):
        nall = numpy.array(results[m][index])
        
        mean_all = nall.mean()
        std_all  = nall.std()
        
        logfile.write(str(m)+"   &    "+str(mean_all) + "  &  "+str(std_all)+ "  &  "+str(round((std_all/mean_all)*100,4)) +" \\\\ \n"  )
    logfile.write("\end{tabular}\n")
    return 0

def writeResultsAcc(logfile,results):
    logfile.write("\\begin{tabular}{lccc} \n")
    logfile.write("mass         &    mean  acceptance   &   standard deviation   &   std % \\\\ \n")
    for m in sorted(results.keys()):
        nall = numpy.array(results[m][0])
        nacc = numpy.array(results[m][1])
        
        acc = numpy.array([])
        for n in range(0,len(nacc)):
            acc = numpy.append(acc,nacc[n]/nall[n])
        mean_all = acc.mean()
        std_all  = acc.std()
        delta_acc = numpy.array([])
        for n in range(1,len(acc)):
            delta_acc = numpy.append(delta_acc,acc[0]-acc[n])
        std_delta_acc = delta_acc.std()
        mean_delta_acc = delta_acc.mean()
        
        logfile.write(str(m)+"   &    "+str(round(mean_all,4)) + "  &  "+str(round(std_all,4))+ "  &  "+str(round((std_all/mean_all)*100,2)) +"\\\\  \n"  )
    logfile.write("\end{tabular} \n")
    return 0



def FitGaussian(htmp,mass):
    gauss  = ROOT.TF1("gauss" ,"gaus",0.6*mass,2*mass)  
    if mass < 100:
        gauss =  ROOT.TF1("gauss" ,"gaus",75,115)
    htmp.Fit(gauss,"R")
      
    mean2 = gauss.GetParameter(1)
    sigma = gauss.GetParameter(2)
    
    mean2 = htmp.GetMean()
    
    print "mean : "+str(mean2)
    print "sigma : "+str(sigma)
    
    #print str(mean)+"   "+str(mean2)
    
    gauss_refined  = ROOT.TF1("gauss" ,"gaus",mean2-0.8*sigma,mean2+1.2*sigma)  
    gauss_refined.SetParameter(1,mean2)
    gauss_refined.SetParLimits(2,sigma*0.5,htmp.GetRMS())
    gauss_refined.SetParameter(2,sigma)
    if mass > 100:
        gauss_refined.SetParLimits(1,1000,5500)
        if mass <= 1100:
            gauss_refined  = ROOT.TF1("gauss" ,"gaus",900,1100)  
            gauss_refined.SetParameter(1,1000)
            gauss_refined.SetParLimits(1,900,1100)
            gauss_refined.SetParLimits(2,0,100)
            gauss_refined.SetParameter(2,80)
        if mass <= 1300 and mass >1100:
            gauss_refined  = ROOT.TF1("gauss" ,"gaus",1000,1300)  
            gauss_refined.SetParameter(1,1200)
            gauss_refined.SetParLimits(1,1000,1300)
            gauss_refined.SetParLimits(2,0,200)
            gauss_refined.SetParameter(2,100)
        if mass <= 4100 and mass >3000:
            gauss_refined  = ROOT.TF1("gauss" ,"gaus",3650,4500)   
            gauss_refined.SetParLimits(1,3500,4500)
            gauss_refined.SetParLimits(2,0,800)
            gauss_refined.SetParameter(1,4000)
            gauss_refined.SetParameter(2,400)
        if mass < 4000 and mass >=3000:
            gauss_refined  = ROOT.TF1("gauss" ,"gaus",2700,3300)  
        if mass < 5500 and mass >=5000:
            gauss_refined  = ROOT.TF1("gauss" ,"gaus",4650,5500)  
        if mass < 6000 and mass >=5500:
            gauss_refined  = ROOT.TF1("gauss" ,"gaus",5200,mass+1.2*sigma)  
        if mass >= 6000:
            gauss_refined  = ROOT.TF1("gauss" ,"gaus",5700,6500)  
            gauss_refined.SetParLimits(1,1000,6500)
            gauss_refined.SetParameter(1,6000)
            gauss_refined.SetParLimits(2,0,1000)
            gauss_refined.SetParameter(2,400)

    htmp.Fit(gauss_refined,"R")
    
    mean = gauss_refined.GetParameter(1)
    sigma = gauss_refined.GetParameter(2)
    
    c = ROOT.TCanvas("c","c",400,400)
    htmp.Draw("hist")
    gauss_refined.Draw("same")
    c.SaveAs(htmp.GetName()+".pdf")
    fitstate = ROOT.gMinuit.fCstatu
    if fitstate.find("CONVERGED")!=-1:
        return [mean,sigma]
    else:
        return [-1,-1]



def CleanFailedFits(values):
    res=[[],[]]
    for m in range(0,len(values)):
        if values[1][m]< 0:
            print " fit failed"
            continue
        res[0].append(values[0][m])
        res[1].append(values[1][m])
    return res

def RebinHisto(htmp,mass):
    massmax = min(6500,1.25*mass)
    massmin = mass*0.75
    first = True
    minb=0
    bins=0
    w = htmp.GetBinWidth(1)
    for n in range(0,htmp.GetNbinsX()+1):
        c = htmp.GetBinCenter(n)
        w = htmp.GetBinWidth(n)
        if c-w/2. > massmin:
            if first == True:
                minb = c-w/2.
            first =False
            bins+=1
            
    massmin = minb 
    massmax = minb+(bins+1)*w
    #if bins%6 ==0:
    #    bins = bins/2
    #if bins%5 ==0:
    #    bins = bins/2
    #if bins%4 ==0:
    #    bins = bins/2    
    #if bins%3 ==0:
    #    bins = bins/3
    bins=bins/2
        
    new = ROOT.TH1F(htmp.GetName(),htmp.GetName(),bins,massmin,massmax)
    for n in range(0,htmp.GetNbinsX()+1):
        new.Fill(htmp.GetBinCenter(n),htmp.GetBinContent(n))
    new.Scale(1/new.Integral())
    return new

def makePlots(histos,results,label,mass):
    htmp=histos[0]
    htmp_Up = histos[1]
    htmp_Down = histos[2]
    
    res = results[0]
    resUp = results[1]
    resDown = results[2]
    c2 = ROOT.TCanvas("c","c",800,600)
    c2.cd()
    legend = ROOT.TLegend(0.12,0.7,0.3,0.8)
    
    
    
    x=60
    y=0.14
    func1 = htmp.GetFunction("gauss")
    func2 = htmp_Up.GetFunction("gauss")
    func3 = htmp_Down.GetFunction("gauss")
    htmp.SetMaximum(0.15)
    if label.find("mjj")!=-1:
        #htmp = RebinHisto(htmp,mass)
        #htmp_Up   = RebinHisto(htmp_Up,mass)
        #htmp_Down = RebinHisto(htmp_Down,mass)
        
        x=0.75*mass  +50
        htmp.SetMaximum(0.25)
        y=0.036
        
    htmp.SetLineColor(ROOT.kBlack)    
    htmp.SetTitle("PDF variations for mjj = "+str(mass))    
    
    
    htmp.Draw("hist")
    func1.SetLineColor(ROOT.kBlack)
    func1.Draw("same")
    #JERhtmp.Draw("func")
    htmp_Up.SetLineColor(ROOT.kBlue)
    htmp_Up.Draw("histsame")
    htmp_Down.SetLineColor(ROOT.kRed)
    htmp_Down.Draw("histsame")
    

    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("same")
    
    func3.SetLineColor(ROOT.kRed)
    func3.Draw("same")
    
    legend.SetBorderSize(0)
    legend.AddEntry(htmp_Down,"PDF down","l")
    legend.AddEntry(htmp,"nominal" ,"l")
    legend.AddEntry(htmp_Up, "PDF up","l")
    legend.Draw("same")
    text = ROOT.TLatex()
    text.DrawLatex(x,y,"#scale[0.6]{#color[2]{#mu ="+str(round(resDown[0],2))+" #sigma = "+str(round(resDown[1],2))+" }  #mu ="+str(round(res[0],2))+" #sigma = "+str(round(res[1],2))+"   #color[4]{#mu ="+str(round(resUp[0],2))+" #sigma = "+str(round(resUp[1],2))+" }}" )
    c2.SaveAs(label+".pdf")


def getHistos(filename,purity):
    f = ROOT.TFile.Open(filename,"READ")
    #print filename.split("_M")[1].split("_PDF")[0]
    mass = float(filename.split("_M")[1].split("_PDF")[0])
    means_mjj =[]
    sigma_mjj =[]
    means_mjet=[]
    sigma_mjet=[]
    htmp_mjet =[]
    htmp_mjj =[]
    forplot_mjet=[]
    forplot_mjj=[]
    
    for i in range(0,101):
        tmp = f.Get(purity+"_hsdmass_"+str(i))
        tmp2 = f.Get(purity+"_hdijetmass_"+str(i))
        tmp2 = RebinHisto(tmp2,mass)
        tmp.Sumw2()
        tmp2.Sumw2()
        
        
        tmp.Scale(1/tmp.Integral())
        tmp2.Scale(1/tmp2.Integral())
    
        
        res = FitGaussian(tmp,90)
        res2 =FitGaussian(tmp2,mass)
        
        print res
        
        if i==0:
            htmp_mjet.append(tmp)
            htmp_mjj.append(tmp2)
            forplot_mjet.append(res)
            forplot_mjj.append(res2)
            
        if i ==50 :
            htmp_mjet.append(tmp)
            htmp_mjj.append(tmp2)
            forplot_mjet.append(res)
            forplot_mjj.append(res2)
        if i==100:
            htmp_mjet.append(tmp)
            htmp_mjj.append(tmp2)
            forplot_mjet.append(res)
            forplot_mjj.append(res2)
        
        means_mjj.append(res2[0])
        sigma_mjj.append(res2[1])
        means_mjet.append(res[0])
        sigma_mjet.append(res[1])
     
    print "make plots : "
    makePlots(htmp_mjet,forplot_mjet,filename.replace(".root","")+"_mjet_"+purity,mass)
    makePlots(htmp_mjj,forplot_mjj,filename.replace(".root","")+"_mjj_"+purity,mass)
    
    f.Close() 
    #print means_mjj
    return [means_mjj,sigma_mjj,means_mjet,sigma_mjet]


def calcErrors(mean,sigma):
    nm = numpy.array(mean)
    ns = numpy.array(sigma)
    
    res1 = nm.std()
    res2 = ns.std()
    print "calc errors"
    print res1
    print res2
    return [nm.mean(),res1,ns.mean(),res2]


def getShapeUnc(filename,purity):
    r = getHistos(filename,purity)
    print r
    r1 = CleanFailedFits([r[0],r[1]])
    r2 = CleanFailedFits([r[2],r[3]])
    res_mjj= calcErrors(r1[0],r1[1])
    res_mjet=calcErrors(r2[0],r2[1])
    #res_mjj = calcErrors(mjj[0],mjj[1])
    #res_mjet= calcErrors(mjet[0],mjet[1])
    print res_mjj
    print res_mjet
    return [res_mjj,res_mjet]
    
    

if __name__=="__main__":
    masspoints = getMasspoints(options.masspoints)
    results={}
    mjj_res_HPHP={}
    mjet_res_HPHP={}
    mjj_res_HPLP={}
    mjet_res_HPLP={}
    logfile = open("PDFUnc_"+options.signal+"_PDF"+options.pdfset+".txt","w")
    for mass in masspoints:
        print mass
        f = open("PDF"+options.signal+"_M"+str(mass)+"_PDF"+options.pdfset+".txt","r")
        tmp = reader(f)
        
        results[mass]=tmp
        f.close()
        tmp = getShapeUnc("PDF"+options.signal+"_M"+str(mass)+"_PDF"+options.pdfset+".root","HPHP")
        print tmp
        mjj_res_HPHP[mass]= tmp[0]
        mjet_res_HPHP[mass]=tmp[1]
        
        tmp = getShapeUnc("PDF"+options.signal+"_M"+str(mass)+"_PDF"+options.pdfset+".root","HPLP")
        mjj_res_HPLP[mass]= tmp[0]
        mjet_res_HPLP[mass]=tmp[1]
        
        #print tmp
        
        print mjj_res_HPHP
        print mjet_res_HPHP
    

    logfile.write( "\caption{Uncertainty on the signal shapes in the HPHP category due to PDF uncertainties for a ."+options.signal   +" model. The uncertainties are evaluated as differences in the mean $\mu$ and variance $\sigma$ of a gaussian function fitted to the core of the $m_{jj}$ distribution.} \n")
    logfile.write("\\begin{tabular}{l|ccc|ccc} \n")
    logfile.write( "dijet mass & mean $\mu$ & std $\mu$  & std $\mu$ (%) & mean $\sigma$ & std $\sigma$ & std $\sigma$ (%) \\\\ \n")
    for mass in sorted(masspoints):
        logfile.write( str(mass)+" & "+str(round(mjj_res_HPHP[mass][0],4))+" & "+str(round(mjj_res_HPHP[mass][1],4))+" & "+str(round(mjj_res_HPHP[mass][1]*100/mjj_res_HPHP[mass][0],4)) +" & ")
        logfile.write( str(round(mjj_res_HPHP[mass][2],4))+" & "+str(round(mjj_res_HPHP[mass][3],4))+" & "+str(round(mjj_res_HPHP[mass][3]*100/mjj_res_HPHP[mass][2],4)) +"\\\\ \n")

    logfile.write("\end{tabular} \n")


    logfile.write( "\caption{Uncertainty on the signal shapes in the HPHP category due to PDF uncertainties for a ."+options.signal   +" model. The uncertainties are evaluated as differences in the mean $\mu$ and variance $\sigma$ of a gaussian function fitted to the core of the $m_{jet}$ distribution. }\n")
    logfile.write("\\begin{tabular}{l|ccc|ccc} \n")
    logfile.write( "dijet mass & mean $\mu$ & std $\mu$  & std $\mu$ (%) & mean $\sigma$ & std $\sigma$ & std $\sigma$ (%) \\\\ \n")
    for mass in sorted(masspoints):
        logfile.write( str(mass)+" & "+str(round(mjet_res_HPHP[mass][0],4))+" & "+str(round(mjet_res_HPHP[mass][1],4))+" & "+str(round(mjet_res_HPHP[mass][1]*100/mjet_res_HPHP[mass][0],4))+" & ")
        logfile.write(str(round(mjet_res_HPHP[mass][2],4))+" & "+str(round(mjet_res_HPHP[mass][3],4))+" &  "+str(round(mjet_res_HPHP[mass][3]*100/mjet_res_HPHP[mass][2],4))  +"\\\\ \n")
      

    logfile.write("\end{tabular} \n")


    logfile.write( "\caption{Uncertainty on the signal shapes in the HPLP category due to PDF uncertainties for a ."+options.signal   +" model. The uncertainties are evaluated as differences in the mean $\mu$ and variance $\sigma$ of a gaussian function fitted to the core of the $m_{jj}$ distribution. }\n")
    logfile.write("\\begin{tabular}{l|ccc|ccc} \n")
    logfile.write( "dijet mass & mean $\mu$ & std $\mu$  & std $\mu$ (%) & mean $\sigma$ & std $\sigma$ & std $\sigma$ (%) \\\\ \n")
    for mass in sorted(masspoints):                                                         
        logfile.write( str(mass)+" & "+str(round(mjj_res_HPLP[mass][0],4))+" & "+str(round(mjj_res_HPLP[mass][1],4))+" & "+str(round(mjj_res_HPLP[mass][1]*100/mjj_res_HPLP[mass][0],4))+" & ")
        logfile.write( str(round(mjj_res_HPLP[mass][2],4))+" & "+str(round(mjj_res_HPLP[mass][3],4))+" & "+str(round(mjj_res_HPLP[mass][3]*100/mjj_res_HPLP[mass][2],4)) +"\\\\ \n")

    logfile.write("\end{tabular} \n")

    logfile.write( "\caption{Uncertainty on the signal shapes in the HPLP category due to PDF uncertainties for a ."+options.signal   +" model. The uncertainties are evaluated as differences in the mean $\mu$ and variance $\sigma$ of a gaussian function fitted to the core of the $m_{jet}$ distribution.} \n")
    logfile.write("\begin{tabular}{l|ccc|ccc} \n")
    logfile.write( "dijet mass & mean $\mu$ & std $\mu$  & std $\mu$ (%) & mean $\sigma$ & std $\sigma$ & std $\sigma$ (%) \\\\ \n")
    for mass in sorted(masspoints):
        logfile.write(str(mass)+ " & "+str(round(mjet_res_HPLP[mass][0],4))+" & "+str(round(mjet_res_HPLP[mass][1],4))+" & "+str(round(mjet_res_HPLP[mass][1]*100/mjet_res_HPLP[mass][0],4))+" & ")
        logfile.write( str(round(mjet_res_HPLP[mass][2],4))+" & "+str(round(mjet_res_HPLP[mass][3],4))+" & "+str(round(mjet_res_HPLP[mass][3]*100/mjet_res_HPLP[mass][2],4)) +" \\\\ \n")                                                                
    
    logfile.write("\end{tabular} \n")                                                                  
                                                                      
                                                                      
                                                                     
        
    #logfile = open("PDFUnc_"+options.signal+"_PDF"+options.pdfset+".txt","w")
    logfile.write("all events weighted with pdfset ")
    logfile.write(options.pdfset+"\n")
    writeResults(logfile,results,0)
    logfile.write("events after acceptance cuts weighted with pdfset ")
    logfile.write(options.pdfset+"\n")
    writeResults(logfile,results,1)
    logfile.write("HPHP category events weighted with pdfset ")
    logfile.write(options.pdfset+"\n")
    writeResults(logfile,results,2)
    logfile.write("HPLP category events weighted with pdfset ")
    logfile.write(options.pdfset+"\n")
    writeResults(logfile,results,3)
    
    
    logfile.write("\caption{PDF uncertainty on the acceptance for "+options.signal+".} \n")
    writeResultsAcc(logfile,results)
    

    
    
    
    logfile.close()    
