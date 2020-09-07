import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
import numpy
from array import array

#parser = optparse.OptionParser()
#parser.add_option("-m","--mass",dest="mass",help="mass of input ROOT File",default='')
#parser.add_option("-s","--expSig",dest="expSig",help="signal strenghts",default='')
#(options,args) = parser.parse_args()


def plotPulledParamters(variables,param,name):
    color=[ROOT.kBlack,ROOT.kRed,ROOT.kBlue,ROOT.kMagenta,ROOT.kGreen,ROOT.kPink,ROOT.kOrange,ROOT.kYellow]
    style=[10,2,4,5,6,7,8,10,22,20,22,34,34]
    graphs=[]
    vmax=-1
    vmin=10000000000000000
    for var in variables:
        c0=0
        g = ROOT.TGraphErrors()
        g.SetName(var)
        graphs.append(g)
        for m in sorted(param.keys()):
            v = param[m][var]
            if v > vmax:
                vmax =v
            if v < vmin: 
                vmin = v
            #print "mass "+str(m)+"  "+str(param[m][var])
            g.SetPoint(c0,float(m),v)
            c0+=1
    l = ROOT.TLegend(0.37,0.2,0.86,0.33)
    #l = ROOT.TLegend(0.55,0.86,0.9,0.7)
    l.SetTextFont(82)
    canv  = getCanvas()
    canv.SetGrid()
    c=0
    for g in graphs:
        g.GetXaxis().SetTitle("dijet invariant mass (GeV)")
        g.SetMaximum(vmax+0.1*vmax)
        svim = max(vmax,ROOT.TMath.Abs(vmin))
        g.SetMinimum(-1.5*svim)
    
        g.SetLineColor(color[c])
        g.SetMarkerColor(color[c])
        g.SetMarkerStyle(style[c])
        l.AddEntry(g,variables[c],"lp")
        if c==0:
            g.Draw("APL")
        else:
            g.Draw("LPsame")
        c+=1
    l.Draw("same")
    canv.SaveAs(name)


def getLimit(filename):
    f=ROOT.TFile(filename,"READ")
    limit=f.Get("limit")
    data=[]
    for event in limit:
        #if event.quantileExpected<0:
        if event.quantileExpected>0.4 and event.quantileExpected <0.55:
            data.append(event.limit)  #*0.01
    f.Close()
    return data


def readLog(logfile,variable):
    #print logfile
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

def beautify(graph,color,marker,title):
    graph.SetLineColor(color)
    graph.SetMarkerStyle(marker)
    graph.SetMarkerColor(color)
    graph.GetYaxis().SetTitle(title)
    graph.GetYaxis().SetTitleSize(0.05)
    graph.GetYaxis().SetTitleOffset(0.9)
    graph.GetXaxis().SetTitleSize(0.05)
    graph.GetXaxis().SetTitleOffset(0.9)
    graph.GetXaxis().SetLabelSize(0.05)
    graph.GetYaxis().SetLabelSize(0.05)
    graph.GetXaxis().SetNdivisions(10)
    graph.GetYaxis().SetNdivisions(6)
    return graph

def fitWithGaus(h):
    #mmin = h.GetXaxis().GetXmin()*(1-0.2)
    #mmax = h.GetXaxis().GetXmax()*(1-0.2)
    #print h.GetXaxis().GetXmax()
    mmax = h.GetXaxis().GetXmax()*0.4
    mmin = h.GetXaxis().GetXmax()*0.2 
    mmin = 6
    mmax = 14
    
    
    gauss  = ROOT.TF1("gauss" ,"gaus", mmin,mmax)  
    h.Fit(gauss)
    mean = gauss.GetParameter(1)
    #print mean
    sigma = gauss.GetParameter(2)
    e_mean = gauss.GetParError(1)
    e_sigma = gauss.GetParError(2)
    #print sigma
    return gauss



def getExpSig(expSig):
    if expSig!="":
        exp = expSig.split(",")
        s=[]
        for e in exp:
            s.append(float(e))
        return s
    return 0

def getCanvas(w=800,h=600):
    c1 = ROOT.TCanvas("c","",w,h)
    c1.SetBottomMargin(0.15)
    c1.SetTopMargin(0.15)
    return c1

def getDiff(r,s):
    diff =[]
    for sig in r:
        diff.append(sig-s)
    return diff

def getDiff(r,s,mass):
    diff =[]
    for sig in r:
        print "in get diff "
        print sig 
        print s[mass]
        diff.append(sig-s[mass])
    return diff



if __name__=="__main__":
        g = ROOT.TGraphErrors()
        i=0
        label = sys.argv[1]   #"fullBkg_pythiaLPLP_expSig3_moreSyst"
        l={}
        err={}
        s={}
        
        histos ={}
        hr={}
        lr={}
        s = {}
        purity = "HPHP"
        if label.find("HPLP")!=-1:
            purity = "HPLP"
        results={}
        testR=False
        # for checking r variable just change "ef" to "r" and "events injected" to "r_in"
        variables =["ef","CMS_VV_JJ_nonRes_PT_"+purity,"CMS_VV_JJ_nonRes_OPT_"+purity,"CMS_VV_JJ_nonRes_PTZ_"+purity,"CMS_VV_JJ_nonRes_OPTZ_"+purity,"CMS_VV_JJ_nonRes_norm_"+purity, "CMS_VV_JJ_tau21_eff","CMS_lumi","CMS_pdf","CMS_res_j","CMS_scale_j","CMS_res_prunedj","CMS_scale_prunedj","CMS_tau21_PtDependence","CMS_VV_JJ_Wjets_norm_"+purity,"CMS_VV_JJ_Wjets_PT","CMS_VV_JJ_Wjets_OPT","CMS_VV_JJ_nonRes_altshape_"+purity,"CMS_VV_JJ_nonRes_altshape2_"+purity,"CMS_VV_JJ_nonRes_OPT3_"+purity]
        graphs_all = {}
        for var in variables:
            graphs_all[var]= (ROOT.TGraphErrors())
            graphs_all[var].SetName(var+"_graph")
        #variables = ["r","CMS_res_prunedj"]
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
            
            #if mass != "3600" or filename.find("9")==-1: continue
            
            if len(readLog(indir+filename,"events injected")[0]) ==0:
                #continue
                testR=True
                s[mass] = readLog(indir+filename,"r_in")[0][0]
            else: s[mass] = readLog(indir+filename,"events injected")[0][0]
            print "s for mass "+str(mass)+" "+str(s[mass]) 
            
            print "read file "+str(filename)
            results[mass] ={}
            
            for var in variables:    
                ldist = readLog(indir+filename,var)[0]
                lerr  = readLog(indir+filename,var)[1]
                #ldist = getLimit(filename)
                if (var.find("r")!=-1 or var.find("ef")!=-1) and var.find("CMS")==-1:    
                    rdiff = getDiff(ldist,s,mass)
                elif var.find("p0")!=-1:
                    rdiff = getDiff(ldist,3.09133077581e-06)
                elif var.find("p1")!=-1:
                    rdiff = getDiff(ldist,5.34319831451)
                elif var.find("p2")!=-1:
                    rdiff = getDiff(ldist,0)
                else:
                    rdiff = ldist
                if mass not in histos.keys():
                    bmin=-10
                    bmax=10
                    if var.find("res_j")!=-1:
                            bmin=-2
                            bmax=0.5
                    histos[mass]= [ROOT.TH1F("h_"+mass+"_"+variables[0],"h_"+mass+"_"+variables[0],100,bmin,bmax)]
                    
                    for nh in range(1,len(variables)):
                        if variables[nh].find("res_j")!=-1:
                            bmin=-0.2
                            bmax=0.2
                        if variables[nh].find("scale_j")!=-1:
                            bmin=-0.1
                            bmax=0.1
                        if variables[nh].find("scale_prunedj")!=-1:
                            bmin=-0.1
                            bmax=0.1
                        if variables[nh].find("nonRes_norm")!=-1:
                            bmin=-0.1
                            bmax=0.1
                        if variables[nh].find("Vjets_norm")!=-1:
                            bmin=-10
                            bmax=10
                        if variables[nh].find("p1")!=-1:
                            bmin=-10
                            bmax=10
                        if variables[nh].find("p0")!=-1:
                            bmin=0
                            bmax=30
                        if variables[nh].find("res_prunedj")!=-1:
                            bmin=-0.5
                            bmax=0.8
                        if variables[nh].find("pdf")!=-1:
                            bmin=-0.5
                            bmax=0.5
                        if variables[nh].find("lumi")!=-1:
                            bmin=-2
                            bmax=2
                        if variables[nh].find("tau21")!=-1:
                            bmin=-2
                            bmax=5
                        if variables[nh].find("tau21_Pt")!=-1:
                            bmin=-0.2
                            bmax=0.2
                        if variables[nh].find("OPT")!=-1 or variables[nh].find("PTXY")!=-1:
                            bmin=-1
                            bmax=1
                        if variables[nh].find("_PTZ")!=-1:
                            bmin=-0.5
                            bmax=1.5
                        histos[mass].append(ROOT.TH1F("h_"+mass+"_"+variables[nh],"h_"+mass+"_"+variables[nh],100,bmin,bmax))
                count =0
                if (var.find("r")!=-1 or var.find("ef")!=-1) and var.find("CMS")==-1:
                    if not mass in hr.keys():
                        hr[mass] = (ROOT.TH1F("hr","hr",50,0,s[mass]+95*s[mass]/10.))
                        lr[mass]= ldist 
                        for element in range(0,len(ldist)):
                            hr[mass].Fill(ldist[element])
                    else:
                        print "fill r histo and list " 
                        print len(ldist)
                        for element in range(0,len(ldist)):
                            hr[mass].Fill(ldist[element])
                            lr[mass].append(ldist[element])
                        print "end "
                for d in rdiff:
                    for nh in range(0,len(variables)):
                        if variables[nh]!=var:
                            continue
                        if var.find("CMS")!=-1:
                            histos[mass][nh].Fill(d/1.)
                        else:
                            print d
                            if testR==True:
                                if var.find("r")!=-1:
                                    histos[mass][nh].Fill(d)
                                else:
                                    histos[mass][nh].Fill(d/lerr[count])
                                
                            else:    
                                if var.find("ef")!=-1:
                                    histos[mass][nh].Fill(d)
                                else:
                                    histos[mass][nh].Fill(d/lerr[count])
                    count+=1
                    #print lr[mass]
                    #if d/lerr[count-1] > -2 and d/lerr[count-1] < -1.5:
                    #if d/lerr[count-1] < -4:
                    #    print filename
                    #    print count-1
            
        count = 0
        for m in sorted(histos.keys()):
            N=0
            #c = ROOT.TCanvas("c","c",1600,1600)
            #c.Divide(3,4)
            for h in histos[m]:
                mediantmp = array("d",[0])# ROOT.Double()
                h.GetQuantiles(1,mediantmp,array("d",[0.5]))
                results[m][h.GetName().split("0_")[1]] = mediantmp[0] 
                c = ROOT.TCanvas("c","c",400,400)
                func = fitWithGaus(h)
                h.GetYaxis().SetTitle("number of toys")
                h.GetXaxis().SetTitle("(r_{fit}-r_{in})/#sigma_{fit}")
                h.Draw("hist")
                func.Draw("same")
                if h.GetName().split("h_"+mass+"_")[-1].find("h_")==-1:
                    graphs_all[h.GetName().split("h_"+mass+"_")[-1]].SetPoint(N,float(m),h.GetMean())
                    graphs_all[h.GetName().split("h_"+mass+"_")[-1]].SetPointError(N,0,h.GetRMS())
                N+=1
                c.SaveAs("test_"+h.GetName()+"_"+m+"_"+label+".pdf")
                c.SaveAs("test_"+h.GetName()+"_"+m+"_"+label+".png")
                #if h.GetName().find("r")!=-1 and h.GetName().find("CMS")==-1:
                    #print "mass "+str(m)+" mean "+str(h.GetMean())
                    #g.SetPoint(count,float(m),float(h.GetMean()))
                    #g.SetPointError(count,100,float(h.GetRMS()))
            count+=1
            
            
        count=0        
        for m in sorted(hr.keys()):
            func  = ROOT.TF1("gauss" ,"gaus", hr[m].GetMean()-hr[m].GetRMS()*2,hr[m].GetMean()+hr[m].GetRMS()*2) 
            hr[m].Fit(func,"R")
            #tmp = fs.Get(m)
            if m == "3600":
                ctest = ROOT.TCanvas("ctest","ctest",400,400)
                hr[m].Draw()
                ctest.SaveAs("test.pdf")
                
            #if tmp==None:
            #    print " for mass "+mass+ " no graph found"
            #    continue
            #s = tmp.Eval(3)
            #s = readLog(indir+filename,"r_in")[0][0]
            if indir.find('expSig0')!=-1:
                s = 0
                
            median = array("d",[0])# ROOT.Double()
            hr[m].GetQuantiles(1,median,array("d",[0.5]))
            print "mass "+str(m)+" mean "+str(func.GetParameter(1))+" injected "+str(s[m])+" from histo " +str(hr[m].GetMean()) + " median "+str(median) 
            print "relative bias "+str(float(median[0]-s[m])/s[m])
            print "xsec "+str(s[m]*0.001)
            if s!= 0:
                #g.SetPoint(count,float(m),float(func.GetParameter(1)-s[m])/s[m])
                #g.SetPoint(count,float(m),float(median[0]-s[m])/s[m])
                #g.SetPointError(count,0,hr[m].GetRMS()/(2.*s[m]))
                #g.SetPoint(count,float(m),float(median[0]-s[m])/s[m])
                g.SetPoint(count,float(m),float(hr[m].GetMean()-s[m])/s[m])
                g.SetPointError(count,0,hr[m].GetRMS()/(2*s[m]))
            else:
                g.SetPoint(count,float(m),numpy.median(lr[m]))
                g.SetPointError(count,0,hr[m].GetRMS()/(2.*s[m]))
            count+=1
            
            print "number of entries per mass "+str(mass)
            print hr.keys()
            print hr[m].GetEntries()
            print hr[m].GetMean()
            print median[0]
            print s[m]
            #sys.exit()

        
        c = getCanvas()
        c.SetGrid()
        g.GetXaxis().SetTitle("dijet invariant mass (GeV)")
        g.SetMaximum(0.5)
        g.SetMinimum(-0.5)
        g.SetLineColor(ROOT.kBlue)
        g.SetMarkerColor(ROOT.kBlue)
        g.SetMarkerStyle(4)
        line1 = ROOT.TLine()
        line1.SetLineStyle(3)
        line1.DrawLine(1000,0.5,5000,0.5)
        line1.DrawLine(1000,-0.5,5000,-0.5)
        
        #g.GetYaxis().SetTitle("signal strength")
        #g = beautify(g,ROOT.kBlue,3,"(r_{fit}-r_{in})/#sigma_{fit}")
        g = beautify(g,ROOT.kBlue,4,"relative bias")
        outfile = ROOT.TFile("biasTest_"+label+".root","RECREATE")
        g.SetName("rel_bias")
        g.Write()
        g.Draw("ALP")
        c.SaveAs("biasTest_"+label+".pdf")
        c.SaveAs("biasTest_"+label+".png")
        for k in graphs_all.keys():
            graphs_all[k].Write()
        outfile.Close()
        print results
        plotPulledParamters(["CMS_res_j","CMS_res_prunedj"],results,"pull_res.pdf")
        
        plotPulledParamters(["CMS_scale_j","CMS_scale_prunedj","CMS_tau21_PtDependence"],results,"pull_scale.pdf")
        
        #plotPulledParamters(["CMS_VV_JJ_nonRes_OPTXY","CMS_VV_JJ_nonRes_PTXY"],results,"pull_qcd_xy.pdf")
   
        plotPulledParamters(["CMS_VV_JJ_nonRes_OPTZ_"+purity,"CMS_VV_JJ_nonRes_PTZ_"+purity,"CMS_VV_JJ_nonRes_OPT3_"+purity,"CMS_VV_JJ_nonRes_altshape_"+purity,"CMS_VV_JJ_nonRes_altshape2_"+purity],results,"pull_qcd_z.pdf")
        
        plotPulledParamters(["CMS_VV_JJ_nonRes_norm_"+purity, "CMS_VV_JJ_tau21_eff","CMS_lumi","CMS_pdf","CMS_VV_JJ_Wjets_norm_"+purity],results,"pull_norm.pdf")
        
