#!/usr/bin/env python
import os, re
import commands
import math, time
import sys
import random

print 
print 'START'
print

def makeSubmitFileCondor(exe,jobname,jobflavour):
    print "make options file for condor job submission "
    submitfile = open("submit.sub","w")
    submitfile.write("executable  = "+exe+"\n")
    submitfile.write("arguments             = $(ClusterID) $(ProcId)\n")
    submitfile.write("output                = "+jobname+".$(ClusterId).$(ProcId).out\n")
    submitfile.write("error                 = "+jobname+".$(ClusterId).$(ProcId).err\n")
    submitfile.write("log                   = "+jobname+".$(ClusterId).log\n")
    submitfile.write('+JobFlavour           = "'+jobflavour+'"\n')
    submitfile.write("queue")
    submitfile.close()

 
#python /afs/cern.ch/user/d/dschafer/forBiasTests//doFitsWithToys2.py -n /afs/cern.ch/user/d/dschafer/forBiasTests/workspace_JJ_ZprimeWW_HPLP_13TeV_2017.root -t 30 -k /afs/cern.ch/user/d/dschafer/forBiasTests/2017/save_new_shapes_pythia_HPLP_3D.root --mass 2000 --output res/ --signalStrength /afs/cern.ch/user/d/dschafer/forBiasTests/scanSignalStrength_HPLP.root --norm /afs/cern.ch/user/d/dschafer/forBiasTests/2017/JJ_nonRes_HPLP.root --label HPLP_ZprimeWW_pythia13 --expSig 6  --useKernel histo 
 
########   YOU ONLY NEED TO FILL THE AREA BELOW   #########
########   customization  area #########
NumberOfJobs= 30 # number of jobs to be submitted
queue = "8nh" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw 
mydir = "/afs/cern.ch/user/d/dschafer/forBiasTests/"

#workspace = mydir+"workspace_JJ_ZprimeWW_HPLP_13TeV_2017.root"
#kernel    = mydir+"2017/save_new_shapes_powheg_HPLP_3D.root"
#fornorm   = mydir+"2017/JJ_powheg_HPLP.root"
#signalStrength  = mydir+'scanSignalStrength_HPLP.root'



#workspace = mydir+"workspace_JJ_ZprimeWW_HPLP_13TeV_2016.root"
#kernel    = mydir+"2016/save_new_shapes_madgraph_HPLP_3D.root"
#fornorm   = mydir+"2016/JJ_madgraph_HPLP.root"
#signalStrength  = mydir+'scanSignalStrength_HPLP.root'


workspace = mydir+"workspace_JJ_ZprimeWW_HPHP_13TeV_2017.root"
kernel    = mydir+"2017/save_new_shapes_herwig_HPHP_3D.root"
fornorm   = mydir+"2017/JJ_herwig_HPHP.root"
signalStrength  = mydir+'scanSignalStrength_HPHP.root'


#workspace = mydir+"MC2017trigWeights/workspace_HPHP_2017Trig.root"
#kernel    = mydir+"MC2017trigWeights/JJ_nonRes_3D_HPHP.root"
#fornorm   = mydir+"MC2017trigWeights/JJ_nonRes_HPHP.root"
#signalStrength  = mydir+'MC2016trigWeights/scanSignalStrength_HPHP_trig2016.root'
out  = mydir+"res/"
masses = [1200,1600,2000,2400,2800,3200,3600,4000,4500] #for these tests add mass point 1000 but for that it is necessary to change the program!
#masses = [4500]
bkghisto="histo"
label = "HPHP_ZprimeWW_herwig_2sigma"
expSig = 3

cmspath="/afs/cern.ch/user/d/dschafer/CMSSW_10_2_10/src/"
#mydir = os.getcwd()
########   customization end   #########

path = os.getcwd()
print
print 'do not worry about folder creation:'
#os.system("rm -r tmp")
os.system("mkdir tmp")
os.system("mkdir res")
print

##### loop for creating and sending jobs #####
for x in range(1, int(NumberOfJobs)+1):
 for mass in masses:   
   print mass  
   ##### creates directory and file list for job #######
   os.system("mkdir tmp/job"+str(x)+"_M"+str(mass)+label)
   os.chdir("tmp/job"+str(x)+"_M"+str(mass)+label)
   #os.system("mkdir -p log")      # added this for KA
   #os.system("mkdir -p out")      # added this for KA
   #os.system("mkdir -p error")    # added this for KA
   path = os.getcwd()
   
   ##### creates jobs #######
   with open('job.sh', 'w') as fout:
      fout.write("#!/bin/sh\n")
      fout.write("echo\n")
      fout.write("echo\n")
      fout.write("echo 'START---------------'\n")
      fout.write("echo 'WORKDIR ' ${PWD}\n")
      fout.write("myworkdir=${PWD}\n")
      fout.write("source /afs/cern.ch/cms/cmsset_default.sh\n")
      fout.write("cd "+cmspath+"\n")
      fout.write("cmsenv\n")
      fout.write("cd $myworkdir\n")
      fout.write("mkdir res\n")
      fout.write("python %s/doFitsWithToys2.py -n %s -t 30 -k %s --mass %i --output %s --signalStrength %s --norm %s --label %s --expSig %i  --useKernel %s\n"%(mydir,workspace,kernel,mass,"res/",signalStrength,fornorm,label+str(x),expSig,bkghisto))
      fout.write("echo 'STOP---------------'\n")
      fout.write("echo\n")
      fout.write("echo\n")
      fout.write("echo 'copy back file'\n")
      fout.write("cp res/* "+out+"\n")
   os.system("chmod 755 job.sh")
   
   ###### sends bjobs ######
   #os.system("bsub -q "+queue+" -o logs job.sh")
   makeSubmitFileCondor("job.sh",label,"workday")
   os.system("condor_submit submit.sub")


   print "job nr " + str(x) + " submitted"
   
   os.chdir("../..")
   
print
print "your jobs:"
#os.system("bjobs")
print
print 'END'
print
