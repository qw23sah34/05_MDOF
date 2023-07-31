"""
@author: Pavlo Shvetsov
e-mail: shvetsov.pavlo@gmail.com

Stores class definitions required for animation. Contains animation main function
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import ConnectionPatch

class AnimatedBodies:
    """
    Stores information for all animated artists.
    """
    # Class variables
    _artist_colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", 
                      "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
    _n_colors = len(_artist_colors)
    _rect_width = 0.15
    _rect_height = 0.01
    _ds_width = 3.0
    _x_offset = -0.5*_rect_width
    _y_offset = -0.5*_rect_height
    # Determines the layering order. Higher order will be displayed over others.
    _m_layer = 100.0
    _con_layer = 50.0
    _ds_layer = 0.0

    def __init__(self, fig, axl, axr, inp_data, Y):
        self._Y = Y
        self._time = inp_data.time
        min_mass = min_c = min_k = 9.0e12
        for body in inp_data.bodies: 
            min_mass = min(min_mass, body.m)
            min_k = min(min_k, body.m)
            min_c = min(min_c, body.m)
        
        # Format every subplot (axes)
        axl.set_xlim([-self._rect_width*1.5, self._rect_width])
        axl.set_ylim([min(self._Y[:,:].min(), 0.0), self._Y[:,:].max()])
        axl.grid()
        axr.set_xlim([0.0, self._time.max()])
        axr.set_ylim([min(self._Y[:,:].min(), 0.0), self._Y[:,:].max()])
        axr.grid()

        self._m_artist = []
        self._ds_artist = []
        self._l_artist = []
        self._con_artist = []
        self._ds_cpl = []
        for i_body, body in enumerate(inp_data.bodies):
            # Initialise an artist for each mass body.
            self._m_artist.append(
                plt.Rectangle((self._x_offset, 0.0), 
                              self._rect_width, self._rect_height,
                              fc=self._artist_colors[i_body%self._n_colors],
                              zorder=(self._m_layer + 0.1*i_body))
            )
            axl.add_patch(self._m_artist[i_body])

            # Initialise an artist for each damped spring body (dspring).
            for cpl in body.coupl:
                self._ds_artist.append(
                    axl.plot([], [], lw=self._ds_width, 
                             c=self._artist_colors[i_body], ls="-",
                             zorder=(self._ds_layer + 0.1*len(self._ds_artist)))[0]
                )
                # self._ds_cpl.append(np.array([i_body, cpl-1]))

            # Initialise mass line artist for right side plot
            self._l_artist.append(
                axr.plot([],[], lw=1, color=self._artist_colors[i_body])[0]
            )

            # Initialise connection artist
            self._con_artist.append(
                ConnectionPatch((0,0), (0,0), 'data', 'data', 
                                axesA=axl, axesB=axr, 
                                color=self._artist_colors[i_body], ls='--', 
                                zorder=(self._con_layer + 0.1*i_body))
            )
            fig.add_artist(self._con_artist[i_body])

        # Create legend for left graph. It is static and not an artist
        axl.legend(self._m_artist, 
                   list(r'$M_{} = {:4.1f}m$'.format(i_body+1, body.m/min_mass) 
                        for i_body, bodies in enumerate(inp_data.bodies)), 
                   title=r'$m = {:4.1f} kg$'.format(min_mass), 
                   loc='lower left'
        )

        # Create time artist for right graph
        self._t_artist = axr.text(0.03, 0.03, '', fontsize=15,
                                  backgroundcolor='white',
                                  transform=axr.transAxes,
                                  zorder=999.0)


    def update(self, i):
        """
        Holds animation function. Here, all artists are updated 
        for each frame, then they are returned.
        """
        # Update all mass bodies artists
        for i_body, body_artist in enumerate(self._m_artist):
            body_artist.set_xy([self._x_offset, self._Y[i,i_body]+self._y_offset])

        # Update all mass lines artists 
        for i_body, line_artist in enumerate(self._l_artist):
            line_artist.set_data(self._time[:i+1], self._Y[:i+1,i_body])

        # Update all connection artists
        for i_body, con in enumerate(self._con_artist):
            con.xy1 = 0.0, self._Y[i,i_body]
            con.xy2 = self._time[i], self._Y[i,i_body]


def animate_results(inp_data, Y):
    """
    Creates and returns animation based on the simulation results and user input
    """
    fig, (ax1, ax2) = plt.subplots(1,2)
    anibodies = AnimatedBodies(fig, ax1, ax2, inp_data, Y)

    # Since we are not using blit option, we do not need to define init_func.
    # Not very efficient, but will do for the sake of code clearness(?). 
    anim = animation.FuncAnimation(fig, anibodies.update, 
                                   frames=inp_data.n_tsteps, interval = 400, 
                                   blit=False, repeat=True)
    return anim