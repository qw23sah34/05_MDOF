"""
@author Pavlo Shvetsov
e-mail: shvetsov.pavlo@gmail.com
License: CC0

Description:
    The programm simulates oscillations of multi degree of freedom system (MDOF).
    All necessary data is defined in "input_data.ste" file.

Functionality:
    - Up to 10 mass bodies (if more, the colour of bodies is repeated)
    - Each body can be coupled to all other bodies
    - Each coupling can be either damped or free spring
    - Force can be applied to each body (so far only SIN and COS forces)
    - Plot animation of displacement

Disclaimer: 
    Some features implemented in this programm may be available
    in Python libraries. Since the goal of this programm is not to buid the most 
    efficient and fastest solution to a problem, but to demostrate knowledge and
    awareness of the used techniques, those features are not used here.
"""
import numpy as np
from mod.initialisation import InputData
from mod.rungekutta4 import RungeKutta4
from mod.visualisation import animate_results

def main():
    
    # Control data filename.
    filename = "input_data.ste"

    # Parse input data
    inp_data = InputData(filename)

    # Couple matrices.
    inp_data.couple_bodies(),

    # Allocate result matrix.
     # [:,:,0] - velocity, [:,:,1] - displacement
    Y = np.zeros([inp_data.n_tsteps,inp_data.n_bodies,2], dtype=float)

    # Set initial conditions. Initial displacements are defined relative to 
    # spring tension-free position (which is on body.xloc).
    Y[0,:,0], Y[0,:,1] = inp_data.get_init_cond()
    P_arr = inp_data.get_force_array()

    # Initialise numerical integrator.
    RK4 = RungeKutta4(P_arr, inp_data.M, inp_data.C, inp_data.K, inp_data.t_step)

    # Solve the problem for each time step, starting from initial conditions 
    # at t=0. The equation of motion for a single body M*x'' + C*x' + K*x = F(t)
    # Defining this equation for every single body will result in a system
    # of coupled equations. Mass, damping and stifness matrices have already
    # been coupled. The system is [M](x)'' + [C](x)' + [K](x) = (F(t))
    # with [M], [C], [K] - mass, damping and stifness matrices respectively,
    # (x)'', (x)', (x) - acceleration, velocity and displacement vectors wuth
    # (n_bodies) dimension. After substitution y = x', reforming and appliying
    # forward step numerical integration scheme, one obtain:
    P_dumm = np.zeros([inp_data.n_tsteps, inp_data.n_bodies])
    for i, t in enumerate(inp_data.time):
        if i > 0:
            Y[i,:,:] = Y[i-1,:,:] + RK4.evaluate(Y[i-1,:,0], Y[i-1,:,1], t)
            for ib in range(inp_data.n_bodies):
                P_dumm[i, ib] = RK4._P[ib].get(t)
            
    # Add initial bodies coordinates.
    for i_body, body in enumerate(inp_data.bodies):
        Y[:,i_body,1] = Y[:,i_body,1] + body.xloc

    # Create animation
    animation = animate_results(inp_data, Y[:,:,1])
    animation.save('anim.gif')
    print("The animation is done!")

if __name__ == "__main__":
    main()