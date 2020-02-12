''' simulation for the 5-qubit (Kitaev) Shor experiment '''

import numpy as np
import PyTIQC.core.simtools as sim
import PyTIQC.core.qctools as qc
import PyTIQC.core.gates as U
import matplotlib.pyplot as pl

import time, sys, pickle, datetime
import shelve, copy

import Kitaev
reload(Kitaev)

from PyTIQC.tools import pp
    
pi = np.pi

### run params ##################################
pulseseqfileShor = os.path.join(os.path.dirname(__file__),'Shorseq.py')

firstMultMap = True # Do first multiplication with CNOT 
                    # mapping instead of Multiplier 
                    # (does nothing in easy cases)
select_a = 2 # Factoring base: 2, 4, 7, 8, 13, 11, or 14

doRun = True
doIdeal = False
printpulse = False
saveKitaev = False
doPPKitaev = False # pp is not None

print('a =',select_a)

NumberOfIons = 5
NumberOfPhonons = 0 if doIdeal else 7 
hspace = sim.hspace(NumberOfIons,2,NumberOfPhonons,0)
hspace.initial_state("quantum", qstate='DSSSS')
params = sim.parameters(hspace)

params.use_servers( ['all'] )
params.ppcpus = 0
params.shortestMS = 16
params.calcPulseParams()
params.progbar = False
params.saveallpoints = False
params.coherenceTime = 15000
params.hidingerr = 1

params.printpulse = printpulse
params.progbar = printpulse
params.pplog = False

dec = sim.decoherence(params)
dec.doRandNtimes = 2
dec.doPP = pp is not None
dec.progbar = printpulse
dec.dict['all'] = False # not doIdeal
dec.dict['none'] = True # not doIdeal
#    if doPPKitaev: params.ppcpus = 2

Kit = Kitaev.Kitaev()

##########################################
# load the pulse sequences
# change ion order and define permutations
##########################################
# execfile(pulseseqfileShor,locals(),globals())
# exec(open(pulseseqfileShor).read(),globals(),locals()) #,locals(),globals())

#Fredkin gate
Fredkin = sim.PulseSequence([ \
sim.Rcar(params, 0.5*pi, 0.5*pi),
sim.Rac(params, 0.5*pi, 0, 0),
sim.RMS(params, 0.5*pi, pi/2),
sim.Rac(params, 0.5*pi, 0, 1),
sim.Rac(params, -0.5*pi, 0, 0),
sim.Rcar(params, 0.75*pi, 1*pi),
sim.RMS(params, -0.25*pi, pi/2),
sim.Rac(params, 0.5*pi, 0, 1),
sim.RMS(params, 0.5*pi, pi/2),
sim.Rcar(params, 0.5*pi, 0*pi),
sim.Rac(params, -0.25*pi, 0, 1),
sim.Rac(params, 0.5*pi, 0, 0),
sim.RMS(params, 0.5*pi, pi/2),
sim.Rac(params, 0.5*pi, 0, 1),
sim.Rac(params, 0.5*pi, 0, 2),
sim.Rcar(params, 0.5*pi, 0*pi),
sim.Rac(params, -0.5*pi, 0, 2),
sim.Rac(params, -0.5*pi, 0, 1)  ])

# CNOT on first four computational qubits:
def cnot1234():
    return sim.PulseSequence([ \
            sim.Rcar(params, 1.5*pi, 0*pi),
            sim.Rac(params, 1.5*pi, 0, 0), 
            sim.RMS(params, 0.25*pi, 0.5*pi),
            sim.Rcar(params, 0.75*pi, 0*pi),
            sim.Rac(params, 1*pi, 0, 0), 
            sim.RMS(params, 1.75*pi, 0.5*pi),
            sim.Rcar(params, 0.75*pi, 0*pi),
            sim.Rac(params, 1.5*pi, 0, 0), 
            sim.Rcar(params, 0.5*pi, 0*pi) ])

# CNOT on first two computational qubits
cnot12 = sim.PulseSequence([ \
sim.Rcar(params, pi/2, 0),
sim.Rac(params, -pi/2, 0, 0),
sim.Rcar(params, pi/4, 0),
sim.RMS(params, pi/8, pi/2),
sim.Rac(params, -pi, 0, 1),
sim.Rac(params, -pi, 0, 2),
sim.Rcar(params, pi/4, 0),
sim.RMS(params, -pi/8, pi/2),
sim.Rac(params, -pi, 0, 0),
sim.RMS(params, pi/8, pi/2),
sim.Rac(params, -pi, 0, 1),
sim.Rac(params, -pi, 0, 2),
sim.RMS(params, -pi/8, pi/2),
sim.Rcar(params, pi/2, pi),
sim.Rac(params, -pi/2, 0, 0),
sim.Rcar(params, pi/2, pi) ])


# shor11 = sim.PulseSequence([ \
# sim.Rcar(params, pi/2, 0),
# sim.Rac(params, -pi/2, 0, 0),
# sim.Rcar(params, pi/4, 0),
# sim.RMS(params, pi/8, pi/2),
# sim.Rac(params, -pi, 0, 1),      
# sim.Rac(params, -pi, 0, 3),      
# sim.Rcar(params, pi/4, 0), 
# sim.RMS(params, -pi/8, pi/2),    
# sim.Rac(params, -pi, 0, 0),      
# sim.RMS(params, pi/8, pi/2),  
# sim.Rac(params, -pi, 0, 1),   
# sim.Rac(params, -pi, 0, 3),       
# sim.RMS(params, -pi/8, pi/2),    
# sim.Rcar(params, pi/2, pi),
# sim.Rac(params, -pi/2, 0, 0),
# sim.Rcar(params, pi/2, pi) ])
# 
# shor7a = sim.PulseSequence([ \
# sim.Rcar(params, pi/2, 0),
# sim.Rac(params, -pi/2, 0, 0),
# sim.Rcar(params, pi/4, 0),
# sim.RMS(params, pi/8, pi/2),
# sim.Rac(params, -pi, 0, 2),   
# sim.Rac(params, -pi, 0, 3),   
# sim.Rcar(params, pi/4, 0), 
# sim.RMS(params, -pi/8, pi/2), 
# sim.Rac(params, -pi, 0, 0),   
# sim.RMS(params, pi/8, pi/2),  
# sim.Rac(params, -pi, 0, 2),    
# sim.Rac(params, -pi, 0, 3),    
# sim.RMS(params, -pi/8, pi/2),  
# sim.Rcar(params, pi/2, pi),
# sim.Rac(params, -pi/2, 0, 0),
# sim.Rcar(params, pi/2, pi) ])


def Fredij(i,j):
    fred = copy.deepcopy(Fredkin)
    fred.changeions(params,(i,j,0))
    return fred

# Fred12 = copy.deepcopy(Fredkin)
# Fred23 = copy.deepcopy(Fredkin)
# Fred34 = copy.deepcopy(Fredkin)
# Fred24 = copy.deepcopy(Fredkin)
# Fred13 = copy.deepcopy(Fredkin)
# Fred12.changeions(params, (1,2,0))
# Fred23.changeions(params, (2,3,0))
# Fred34.changeions(params, (3,4,0))
# Fred24.changeions(params, (2,4,0))
# Fred13.changeions(params, (1,3,0))

def cnotij(i,j):
    cnot = copy.deepcopy(cnot12)
    cnot.changeions(params,(0,i,j))
    return cnot

# cnot13 = copy.deepcopy(cnot12)
# cnot24 = copy.deepcopy(cnot12)
# cnot13.changeions(params,(0,1,3))
# cnot24.changeions(params,(0,2,4))


# times13 = copy.deepcopy(times8)
# times13.append(cnot1234)

# times7 = copy.deepcopy(times2)
# times7.append(cnot1234)


### general pulse sequence
def GeneratePulseSeq(a):

    NOP = lambda: sim.PulseSequence([sim.Delay(params, 0.1)])

    if a in (2,7,8,13): # hard cases
        if firstMultMap:
            a2modN = cnotij(2,4)
        else:
            a2modN = sim.PulseSequence([ \
                sim.Hide(params, 1, True),
                sim.Hide(params, 3, True), #vis: 2,4
                Fredij(2,4),
                sim.Hide(params, 1, False),
                sim.Hide(params, 3, False),
                sim.Hide(params, 2, True),
                sim.Hide(params, 4, True), #vis: 1,3
                Fredij(1,3),
                sim.Hide(params, 2, False),
                sim.Hide(params, 4, False)
                ])
    else:               # easy cases
        a2modN = NOP()
    

    if a == 4:
        amodN = cnotij(2,4)
    elif a == 11:
        amodN = cnotij(1,3)
    elif a == 14:
        amodN = cnot1234()
    elif a in (8,13):
        amodN = sim.PulseSequence([ \
            sim.Hide(params, 1, True),
            sim.Hide(params, 2, True), #vis: 3,4
            Fredij(3,4),
            sim.Hide(params, 2, False),
            sim.Hide(params, 4, True), #vis: 2,3
            Fredij(2,3),
            sim.Hide(params, 1, False),
            sim.Hide(params, 3, True), #vis: 1,2
            Fredij(1,2),
            sim.Hide(params, 3, False),
            sim.Hide(params, 4, False)
            ])
    elif a in (2,7):
        amodN = sim.PulseSequence([ \
            sim.Hide(params, 3, True),
            sim.Hide(params, 4, True), #vis: 1,2
            Fredij(1,2),
            sim.Hide(params, 3, False),
            sim.Hide(params, 1, True), #vis: 2,3
            Fredij(2,3),
            sim.Hide(params, 4, False),
            sim.Hide(params, 2, True), #vis: 3,4
            Fredij(3,4),
            sim.Hide(params, 1, False),
            sim.Hide(params, 2, False) #vis: 1,2,3,4
            ])

    if a in (7,13):
        amodN.append(cnot1234())


    # if   a == 2:
    #     amodN = times2
    # elif a == 7:
    #     # amodN = times7
    #     amodN = copy.deepcopy(times2)
    #     amodN.append(cnot1234)
    # elif a == 8:
    #     amodN = times8
    # elif a == 13:
    #     # amodN = times13
    #     amodN = copy.deepcopy(times8)
    #     amodN.append(cnot1234)
    # elif a == 4:
    #     amodN = cnot24
    # elif a == 11:
    #     amodN = cnot13
    # elif a == 14:
    #     amodN = cnot1234

    pulseseq_group = Kit.GeneratePulseSeq(params, [NOP(), a2modN, amodN])
    return pulseseq_group

#######################################################

pulseseq = GeneratePulseSeq(select_a)
# def main():
    #return pulseseq

if doIdeal:
    for ps in pulseseq:
        for pulse in ps:
            pulse.use_ideal = True

### run it
if doRun:
    tic = time.time()
    result = Kit.simulateevolution(pulseseq, params, dec, doPP=doPPKitaev)
    if not doIdeal: print("runtime: ", time.time()-tic, "sec")
    print(np.around(result,6))

if saveKitaev:
    timestr = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    fnameappend = ''
    Kit.getQFTall()
    Kit.datagroupsave('Shor'+str(select_a)+'-data-'+fnameappend+timestr+'.pk', 
                      RhoOnly=True)
    Kit.resultSave('Shor'+str(select_a)+'-res-'+fnameappend+timestr+'.npy')
    f = open('Shor'+str(select_a)+'-params-'+fnameappend+timestr+'.pk', 'wb')
    pickle.dump(dec.dict_params_static, f)
    f.close()

#    return True#dataobj

#if __name__ == '__main__':
#    ps = main()
