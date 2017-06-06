from cks.evolve import communicate_fields
import arrayfire as af

def fdtd(da, config, E_x, E_y, E_z, B_x, B_y, B_z, J_x, J_y, J_z, dt):
    
  # E's and B's are staggered in time such that
  # B's are defined at (n + 1/2), and E's are defined at n 
  
  # Positions of grid point where field quantities are defined:
  # B_x --> (i, j + 1/2)
  # B_y --> (i + 1/2, j)
  # B_z --> (i + 1/2, j + 1/2)
  
  # E_x --> (i + 1/2, j)
  # E_y --> (i, j + 1/2)
  # E_z --> (i, j)
  
  # J_x --> (i + 1/2, j)
  # J_y --> (i, j + 1/2)
  # J_z --> (i, j)

  N_x = config.N_x
  N_y = config.N_y

  x_start = config.x_start
  x_end   = config.x_end

  y_start = config.y_start
  y_end   = config.y_end

  dx = (x_end - x_start)/(N_x)
  dy = (y_end - y_start)/(N_y)

  # Creating local and global vectors to take care of boundary conditions:
  glob  = da.createGlobalVec()
  local = da.createLocalVec()

  # The communicate function transfers the data from the local vectors to the global
  # vectors, in addition to dealing with the boundary conditions:
  B_x = communicate_fields(da, config, B_x, local, glob)
  B_y = communicate_fields(da, config, B_y, local, glob)
  B_z = communicate_fields(da, config, B_z, local, glob)
  
  E_x = communicate_fields(da, config, E_x, local, glob)
  E_y = communicate_fields(da, config, E_y, local, glob)
  E_z = communicate_fields(da, config, E_z, local, glob)

  E_x +=   (dt/dy) * (B_z - af.shift(B_z, 1, 0)) - J_x * dt
  E_y +=  -(dt/dx) * (B_z - af.shift(B_z, 0, 1)) - J_y * dt
  E_z +=   (dt/dx) * (B_y - af.shift(B_y, 0, 1)) \
         - (dt/dy) * (B_x - af.shift(B_x, 0, 1)) \
         - dt * J_z
          
  # Applying boundary conditions:
  E_x = communicate_fields(da, config, E_x, local, glob)
  E_y = communicate_fields(da, config, E_y, local, glob)
  E_z = communicate_fields(da, config, E_z, local, glob)

  B_x +=  -(dt/dy) * (af.shift(E_z, -1, 0) - E_z)
  B_y +=   (dt/dx) * (af.shift(E_z, 0, -1) - E_z)
  B_z += - (dt/dx) * (af.shift(E_y, 0, -1) - E_y) \
         + (dt/dy) * (af.shift(E_x, -1, 0) - E_x)

  # Applying boundary conditions:
  B_x = communicate_fields(da, config, B_x, local, glob)
  B_y = communicate_fields(da, config, B_y, local, glob)
  B_z = communicate_fields(da, config, B_z, local, glob)

  af.eval(E_x, E_y, E_z, B_x, B_y, B_z)

  # Destroying the vectors since we are done with their usage for the instance:
  glob.destroy()
  local.destroy()

  return(E_x, E_y, E_z, B_x, B_y, B_z)

def fdtd_grid_to_ck_grid(da, config, E_x, E_y, E_z, B_x, B_y, B_z):

  # Creating local and global vectors to take care of boundary conditions:
  glob  = da.createGlobalVec()
  local = da.createLocalVec()

  # Interpolating at the (i + 1/2, j + 1/2) point of the grid to use for the CK solver:    
  E_x = 0.5 * (E_x + af.shift(E_x, -1, 0)) #(i + 1/2, j + 1/2)
  B_x = 0.5 * (B_x + af.shift(B_x, 0, -1)) #(i + 1/2, j + 1/2)

  E_y = 0.5 * (E_y + af.shift(E_y, 0, -1)) #(i + 1/2, j + 1/2)
  B_y = 0.5 * (B_y + af.shift(B_y, -1, 0)) #(i + 1/2, j + 1/2)

  E_z = 0.25 * (
                E_z + af.shift(E_z, 0, -1) + \
                af.shift(E_z, -1, 0) + af.shift(E_z, -1, -1)
               ) #(i + 1/2, j + 1/2)

  # Applying boundary conditions:
  B_x = communicate_fields(da, config, B_x, local, glob)
  B_y = communicate_fields(da, config, B_y, local, glob)
  B_z = communicate_fields(da, config, B_z, local, glob)
  
  E_x = communicate_fields(da, config, E_x, local, glob)
  E_y = communicate_fields(da, config, E_y, local, glob)
  E_z = communicate_fields(da, config, E_z, local, glob)

  af.eval(E_x, E_y, E_z, B_x, B_y, B_z)

  # Destroying the vectors since we are done with their usage for the instance:
  glob.destroy()
  local.destroy()

  return(E_x, E_y, E_z, B_x, B_y, B_z)