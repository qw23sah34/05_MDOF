"""
@author: Pavlo Shvetsov
e-mail: shvetsov.pavlo@gmail.com

Stores data necessary for numerical integration. 
Contains integration function body.
"""
import numpy as np

class RungeKutta4:
    """
    RK4 numerical integrator class.
    """
    def __init__(self, P, M, C, K, dt):
        self._M_inv = np.linalg.inv(M) # inverse of mass matrix
        self._C = C # damping matrix
        self._K = K # stiffness matrix
        self._P = P # force function
        self._dt = dt # time step
        self._nbodies = np.size(M,1)

    def evaluate(self, y, x, t):
        """ 
        Evaluating the Runge-Kutta-4 step 
        """
        
        # y[:] - velocities of all body masses
        # x[:] - displacement of all body masses
        _x1 = x
        _y1 = y
        _t1 = t
        _F1 = self.F(_x1, _y1, _t1)
        
        _x2 = x + _y1*self._dt/2.0
        _y2 = y + _F1*self._dt/2.0
        _t2 = t + self._dt/2.0
        _F2 = self.F(_x2, _y2, _t2)
        
        _x3 = x + _y2*self._dt/2.0
        _y3 = y + _F2*self._dt/2.0
        _t3 = t + self._dt/2.0
        _F3 = self.F(_x3, _y3, _t3)
        
        _x4 = x + _y3*self._dt
        _y4 = y + _F3*self._dt
        _t4 = t + self._dt
        _F4 = self.F(_x4, _y4, _t4)
        
        x_ip1 = self._dt/6.0 * (_y1 + 2*_y2 + 2*_y3 + _y4)
        y_ip1 = self._dt/6.0 * (_F1 + 2*_F2 + 2*_F3 + _F4)
        return np.transpose(np.array([y_ip1, x_ip1]))
    
    def F(self, x, y, t):
        # Compute the force vector at actual time
        P = np.zeros(self._nbodies)
        for i_body in range(self._nbodies):
            P[i_body] = self._P[i_body].get(t)

        return self._M_inv.dot(P - self._K.dot(x) - self._C.dot(y))