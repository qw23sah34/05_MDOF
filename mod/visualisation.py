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
    _rect_height = 0.02
    _ds_line_width = 3.0
    _x_offset = -0.5*_rect_width
    _y_offset = -0.5*_rect_height

    # Determines the layering order. Higher order will be displayed over others.
    _m_layer = 100.0
    _con_layer = 50.0
    _ds_layer = 0.0

    def __init__(self, fig, axl, axr, inp_data, Y):
        self._full = inp_data.full_animation
        self._ds_body_width = self._rect_width/inp_data.n_ds
        self._Y = Y
        self._time = inp_data.time
        self._t_step = inp_data.t_step
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

        # ---------------------- Initialise left subplot --------------------- #
        self._m_artist = []
        self._ds_artist = []
        self._ds_cpl = []
        self._ds_xpos = []
        for i_body, body in enumerate(inp_data.bodies):
            # Initialise an artist for each mass body.
            self._m_artist.append(
                plt.Rectangle((self._x_offset, 0.0), 
                              self._rect_width, self._rect_height,
                              fc=self._artist_colors[i_body%self._n_colors],
                              zorder=(self._m_layer + 0.1*i_body))
            )
            axl.add_patch(self._m_artist[i_body])
            
            # Damped springs section.
            for cpl in body.coupl:
                # Save couplings. Cpl number begins at 1, so -1 to 
                # conform with python array numeration.
                self._ds_cpl.append([i_body, cpl-1])
                # Define x position of the damped string
                self._ds_xpos.append(-self._rect_width/2.0 
                                     + self._ds_body_width/2.0 
                                     + self._ds_body_width*len(self._ds_xpos))

                # Initialise an artist for each damped spring body (dspring).
                self._ds_artist.append(
                    axl.plot([], [], lw=self._ds_line_width, 
                             c=self._artist_colors[i_body], ls="-",
                             zorder=(self._ds_layer + 0.1*len(self._ds_artist)))[0]
                )

        # Create legend for left graph. It is static and not an artist
        leg = axl.legend(self._m_artist, 
                         list(r'$M_{} = {:4.1f}m$'.format(i_body+1, body.m/min_mass) 
                              for i_body, body in enumerate(inp_data.bodies)), 
                         title=r'$m = {:4.1f} kg$'.format(min_mass), 
                         loc='lower left'
        )
        leg.set_zorder(999)

        # --------------------- Initialise right subplot --------------------- #
        self._l_artist = []
        self._con_artist = []
        for i_body in range(len(inp_data.bodies)):
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

        # Create time artist for right graph
        self._t_artist = axr.text(0.03, 0.03, '', fontsize=15,
                                  backgroundcolor='white',
                                  transform=axr.transAxes,
                                  zorder=999.0)
        
    def get_ds_xy(self, i_ds, i):
        """
        Returns damped spring x and y position for plotting.
        """
        body_nr = self._ds_cpl[i_ds][0]
        y1 = self._Y[i,body_nr]
        coupl_nr = self._ds_cpl[i_ds][1]
        if coupl_nr < 0:
            y2 = 0.0
        else:
            y2 = self._Y[i,coupl_nr]

        if self._full:
            N = 20
            x = np.zeros(N) + self._ds_xpos[i_ds]
            x[7:13] += self._ds_body_width/2.0 * (-1)**np.arange(6)
            y = np.linspace(y1, y2, N)
            return x, y
        else:
            x = self._ds_xpos[i_ds]
            return [x, x], [y1,y2]


    def update(self, i):
        """
        Holds animation function. Here, all artists are updated 
        for each frame, then they are returned.
        """
        # Update all mass bodies artists.
        for i_body, body_artist in enumerate(self._m_artist):
            body_artist.set_xy([self._x_offset, self._Y[i,i_body]+self._y_offset])

        # Update all mass lines artists.
        for i_body, line_artist in enumerate(self._l_artist):
            line_artist.set_data(self._time[:i+1], self._Y[:i+1,i_body])

        # Update all damped spring artists.
        for  i_ds, ds_artist in enumerate(self._ds_artist):
            ds_artist.set_data(self.get_ds_xy(i_ds, i))

        # Update all connection artists.
        for i_body, con in enumerate(self._con_artist):
            con.xy1 = self._rect_width/2.0, self._Y[i,i_body]
            con.xy2 = self._time[i], self._Y[i,i_body]

        # Update time artist
        self._t_artist.set_text("time = %.1fs" % (i*self._t_step))


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