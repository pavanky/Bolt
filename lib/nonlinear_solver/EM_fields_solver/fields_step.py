#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import arrayfire as af

from lib.nonlinear_solver.EM_fields_solver.electrostatic \
    import fft_poisson, compute_electrostatic_fields
from lib.nonlinear_solver.EM_fields_solver.fdtd_explicit \
    import fdtd, fdtd_grid_to_ck_grid
from lib.nonlinear_solver.interpolation_routines import f_interp_p_3d


def fields_step(self, dt):

    # Obtaining the left-bottom corner coordinates
    # (lowest values of the canonical coordinates in the local zone)
    # Additionally, we also obtain the size of the local zone
    ((i_q1_lowest, i_q2_lowest), (N_q1_local,
                                  N_q2_local)) = self._da_fields.getCorners()

    if (self.physical_system.params.fields_solver == 'fft'):
        fft_poisson(self)
        self._communicate_fields()

    elif (self.physical_system.params.fields_solver == 'electrostatic'):
        compute_electrostatic_fields(self)
        self._communicate_fields()

    elif (self.physical_system.params.fields_solver == 'fdtd'):
        # Will returned a flattened array containing the values of
        # J1,2,3 in 2D space:
        self.J1 = self.physical_system.params.charge_electron * \
                  self.compute_moments('mom_p1_bulk')  # (i + 1/2, j + 1/2)
        self.J2 = self.physical_system.params.charge_electron * \
                  self.compute_moments('mom_p2_bulk')  # (i + 1/2, j + 1/2)
        self.J3 = self.physical_system.params.charge_electron * \
                  self.compute_moments('mom_p3_bulk')  # (i + 1/2, j + 1/2)

        # Obtaining the values for current density on the Yee-Grid:
        self.J1 = 0.5 * (self.J1 + af.shift(self.J2, 0, 1))  # (i + 1/2, j)
        self.J2 = 0.5 * (self.J2 + af.shift(self.J2, 1, 0))  # (i, j + 1/2)

        self.J3 = 0.25 * (self.J3 + af.shift(self.J3, 1, 0) +
                                    af.shift(self.J3, 0, 1) +
                                    af.shift(self.J3, 1, 1))  # (i, j)

        # Storing the values for the previous half-time step:
        # We do this since the B values on the CK grid are defined at
        # time t = n. While the B values on the FDTD grid are defined
        # at t = n + 1/2

        fdtd(self, dt)
        fdtd_grid_to_ck_grid(self)

    else:
        raise NotImplementedError('The method specified is \
                                    invalid/not-implemented')

    f_interp_p_3d(self, dt)

    return
