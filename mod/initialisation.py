"""
@author: Pavlo Shvetsov
e-mail: shvetsov.pavlo@gmail.com

Initialisation module. Reads, parses and prepares simulation data. 
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
        self.m = 0.0    # [kg] mass
        self.No = 0     # [-] body number
        self.k = 0.0    # [N/m] spring stiffness
        self.zeta = 0.0 # [-] damping ratio
        self.coupl = np.zeros(0, dtype=int)
        self._x0 = 0.0   # [m] initial displacement
        self._v0 = 0.0   # [m/s] initial velocity
        self.P = []     # [N] force function
        self.c = 0.0    # [Ns/m] damping coefficient
        self.xloc = 0.0 # [m] x position, at which spring of the body has no tension


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
        self._body_no = body_no
        self._time = time
        self._force_def = force_def
        self._P_array = np.zeros(len(time), dtype=float)
        # Define force function
        if self._force_def["STOP"] < 0.0:
            _t_stop = time[-1]
        else:
            _t_stop = self._force_def["STOP"]

        _t_start = self._force_def["START"]
        if self._force_def["TYPE"] == "SIN":
            self._P_array = np.where(
                (time>=_t_start) & (time<=_t_stop),
                self._force_def["P0"]*np.sin(self._force_def["OMEGA"]*(time-_t_start)),
                0.0
            )
        elif force_def["TYPE"] == "COS":
            self._P_array = np.where(
                (time>=_t_start) & (time<=_t_stop),
                self._force_def["P0"]*np.cos(self._force_def["OMEGA"]*(time-_t_start)),
                0.0
            )
        elif force_def["TYPE"] == "RANDOM":
            raise NotImplementedError("Random force definition is not implemented yet!")
        return

    def get(self, t):
        return np.interp(t, self._time, self._P_array)
    
    def __setattr__(self, name, value):
        """
        Check the correctness of force definition dictionary.
        """
        super().__setattr__(name, value)
        if name != "_force_def":
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
                else:
                    if not (value["START"] >= self._time[0] and 
                            value["START"] <= self._time[-1]):
                        raise ValueError("Force start time for body No.{} lies "\
                                         "outside simulation time span"\
                                         "".format(self._body_no))
                
                if not "STOP" in value:
                    value["STOP"] = -1.0
                    print("Force end time for force applied to body No.{} "\
                          "was not specified. Setting it to simulation total "\
                          "time".format(self._body_no))
                else:
                    if not (value["STOP"] >= self._time[0] and 
                            value["STOP"] <= self._time[-1]):
                        raise ValueError("Force end time for body No.{} lies "\
                                         "outside simulation time span"\
                                         "".format(self._body_no))
                    
            elif value["TYPE"] == "RANDOM":
                raise NotImplementedError("Random force definition is not "\
                                          "implemented yet!")
        else:
            _ierr = 1
        if _ierr > 0:
            raise ValueError("Force function definition for body No. "\
                             "{0} is invalid or incomplete.\n No force "\
                             "will be applied to body No. {0}.".format(self._body_no))


class InputData:
    """
    Class for storing, parsing and initialising of all necessary data.
    """
    def __init__(self, filename):
        #
        _sim_active = False
        _body_active = False
        _force_active = False
        self.n_bodies = 0
        self.bodies = []

        # First body is always base.
        self.bodies.append(MassBody())
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
                    self._t_max = float(line.split('=')[1])
    
                elif _sim_active and line.startswith("TSTEP"):
                    self.t_step = float(line.split('=')[1])

                elif _sim_active and line.startswith("ANISTYLE"):
                    self.full_animation = bool(line.split('=')[1])
    
                elif line.startswith("*ENDSIMULATION"):
                    if self.t_step > 0.0 and self._t_max > 0.0:
                        self.time = np.arange(0.0, self._t_max, self.t_step)
                        self.n_tsteps = np.size(self.time)
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
                    _act_body.c = _act_body.zeta*2.0*np.sqrt(_act_body.k
                                                             *_act_body.m)
                    _body_active = False
                    self.bodies.append(_act_body)
    
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
                    _act_body._x0 = float(line.split("=")[1])
    
                elif _body_active and line.startswith("V0"):
                    _act_body._v0 = float(line.split("=")[1])
    
                elif _body_active and line.startswith("XLOC"):
                    _act_body.xloc = float(line.split("=")[1])
                
                # Force block
                elif line.startswith("*FORCE"):
                    _force_active = True

                elif line.startswith("*ENDFORCE"):
                    _act_body.P = ForceFunction()
                    _act_body.P.set(_force_def, self.time, _act_body.No)
                    _force_def = {}
                    _force_active = False
                elif _force_active and line.startswith("TYPE"):
                    _force_def["TYPE"] = line.split("=")[1].strip()

                elif _force_active and line.startswith("OMEGA"):
                    _force_def["OMEGA"] = float(line.split("=")[1])

                elif _force_active and line.startswith("P0"):
                    _force_def["P0"] = float(line.split("=")[1])

                elif _force_active and line.startswith("START"):
                    _force_def["START"] = float(line.split("=")[1])
                    
                elif _force_active and line.startswith("STOP"):
                    _force_def["STOP"] = float(line.split("=")[1])
                    
        _file.close()

    def couple_bodies(self):
        """ 
        Couple bodies and calculate coupled mass, 
        stiffness and damping matrices
        """
        _nbodies = len(self.bodies)
        self.M = np.zeros((_nbodies,_nbodies), dtype=float)
        self.C = np.zeros((_nbodies,_nbodies), dtype=float)
        self.K = np.zeros((_nbodies,_nbodies), dtype=float)
    
        # 0 mass_body is the base. Numeration of mass bodies starts at 1.
        self._relations = np.full((_nbodies,_nbodies), False, dtype=bool)
        _relations_C = np.zeros((_nbodies,_nbodies), dtype=float)
        _relations_K = np.zeros((_nbodies,_nbodies), dtype=float)
        self.n_ds = 0
        for i, body in enumerate(self.bodies):
            # _relations[i,k]
            #            ^ - body number
            # _relations[i,k]
            #              ^ - number of bodies coupled with body i
            for i_con, k in enumerate(body.coupl):
                self.n_ds += 1
                self._relations[i,k] = True
                self._relations[k,i] = True
                _relations_C[i,k] = body.c[i_con]
                _relations_C[k,i] = body.c[i_con]
                _relations_K[i,k] = body.k[i_con]
                _relations_K[k,i] = body.k[i_con]
        
        # Loop over all moving bodies
        for i, body in enumerate(self.bodies):
            # Mass matrix can be set up directly. Inertia forces 
            # only affect their own masses.
            self.M[i,i] = body.m
            if not any(self._relations[i,:]):
                raise ValueError("There is no coupling for body {0}."\
                                 "Please check input data".format(body.No))
        
            # Loop over all bodies to determine coupling relations
            for k in range(i, _nbodies):
                if i == k:
                    for i_con, coupled in enumerate(self._relations[i,:]):
                        if coupled:
                            self.C[i,k] = self.C[i,k] + _relations_C[i,i_con]
                            self.K[i,k] = self.K[i,k] + _relations_K[i,i_con]
                else:
                    for i_con, coupled in enumerate(self._relations[i,:]):
                        
                        # ic = 0 is base. Base can not move. Ignore
                        if i_con != 0 and coupled:
                            self.C[i,k] = self.C[i,k] + (-_relations_C[i,i_con])
                            self.K[i,k] = self.K[i,k] + (-_relations_K[i,i_con])
        
        # Delete base from bodies. Double check if the body to 
        # delete is the mass body.
        if self.bodies[0].No == 0:
            self.M = self.M[1:,1:]
            self.C = self.C[1:,1:]
            self.K = self.K[1:,1:]
            del self.bodies[0]
            self.n_bodies = len(self.bodies)
        
        # Mirror the bottom half
        for i in range(np.size(self.C,0)):
            for k in range(i, np.size(self.C,1)):
                if i != k:
                    self.C[k,i] = self.C[i,k]
                    self.K[k,i] = self.K[i,k]

    def get_init_cond(self):
        """
        Return initial conditions for all bodies.
        """
        v_0 = np.zeros(self.n_bodies, dtype=float)
        x_0 = np.zeros(self.n_bodies, dtype=float)
        for i_body, body in enumerate(self.bodies):
            v_0[i_body] = body._v0
            x_0[i_body] = body._x0
        return v_0, x_0
    
    def get_force_array(self):
        """
        Return array with force functions for all bodies
        """
        P_arr = []
        for body in self.bodies:
            P_arr.append(body.P)
        return P_arr

    def __getattr__(self, name):
        raise AttributeError("The attribute {} does not exist".format(name))


