"""
@author: Pavlo Shvetsov
e-mail: shvetsov.pavlo@gmail.com
"""
from typing import Any
import numpy as np


class MassBody:
    """
    Contains information about mass body, such as:
      - body properties
      - its initial conditions
      - all couplings defined for that body (coupling = spring-damper)
    """
    def __init__(self):
        self._m = 0.0    # [kg] mass
        self._No = 0     # [-] body number
        self._k = 0.0    # [N/m] spring stiffness
        self._zeta = 0.0 # [-] damping ratio
        self._coupl = np.zeros(0, dtype=int)
        self._x0 = 0.0   # [m] initial displacement
        self._v0 = 0.0   # [m/s] initial velocity
        self._P = []     # [N] force function
        self._c = 0.0    # [Ns/m] damping coefficient
        self._xloc = 0.0 # [m] x position, at which spring of the body has no tension


class ForceFunction:
    """
    Contains methods and variables to store the force function. At the end 
    a force function results in time span array and force values array, 
    corresponding to that time span.
    """
    def __init__(self):
        self._P_array = []
        self._time = []

    def set(self, force_def, time, body_no):
        #!shv continue
        self._body_no = body_no

    def __setattr__(self, name, value):
        """
        Check the correctness of force definition dictionary.
        """
        if name != "force_def":
            return
        # Check if force is defined properly
        _ierr = 0
        if "TYPE" in value:
            if value["TYPE"] == "NONE":
                # Since the force is set to be 0 by default, just return
                return
            elif value["TYPE"] == "SIN" or value["TYPE"] == "COS":
                if not "OMEGA" in value: _ierr = 1
                if not "P0" in value: _ierr = 1
                if not "START" in value: 
                    value["START"] = 0.0
                    print("Force start time for force applied to body No.{} "\
                          "was not specified. Setting it to 0".format(self._body_no))
                if not "STOP" in value:
                    value["STOP"] = -1.0
                    print("Force end time for force applied to body No.{} "\
                          "was not specified. Setting it to simulation total "\
                          "time".format(self._body_no))
            elif value["TYPE"] == "RANDOM":
                #!shv to be implemented
                raise ValueError("Random force definition is not implemented yet!")
        else:
            _ierr = 1
        if _ierr > 0:
            raise ValueError("Force function definition for body No. "\
                             "{0} is invalid or incomplete.\n No force "\
                             "will be applied to body No. {0}.".format(self.No))



class InputData:
    """
    Class for storing, parsing and initialising of all necessary data.
    """
    def __init__(self, filename):
        #
        _sim_active = False
        _body_active = False
        _force_active = False
        self._bodies = []

        # First body is always base.
        self._bodies.append(MassBody())
        _force_def = {}
        try:
            _file = open(filename, 'r')
        except FileNotFoundError:
            raise FileNotFoundError("Input data file was not found. Simulation "\
                                    "can not be executed.")
        
        for line in _file.readlines():
            _ix = line.find("**")
            if _ix == 0:
                # The line is a comment, ignore.
                continue
            elif _ix > 0:
                # Delete inline comments.
                line = line[:_ix].strip()
            
            if not line.isspace():
                # Simulation block
                if line.startswith("*SIMULATION"):
                    _sim_active = True
    
                elif _sim_active and line.startswith("TMAX"):
                    self.t_max = float(line.split('=')[1])
    
                elif _sim_active and line.startswith("TSTEP"):
                    self.t_step = float(line.split('=')[1])
    
                elif line.startswith("*ENDSIMULATION"):
                    if self.t_step > 0.0 and self.t_max > 0.0:
                        self.time = np.arange(0.0, self.t_max, self.t_step)
                    else:
                        raise ValueError("Simulation time settings are not defined")
                    _sim_active = False
                
                # Bodies block
                elif line.startswith("*BODY"):
                    _body_active = True
                    _act_body = MassBody()
                    _act_body.No = int(line.split()[1])
    
                elif line.startswith("*ENDBODY"):
                    if (np.size(_act_body.k) != np.size(_act_body.coupl) or \
                        np.size(_act_body.zeta) != np.size(_act_body.coupl)):
                        raise ValueError(
                            "Coupling parameters for body No. {} are incorrect/"\
                            "incomplete. Please specify for each coupling entity "\
                            "its own ZTA or STIFF, even if it is zero."\
                            .format(_act_body.No))
                    _act_body.c = _act_body.zeta*2.0*np.sqrt(_act_body.k*_act_body.m)
                    _body_active = False
                    self._bodies.append(_act_body)
    
                elif _body_active and line.startswith("MASS"):
                    _act_body.m = float(line.split("=")[1])
    
                elif _body_active and line.startswith("STIFF"):
                    _act_body.k = np.zeros(0, dtype=float)
                    for s in line.split("=")[1].split(","):
                        _act_body.k = np.append(_act_body.k, float(s))
    
                elif _body_active and line.startswith("ZTA"):
                    _act_body.zeta = np.zeros(0, dtype=float)
                    for z in line.split("=")[1].split(","):
                        _act_body.zeta = np.append(_act_body.zeta, float(z))
    
                elif _body_active and line.startswith("CPL"):
                    _act_body.coupl = np.zeros(0, dtype=int)
                    for c in line.split("=")[1].split(","):
                        _act_body.coupl = np.append(_act_body.coupl, int(c))
                        if (int(c) == _act_body.No):
                            raise ValueError("Mass body can not be coupled to "\
                                             "itself. Please check the CPL input "\
                                             "for body {}".format(_act_body.No))
                        
                elif _body_active and line.startswith("X0"):
                    _act_body.x0 = float(line.split("=")[1])
    
                elif _body_active and line.startswith("V0"):
                    _act_body.v0 = float(line.split("=")[1])
    
                elif _body_active and line.startswith("XLOC"):
                    _act_body.xloc = float(line.split("=")[1])
                
                # Force block
                elif line.startswith("*FORCE"):
                    _force_active = True

                elif line.startswith("*ENDFORCE"):
                    _act_body.P = ForceFunction()
                    _act_body.P.set(_force_def, self.time, _act_body.No)
                    forceDef = {}
                    forceActive = False
                elif forceActive and line.startswith("TYPE"):
                    forceDef["TYPE"] = line.split("=")[1].strip()
                elif forceActive and line.startswith("OMEGA"):
                    forceDef["OMEGA"] = float(line.split("=")[1])
                elif forceActive and line.startswith("P0"):
                    forceDef["P0"] = float(line.split("=")[1])
                elif forceActive and line.startswith("START"):
                    forceDef["START"] = float(line.split("=")[1])
                    if not (forceDef["START"] >= time[0] and forceDef["START"] <= time[-1]):
                        raise ValueError("Force start time for body No.{} lies "\
                                         "outside simulation time span".format(actBody.No))
                elif forceActive and line.startswith("STOP"):
                    forceDef["STOP"] = float(line.split("=")[1])
                    if not (forceDef["STOP"] >= time[0] and forceDef["STOP"] <= time[-1]):
                        raise ValueError("Force end time for body No.{} lies "\
                                         "outside simulation time span".format(actBody.No))
        _file.close()

    

    def couple_bodies(self):
        pass

    def __getattribute__(self, name):
        raise AttributeError("The attribute {} does not exist",format(name))


