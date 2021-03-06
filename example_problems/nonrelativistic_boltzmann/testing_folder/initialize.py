import arrayfire as af
import numpy as np 

def initialize_f(q1, q2, p1, p2, p3, params):

  m = params.mass_particle
  k = params.boltzmann_constant

  rho_b = params.rho_background
  T_b   = params.temperature_background

  p1_bulk = params.p1_bulk_background
  p2_bulk = params.p2_bulk_background
  p3_bulk = params.p3_bulk_background

  pert_real = params.pert_real
  pert_imag = params.pert_imag

  k_q1 = params.k_q1
  k_q2 = params.k_q2

  # Calculating the perturbed density:
  rho = rho_b + (pert_real * af.cos(k_q1 * q1 + k_q2 * q2) -\
                 pert_imag * af.sin(k_q1 * q1 + k_q2 * q2)
                )

  # Depending on the dimensionality in velocity space, the 
  # distribution function is assigned accordingly:
  if(params.p_dim == 3):
    
    f = rho * (m/(2*np.pi*k*T_b))**(3/2) * \
        af.exp(-m*(p1 - p1_bulk)**2/(2*k*T_b)) * \
        af.exp(-m*(p2 - p2_bulk)**2/(2*k*T_b)) * \
        af.exp(-m*(p3 - p3_bulk)**2/(2*k*T_b))

  elif(params.p_dim == 2):

    f = rho * (m/(2*np.pi*k*T_b)) * \
        af.exp(-m*(p1 - p1_bulk)**2/(2*k*T_b)) * \
        af.exp(-m*(p2 - p2_bulk)**2/(2*k*T_b))

  else:

    f = rho *\
        np.sqrt(m/(2*np.pi*k*T_b)) * \
        af.exp(-m*(p1 - p1_bulk)**2/(2*k*T_b))

  af.eval(f)
  return(f)

# In case of user-defined fields the initial-conditions are provided
# using the functions below. It should be ensured that these satisfy 
# maxwell's constraint equations.

def initialize_E(q1, q2, p1, p2, p3, params):
  # Declare initial conditions for E here
  E1 = 0 * q1[:, :, 0]
  E2 = 0 * q1[:, :, 0]
  E3 = 0 * q1[:, :, 0]

  af.eval(E1, E2, E3)
  return(E1, E2, E3)

def initialize_B(q1, q2, p1, p2, p3, params):
  # Declare initial conditions for B here
  B1 = 0 * q1[:, :, 0]
  B2 = 0 * q1[:, :, 0]
  B3 = 0 * q1[:, :, 0]

  af.eval(B1, B2, B3)
  return(B1, B2, B3)