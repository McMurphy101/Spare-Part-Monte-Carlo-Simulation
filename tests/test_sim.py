from simulation import run_simulation
from datetime import date, timedelta

def test_sim_runs():

    # Create Generic PRT Data
    Nomenclature = "Test Part 1"
    PN = "A001"
    prt_MTBF = 850
    prt_RTAT = 250
    OneWayRepairShipTime = 30
    annualOpHrs = 10000
    opHrsSinceLastFailure = 200
    userNMCSrequirement = 5
    monte_carlo_iterations = 500
    prt_BER = 0.02

    model_start = date.today()
    model_end   = date(2030,12,31)


    # Run 
    spares_needed = run_simulation(Nomenclature, PN, prt_MTBF, prt_RTAT, OneWayRepairShipTime, annualOpHrs, opHrsSinceLastFailure, userNMCSrequirement, model_start, model_end, monte_carlo_iterations,prt_BER)

    # Ensure Result is >= 0
    assert spares_needed >= 0