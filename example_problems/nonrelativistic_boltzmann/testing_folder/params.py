import numpy as np
import arrayfire as af

# Can be defined as 'electrostatic', 'user-defined'.
# The initial conditions need to be specified under initialize
# Ensure that the initial conditions specified satisfy
# Maxwell's constraint equations
fields_initialize = 'fft'

# Can be defined as 'electrostatic' and 'fdtd'
fields_solver = 'fdtd'

# Can be defined as 'strang' and 'lie'
time_splitting = 'strang'

# Can be defined as 'RK2', 'RK4' and 'RK6'
time_stepper = 'RK6'

# Dimensionality considered in velocity space:
p_dim = 1

# Constants:
mass_particle      = 1
boltzmann_constant = 1
charge_electron    = -10

# Initial Conditions used in initialize:
rho_background         = 1
temperature_background = 1

p1_bulk_background = 0
p2_bulk_background = 0
p3_bulk_background = 0

pert_real = 0.01
pert_imag = 0

k_q1 = 2*np.pi
k_q2 = 0

# Variation of collisional-timescale parameter through phase space:
def tau(q1, q2, p1, p2, p3):
  return(af.constant(0.01, q1.shape[0], q1.shape[1], q1.shape[2], dtype = af.Dtype.f64))