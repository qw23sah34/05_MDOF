"""
@author Pavlo Shvetsov
e-mail: shvetsov.pavlo@gmail.com

Description:
    The programm simulates oscillations of multi degree of freedom system (MDOF).
    All necessary data is defined in "input_data.ste" file.

Functionality:
    - Up to 10 mass bodies (if more, the colour of bodies is repeated)
    - Each body can be coupled to all other bodies (!shv test animation if true)
    - Each coupling can be either damped or free spring
    - Force can be applied to each body (so far only SIN and COS forces)
    - Plot animation of displacement

Disclaimer: 
    Some features implemented in this programm may be available
    in Python libraries. Since the goal of this programm is not to buid the most 
    efficient and fastest solution to a problem, but to demostrate knowledge and
    awareness of the used techniques, those features are not used here.
"""
from mod.initialisation import InputData
def main():
    
    # Control data filename
    filename = "input_data.ste"

    # Parse input data
    inp_data = InputData(filename)

if __name__ == "__main__":
    main()