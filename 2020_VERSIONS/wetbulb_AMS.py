# Function to calculate wetbulb temperature given pressure, dewpoint, and
# temperature. Uses the psychrometric formula from the American
# Meteorological Society glossary. 
# Tetens's formula is used for vapor pressure calculations.

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from sympy import *

def calc_wetbulb_temp(T,Td,P):

    # Define the expression whose roots we want to find
    # Declare the Tw symbol, required for symbolic toolbox operations
    Tw=Symbol('Tw')

    # Actual vapor pressure is calculated from dewpoint
    eAct = 6.11*10.**((7.5*Td)/(237.3+Td)); 

    if T > 0:
        func = lambda Tw: eAct - ( 6.11*10**((7.5*Tw)/(237.3+Tw))-6.60*10**(-4)*(1+0.00115*Tw)*P*(T-Tw) )
    else:
        func = lambda Tw: eAct - ( 6.11*10**((7.5*Tw)/(237.3+Tw))-5.82*10**(-4)*(1+0.00115*Tw)*P*(T-Tw) )
    
    # Use numerical solver to find roots

    ####### Need to see if this initial guess always works ########
    Tw_initial_guess = 20.
    Tw_solution = fsolve(func, Tw_initial_guess)

    return Tw_solution[0]
