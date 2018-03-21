## morePVs working notes

21/3/18
Issues with Solar Block Tariffs
-------------------------------
- SBTi is not a block tariff. It can be calculated for whole period (year), assuming no demand shifting
- More major issue is that currently tariffs may be calculated dynamically, but bills are still calculated statically. 
ie a tariff rate is allocated for each time step. this is __bad__.
- Need to cal $ dynamically. 
ie for each timestep:
    calc solar rate x allocation (or x load if less)
    calc base rate x residual load
- this also affects quarterly block tariffs, but current approximation (each step is either inside block or outside block)
works better for quarterly period. It is less good for daily period
and bad for instantaneous.
- Maybe this means reworking the whole f***ing model??

 
