# Pico float estimate of log2 Q for family 192 Gaussian packet, from PROOF.md parameters only.
import numpy as np
c=3/8; h=2.0**-20; r=2.0**-33
j=np.arange(-2**23,2**23+1,dtype=np.float64); x=c+j*h
# beta_j = Phi(x+r)-Phi(x-r) = 2r*phi(x)*(1+O(r^2)); log2 phi(x) = -x^2/(2 ln2) - log2(sqrt(2pi))
log2beta = np.log2(2*r) - x**2/(2*np.log(2)) - np.log2(np.sqrt(2*np.pi))
print("leaves",len(j),"log2 Q ~", np.sum(log2beta, dtype=np.float64), "claimed bound > -1426063445")
