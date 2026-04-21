import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
from simulation import run_simulation
import time

st.title("Simulation Runner")

# user inputs
Nomenclature          = st.text_input("Enter Part Nomenclature", value="Test Part 1")
PN                    = st.text_input("Enter Part Number", value="A001")

prt_MTBF              = st.number_input("Enter Part MTBF", value=850)
prt_RTAT              = st.number_input("Enter Part RTAT", value=250)
OneWayRepairShipTime  = st.number_input("Enter Part Ship Time (one way)", value=30)
annualOpHrs           = st.number_input("Enter Fleet Annual Operating Hours", value=10000)
opHrsSinceLastFailure = st.number_input("Enter Fleet Operating Hours Since Last Failure", value=200)
userNMCSrequirement   = st.number_input("Enter Maximum Allowable NMCS Percentage", value=5)
monte_carlo_iterations = st.number_input("Enter Number of Monte Carlo Iterations", value=500)

model_start           = st.date_input("Enter Model Start Date", value=date.today())
model_end             = st.date_input("Enter Model End Date", value=date(2030,12,31))



# run button
if st.button("Run Simulation"):
    with st.spinner('Compiling...'):
        spares_needed = run_simulation(Nomenclature, PN, prt_MTBF, prt_RTAT, OneWayRepairShipTime, annualOpHrs, opHrsSinceLastFailure, userNMCSrequirement, model_start, model_end, monte_carlo_iterations)
        st.write(f"Estimated Spares Needed to Meet NMCS Requirement: {spares_needed}")
    st.success('Simulation Complete!')