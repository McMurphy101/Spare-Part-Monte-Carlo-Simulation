import pandas as pd
import numpy as np
from datetime import date, timedelta
from simulation import run_simulation
import time

# user inputs
Nomenclature          = "Test Part 1"
PN                    = "A001"
prt_MTBF              = 850
prt_RTAT              = 250
prt_BER               = 0.02
OneWayRepairShipTime  = 30
annualOpHrs           = 10000
opHrsSinceLastFailure = 200
userNMCSrequirement   = 5
monte_carlo_iterations = 500
model_start           = date.today()
model_end             = date(2030,12,31)


# run
spares_needed = run_simulation(Nomenclature, PN, prt_MTBF, prt_RTAT, OneWayRepairShipTime, annualOpHrs, opHrsSinceLastFailure, userNMCSrequirement, model_start, model_end, monte_carlo_iterations,prt_BER)