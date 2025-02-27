"""
This module contains useful helper functions for generating probes.

"""

import numpy as np

from .probe import Probe
from .probegroup import ProbeGroup
from .utils import combine_probes


def generate_dummy_probe(elec_shapes='circle'):
    """
    Generate a dummy probe with 3 columns and 32 contacts.
    Mainly used for testing and examples.

    Parameters
    ----------
    elec_shapes : str, optional
        Shape of the electrodes, by default 'circle'
        
    Returns
    -------
    probe : Probe
        The generated probe
    """

    if elec_shapes == 'circle':
        contact_shape_params = {'radius': 6}
    elif elec_shapes == 'square':
        contact_shape_params = {'width': 7}
    elif elec_shapes == 'rect':
        contact_shape_params = {'width': 6, 'height': 4.5}

    probe = generate_multi_columns_probe(num_columns=3,
                                         num_contact_per_column=[10, 12, 10],
                                         xpitch=25, ypitch=25, y_shift_per_column=[0, -12.5, 0],
                                         contact_shapes=elec_shapes, contact_shape_params=contact_shape_params)

    probe.annotate(manufacturer='me')
    probe.annotate_contacts(quality=np.ones(32) * 1000.)

    return probe


def generate_dummy_probe_group():
    """
    Generate a ProbeGroup with 2 probes.
    Mainly used for testing and examples.

    Returns
    -------
    probe : Probe
        The generated probe
    """

    probe0 = generate_dummy_probe()
    probe1 = generate_dummy_probe(elec_shapes='rect')
    probe1.move([150, -50])

    # probe group
    probegroup = ProbeGroup()
    probegroup.add_probe(probe0)
    probegroup.add_probe(probe1)

    return probegroup


def generate_tetrode(r=10):
    """
    Generate a tetrode Probe.

    Returns
    -------
    probe : Probe
        The generated probe
    """
    probe = Probe(ndim=2, si_units='um')
    phi = np.arange(0, np.pi * 2, np.pi / 2)[:, None]
    positions = np.hstack([np.cos(phi), np.sin(phi)]) * r
    probe.set_contacts(positions=positions, shapes='circle', shape_params={'radius': 6})
    return probe


def generate_multi_columns_probe(num_columns=3, num_contact_per_column=10,
                                 xpitch=20, ypitch=20, y_shift_per_column=None,
                                 contact_shapes='circle', contact_shape_params={'radius': 6}):
    """Generate a Probe with several columns.

    Parameters
    ----------
    num_columns : int, optional
        Number of columns, by default 3
    num_contact_per_column : int, optional
        Number of contacts per column, by default 10
    xpitch : float, optional
        Pitch in x direction, by default 20
    ypitch : float, optional
        Pitch in y direction, by default 20
    y_shift_per_column : float, optional
        Shift in y direction per column, by default None
    contact_shapes : str, optional
        Shape of the contacts ('circle', 'rect', 'square'), by default 'circle'
    contact_shape_params : dict, optional
        Parameters for the shape, by default {'radius': 6}

    Returns
    -------
    probe : Probe
        The generated probe
    """

    if isinstance(num_contact_per_column, int):
        num_contact_per_column = [num_contact_per_column] * num_columns

    if y_shift_per_column is None:
        y_shift_per_column = [0] * num_columns

    positions = []
    for i in range(num_columns):
        x = np.ones(num_contact_per_column[i]) * xpitch * i
        y = np.arange(num_contact_per_column[i]) * ypitch + y_shift_per_column[i]
        positions.append(np.hstack((x[:, None], y[:, None])))
    positions = np.vstack(positions)

    probe = Probe(ndim=2, si_units='um')
    probe.set_contacts(positions=positions, shapes=contact_shapes,
                       shape_params=contact_shape_params)
    probe.create_auto_shape(probe_type='tip', margin=25)

    return probe


def generate_linear_probe(num_elec=16, ypitch=20,
                          contact_shapes='circle', contact_shape_params={'radius': 6}):
    """Generate a one-column linear probe.

    Parameters
    ----------
    num_elec : int, optional
        Number of electrodes, by default 16
    ypitch : float, optional
        Pitch in y direction, by default 20
    contact_shapes : str, optional
        Shape of the contacts ('circle', 'rect', 'square'), by default 'circle'
    contact_shape_params : dict, optional
        Parameters for the shape, by default {'radius': 6}

    Returns
    -------
    probe : Probe
        The generated probe
    """

    probe = generate_multi_columns_probe(num_columns=1, num_contact_per_column=num_elec,
                                         xpitch=0, ypitch=ypitch, contact_shapes=contact_shapes,
                                         contact_shape_params=contact_shape_params)
    return probe


def generate_multi_shank(num_shank=2, shank_pitch=[150, 0], **kargs):
    """Generate a multi-shank probe.
    Internally, calls generate_multi_columns_probe and combine_probes.

    Parameters
    ----------
    num_shank : int, optional
        Number of shanks, by default 2
    shank_pitch : list, optional
        Distance between shanks, by default [150, 0]

    Returns
    -------
    probe : Probe
        The generated probe
    """

    shank_pitch = np.asarray(shank_pitch)

    probes = []
    for i in range(num_shank):
        probe = generate_multi_columns_probe(**kargs)
        probe.move(shank_pitch * i)
        probes.append(probe)

    multi_shank = combine_probes(probes)

    return multi_shank
