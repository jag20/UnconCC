from CCSDutils import *
import CCDutils 
import os
import pickle
import CCD
from scf import moUHF_to_GHF

def ccsd(ham,ampfile="none",variant="ccd"):
	#We need to convert integrals to spin-orbital basis if our meanfield is RHF
	if (ham.wfn_type == 'rhf'):
		print("converting RHF wavefunction to spin-orbital basis")
		ham.F, ham.Eri, ham.C = moUHF_to_GHF(ham.C,ham.C,ham.F,ham.F,ham.Eri,ham.nocc,ham.nocc,ham.nbas)
		ham.nbas  *= 2
		ham.nocc  *= 2
		ham.nvirt *= 2
		ham.wfn_type = 'uhf'

#read amplitudes from file if present to improve convergence
	if ((ampfile != 'none') and(os.path.isfile(ampfile))):
		with open(ampfile, 'rb') as f:
			T2 = pickle.load(f)
			T1 = pickle.load(f)

		E2 = CCDutils.GCCDEn(ham.Eri,T2,ham.nocc)
		E1 = GCCSEn(ham.F,ham.Eri,T1,ham.nocc)
		ecorr = E1 + E2
		eold = ecorr
	else:
		T2 = np.zeros([ham.nocc,ham.nocc,ham.nvirt,ham.nvirt])
		T1 = np.zeros([ham.nocc,ham.nvirt])
		eold = 0.0e0

	#Set up for CCD iteration and DIIS. interpolate doubles only for now
	diis_start, diis_dim, Errors, T2s, Err_vec = CCDutils.diis_setup(ham.nocc,ham.nvirt)
	T1Errors, T1s, T1Err_vec = diis_singles_setup(ham.nocc,ham.nvirt,diis_start,diis_dim)
	G1 = CCSDsingles(ham.F,ham.Eri,T2,T1,ham.nocc,ham.nbas)
	G2 = CCSDdoubles(ham.F,ham.Eri,T2,T1,ham.nocc,ham.nbas,variant)
	niter = 1
	tol = 1.0e-9
	error = tol*50

	print("Beginning CCSD iteration")
	while (error > tol):
		T2, Errors, T2s = CCDutils.diis(diis_start,diis_dim,niter,Errors,T2s,T2,Err_vec)
		T1, T1Errors, T1s = diis_singles(diis_start,diis_dim,niter,T1Errors,T1s,T1,T1Err_vec)
   	#build RHS
		G1 = CCSDsingles(ham.F,ham.Eri,T2,T1,ham.nocc,ham.nbas)
		G2 = CCSDdoubles(ham.F,ham.Eri,T2,T1,ham.nocc,ham.nbas,variant)
		#Get error
		T2error, Err_vec = CCDutils.get_Err(ham.F,G2,T2,ham.nocc,ham.nvirt)
		T1error,T1Err_vec = get_singles_Err(ham.F,G1,T1,ham.nocc,ham.nvirt)
		error = 0.5e0*(T2error+T1error)

   	#solve H
		T1 = solveccs(ham.F,G1,T1,ham.nocc,ham.nvirt,x=1.0)
		T2 = CCDutils.solveccd(ham.F,G2,T2,ham.nocc,ham.nvirt,x=1.0)

   	#get energies
		E1 = GCCSEn(ham.F,ham.Eri,T1,ham.nocc)
#		E1 = 0.0e0
		E2 = CCDutils.GCCDEn(ham.Eri,T2,ham.nocc)
		ecorr = E1 + E2
#		error = np.abs(ecorr-eold)
		print("Iteration = ", niter, " ECorr = ", ecorr, "error = ", error)
		eold = ecorr 
		niter += 1  


	if ((ampfile != 'none')):
		with open(ampfile, 'wb') as f:
			pickle.dump(T2,f)
			pickle.dump(T1,f)

	ham.ecorr = ecorr
	
	
