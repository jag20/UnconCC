import ham 
import numpy as np
import CCD

#This script demonstrates the use of the CCD and CCDutils modules
#to run attenuated Coupled Cluster(Gomez, Henderson and Scuseria, Mol. Phys. online 23 Mar 2017)
#for 1D 10-site Hubbard at half filling with periodic boundary conditions for a range of U values

flnm = "./Output"
print("Writing results to ", flnm)
with open(flnm, "w") as f:
   f.write("U" + "     " + "Ecorr" + "            "+ "Escf" + "\n")
   for U in np.arange(1.,10.1,.2):
    print("U = ", U)
    #Build hamiltonian and do RHF
    hub = ham.hub(nsitesx=10,nsitesy=1,U=U,fill=0.5,PeriodicX=True)
    hub.get_ints(wfn_type="rhf")
    #Do attenuated coupled cluster
    CCD.ccd(hub,ampfile="amps",variant="acpd45")
    f.write(str(U) + "   " + str(hub.eccd) + "  "+ str(hub.escf) + "\n")
 

