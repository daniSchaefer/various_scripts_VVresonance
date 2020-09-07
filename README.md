# Instructions on how to run the scripts compiled in this repo

for running any of these scripts you'll need ROOT.


## script makeProjections.py
script to make quick stackplots of all of our background components starting from the normalisation files that come out of the makeInputs scripts. I use this script as well to check the relative contribution of minor backgrounds to QCD per category that is detailed in the AN (section about minor Bkg).
output of this script are stackplots called for example: CP_background_py_xrange55-215_yrange55-215zrange1126-5000_VV_HPHP.pdf
as well as a table like this (numbers given here for VV_HPHP):

   contribution      events           events/all events 
        qcd    2945.1    0.6
        Wjets 634.2    0.131
        Zjets 209.5    0.043
        ttbar 1056.7    0.218
        
giving the number of events per bkg as well as the relative contribution to all background events

```
py makeProjections.py directory_results_from_makeInputs/ category
```

## evaluate PDF uncertainties from the lhapdf package

first run the script :

```
py evaluatePDFUncertainties.py filename.root outputfilename.txt

```
the output of this script is a outputfilename.txt containing three numbers: processed events, the number of all events with differing pdfweights applied, and those same numbers for the HPHP and HPLP category! these scripts are old and contain the tau21DDT selections used in B2G18002!
the second output is a file called outputfilename.root which contains histograms the jet mass (category_hsdmass_x) and the dijet invariant mass (category_hdijetmass_x) for each pdf variation (x) and the two old purity categories. By running
```
py evaluatePDFUncertainties_step2.py -s signal -m masspoint1,masspoint2,...,masspointN -p pdfsetnumber
```
an output txt file is created containing the relative uncertainty (1 sigma) on the acceptance, cross section and the scale/resolution of the jet mass and dijet invariant mass due to the different PDF uncertainties -> last time i evaluated this for B2G18002 the uncertainties were about 3% for the acceptance 10-150% for the cross section and <1% for the resolution/scale of the jetmass and dijet mass distributions. 
These resolution and scale uncertainties are derived from a gaussian fit to the core of the mass distributions.

## evaluate JEC uncertainties

The scripts for this can be found in here: CMGTools/VVResonances/interactive (on mybranch)
There are two scripts, one in the scripts directory called vvMakeJECShapes.py to actually make and fit the histograms the other called JECUncertainties_2017.py which runs the other script.
Here i initially copied the selection cuts of the analysis again but this should now be easily updated and replaced with the cuts from init_VV_VH.json and the cut.py class. After that you can also run this on every year. Somewhere in this code i stupidly hardcoded the directory containing the JES/JER uncertainty trees on lxplus this will need to be changed!
Once you change the selection cuts, some of the code in the main part of JECUncertainties_2017.py will need to be changed so that all new categories are in there. this code as well produced .txt files as output containg the 1 sigma uncertainty on the mean/width of a gaussian fitted to the jetmass and dijetmass spectrum of different signals and with different signal masses. 
In the past i just got one value from this file -> the maximum up/down variation over all signals and mass points, which in the end was around 5-13% for the resolution and about 2-3% for the mean of the distribution. This must be reevaluated with the new tagger and new categories!!!

run with
```
py JECUncertainties_2017.py
```

## make histograms with pseudodata for the datacards

I have my own file to make pseudo-data -> the main reason for this were the tests i did with trying to fit pseudodata from madgraph/herwig/powheg events and fitting them with the kernels derived from pythia. For most of the tests i did i used pseudodata thrown from the kernels derived with madgraph/herwig/powheg because using the MC had too many fluctuation because of limited statistics. However using MC simulation directly would be better and now you can just use the NP category (which has higher stats) to throw toys. For this you will have to change the code in makePseudoData.py a bit though.
run with:
```
py makePseudoData.py -o outputfile.root -k kernelforqcd.root --norm normfileqcd.root --useKernel histo/histo_altshape/... --workspace workspace.root --purity VX_XX --period 201X --which all/ttbar/vjets
```
The ws you will only need if you go into the code and change that the minor backgrounds are not toys thrown from MC anymore but rather from their pdfs in the ws. the code is commented right now since i wanted to compare to MC simulation for all the tests so far.
the flag --which decide whether the toys contain all bkg (all), just ttbar (ttbar) or all minor bkg (vjets). 
With the --histo flag you can decide which kernel histo is used to generate the qcd bkg toys.



## make GOF fit tests and test the distribution of fit parameters

There is some functionality of combine that does something very similar, however there you can ONLY throw toys from your input model. I wanted to make GOF tests for distributions (madgraph/herwig/etc.) that are explicitly not part of my input model. This is the reason why i wrote my own scipts for this. 
run with:
``` 
py run_mlfit_jobs.py
```
In this file you will have to change for example if an how much signal should be injected , which workspace to use, which distribution to use to throw the toys from etc. The script then automatically submits the toy generation and fits to the lxplus condor-batch. 
Output of these fits are .txt files that look like this:


begin making signal + background toys with 6.000000 sigma signals and a signal mass of 2000 
nEvents_sig = 20.0
effective injected r_in = 15.1436552299
##################### for toy number 0 ############################
CMS_VV_JJ_Wjets_OPTZ_HPHP = -0.00141484648028 - -0.099972408521 + 0.0989433651719 L(-0.4 0.4)
CMS_VV_JJ_Wjets_PTZ_HPHP = 0.000990787853103 - -0.09999754191 + 0.0989601254959 L(-0.4 0.4)
CMS_VV_JJ_Wjets_norm = 0.12205616516 - -0.946927184864 + 0.944153787782 L(-7.0 7.0)
CMS_VV_JJ_Zjets_OPTZ_HPHP = -0.000478692917687 - -0.100004399781 + 0.0989703140385 L(-0.4 0.4)
CMS_VV_JJ_Zjets_PTZ_HPHP = 0.000494647476883 - -0.100000177341 + 0.098976689466 L(-0.4 0.4)
CMS_VV_JJ_Zjets_norm = -0.0984939466195 - -0.984230595676 + 0.981043226625 L(-7.0 7.0)
CMS_VV_JJ_nonRes_OPT3_HPHP = 0.959057837159 - -0.330616462232 + 0.327305020546 L(-0.332 2.332)
CMS_VV_JJ_nonRes_OPT_HPHP = 0.0895961982382 - -0.247550587358 + 0.246083795828 L(-1.332 1.332)
CMS_VV_JJ_nonRes_PT_HPHP = -0.0836592649427 - -0.272887427381 + 0.271037562302 L(-1.332 1.332)
CMS_VV_JJ_nonRes_altshape2_HPHP = 0.0565644215991 - -0.316249354346 + 0.313320824507 L(-1.332 1.332)
CMS_VV_JJ_nonRes_altshape_HPHP = 0.140923734527 - -0.245075099405 + 0.243791916143 L(-1.332 1.332)
CMS_VV_JJ_nonRes_norm = 0.200013020309 - -0.159766759264 + 0.159798315215 L(-7.0 7.0)
CMS_VV_JJ_tau21_eff = -0.0310027879764 - -0.829876421805 + 0.828157082482 L(-7.0 7.0)
CMS_lumi = 0.00337148544439 - -0.998736234533 + 0.995374565062 L(-7.0 7.0)
CMS_pdf = 0.00040560612887 - -0.999978534089 + 0.99662754218 L(-7.0 7.0)
CMS_res_j = 0.00430758073421 - -0.0779467856025 + 0.0771919605192 L(-0.32 0.32)
CMS_res_prunedj = -0.0127649474459 - -0.0757612080573 + 0.0750696205081 L(-0.32 0.32)
CMS_scale_j = 0.00561519236865 - -0.00983942174535 + 0.00977119031197 L(-0.048 0.048)
CMS_scale_prunedj = 0.0028148685436 - -0.0140441818793 + 0.0139747623214 L(-0.08 0.08)
CMS_tau21_PtDependence = 0.0043146461874 - -0.999939643677 + 0.989623995778 L(-4.0 4.0)
r = 14.2254104535 - -5.46797994415 + 5.46630883451 L(0.0 800.0)


containing the fit result and uncertainty from the fit of each nuisance parameter as well as the injected (r_in) and fitted (r) signal.
All scripts discussed in the following need these files as input.
There should be no need to change anything when the nuisance parameters change, the script should handle it automatically.
Unfortunately these scripts do not yet use the new plotting class but rather our old plotting script. The lines that plot should be commented out when submitting to batch we do not want a plot for all of these fits (they are just plotted for debugging purposes).
For the signal injection it is important to note that here you will need an additional signal_strength.root file containing the significance (calculated from combine) as a function of number of signal events (How i made this file is below) for different signal masses. This is more correct than just injecting a number since we for sure take a number of signal events that for example yield a significance of 3 sigma. BUT doing it this way is more computational work. This stuff might therefore be replaced by just injected a guess for the signal events that correspond to about 3 sigma (or something like this). i
at the moment you give that same of said signal_strength.root file with the option --signalStrength and choose the expected significance with --expSig

With the scripts plotBias.py plotBias2.py and makeBeautifulBiasPlots.py, it is possible to make some nice (and not so nice) visualisation of the results of these toys. 

```
py plotBias.py HPLP_ZprimeWW_pythia
```
you can make simple histos containing the postfit values of each of the nuisance parameters -> to check if we have a centered/pulled distribution and to check the scattering of this parameter after the fit. In these histos it for example shows up as a double peak structure in some of the nuisance parameters if the fit does not converge properly. In this script things need to be changed if the nuisances/ names of nuisances change. 

Using

```
py plotBias2.py HPLP_ZprimeWW_pythia
```
you can make the plots found on pages 124 and following in my thesis. I.e. the pull plots for different nuisance parameters as function of the dijet invariant mass. These plots are quite nice to show how the fit behaves for example when different qcd shapes are used in the toys. There is one workaround that is quite ugly in here: i rescale the qcd normalisation so that it is centered. The reason for this was that i made toys with the number of events i would expect from actual data, which was not the same as if we just apply all the selections to qcd (this was the expected value for the fit however) so in order to not show giant pulls in the qcd norm i retroactively rescaled the expected value for this norm. If you shold make these toys in the future i would suggest to remove this rescaling and just throw the number of expected events (as we expect them from qcd MC). 

The bias plots for signal injection (see my thesis page 129) are made with:
```
py makeBeautifulBiasPlots.py
```
In this script you will need to change the names of input files (i.e. the txt files that come out of the fits to toys...)

The last script you will need is to plot the goodness of fit tests. It is called goftest.py and makes the plots you can find on page 123 of my thesis. This file is run with:

```
py goftest.py -o outputname -f combinefilecontainingtoys.root -s combinefilecontainingobserved.root -l labelofoutputfigure
```
The input files here are made using combine (combine -M GoodnessOfFit workspace_JJ_BulkGWW_13TeV.root --algo=saturated -t 10 -s -1 --toysFreq) with 1000 toys (best to parallelize and then hadd the files so it can be plotted with the goftest.py script.

You can find a way to parallelize this and submit it to batch (as well as the code to make the above mentioned signalstrenght file in this git repo: https://github.com/daniSchaefer/job_submission Unfortunately this only works out of the box on the condor-batch here in KA but its only the submission part that needs to be changed for you)


## make some other nice plots

makePHDplots.py  is a simple plotting script that makes for example nicer plots for the kernel resolution histograms and stuff like that. 
