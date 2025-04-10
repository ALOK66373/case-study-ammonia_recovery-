# case-study-ammonia_recovery-
Advanced ammonia recovery
 This ammonia recovery project is dedicated to understand the mass transfer laws:

Here we are dealing with 3 equations that are : Absorption : Kg(C-H)        Stripping : Kl(C-H)      Membrane Separation :  Pa*C/L

Kg is gas diffusivity coefficient 
Kl is liquid diffusivity coefficient
H is henry law constant that is dependent on equillibrium of gas and liquid phases
Pa permeability for phase separation
C concentration 
L thickness of the gas liquid layed

Here firstly gas containg Ammonia get absorbed by the liquid (generally water or acid) then membrane separation occur in which ammonia from the mixture is separated only gas
phase can move out of the semi permeable membrane.And the rest of ammonia that is left of eith liquid can be separated out by stripping.

here pH plays a very important role like high ph always favours mass transfer.It is derived from henderson hassalbach equation and fraction of ammonia to the whole mixture directly proportional
to pH. pKa here we take ~9.6 that is constant at 25 degree celcius. 

Then we prepare a Random forest ml model to predict the concentration of Ammonia. 

Further i made a GUI with the help of pyQt5  from here future scopes and optimization start.
