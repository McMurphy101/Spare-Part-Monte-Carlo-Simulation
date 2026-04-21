# -*- coding: utf-8 -*-

# Create Basic Simulation
# Tool Will Run Simple Monte Carlo For Prt Reliability

# Import Library
from datetime import date, timedelta
from statistics import mean
import pandas as pd
import numpy as np

# Create Class for all Sim Functions
class SimulationFunctions:

  # Initialization
  def __init__(self,part_df):
    self.part_df = part_df

  # Create Def for Reliability
  def getMTBF(self,setSeed):
    np.random.seed(setSeed)
    if self.part_df.loc[0,'Part Reliability Type'] == 'exponential':
      newMTBF = np.random.exponential(scale = self.part_df.loc[0,'Part MTBF'])
      return newMTBF

  # Create Def for Checking For Failure
  def checkForPrtFailure(self,OpHrTracker,MTBF):
    if OpHrTracker >= MTBF:
      # Failure Occured
      return True
    else:
      return False

  def move2repair(self,model_date,RepairList,Repairs_Track):
    days2add = self.part_df.loc[0,'Part Shipping Days']*2
    returnDate = model_date + timedelta(days = int(days2add))
    RepairList.append({'PN': self.part_df.loc[0,'Part Number'],'Return Date': returnDate})
    Repairs_Track = Repairs_Track + 1
    return RepairList, Repairs_Track

  def check_and_execute_prtReturn(self,modelDate,RepairList,Inventory_Track):
    for item in RepairList[:]:  # copy to safely modify list
      if modelDate >= item['Return Date']:
        # move part back to inventory
        Inventory_Track = Inventory_Track + 1
        # remove from repair list
        RepairList.remove(item)

    return RepairList, Inventory_Track

def run_simulation(Nomenclature, PN, prt_MTBF, prt_RTAT, OneWayRepairShipTime, annualOpHrs, opHrsSinceLastFailure, userNMCSrequirement, model_start, model_end,monte_carlo_iterations):

  # Consolidate Data for Prt into Dictonary
  prtData = {
      'Part Name': Nomenclature,
      'Part Number': PN,
      'Part MTBF': prt_MTBF,
      'Part Reliability Type': 'exponential',
      'Part RTAT': prt_RTAT,
      'Part Shipping Days': OneWayRepairShipTime
  }

  part_df = pd.DataFrame([prtData])

  # Create Instance of Simulation Class for Part to Model
  simulation = SimulationFunctions(part_df)

  # Create Sim Variables

  # Model Length
  sim_days = model_end - model_start

  # Hour Tracker
  OpHrTracker = 0

  # Create Asset Plan
  # For simplicity assume 1 location & 1 asset
  # Op Hrs - steady state, no mods
  dailyOpHrs  = annualOpHrs/365

  # Initial Conditions
  OpHrTracker = opHrsSinceLastFailure

  setSeed = 1
  Initial_MTBF = simulation.getMTBF(setSeed)
  Init_Spare_Inventory = 0

  Inventory_Track = Init_Spare_Inventory
  Repairs_Track = 0
  RepairList = []

  downTime = 0
  NMCS = 101
  MICAPdayTrack = np.zeros(sim_days.days)
  result_per_MC_run = np.zeros(monte_carlo_iterations)

  # Start Sim
  for i in range(0,monte_carlo_iterations):

    # Reset Variables
    Repairs_Track = 0
    OpHrTracker = opHrsSinceLastFailure
    RepairList = []
    downTime = 0
    NMCS = 101  
    set_seed = 1
    Initial_MTBF = simulation.getMTBF(set_seed)
    Init_Spare_Inventory = 0
    Inventory_Track = Init_Spare_Inventory

    while NMCS > userNMCSrequirement:
      Init_Spare_Inventory = Init_Spare_Inventory +1
      Inventory_Track = Init_Spare_Inventory
      downTime = 0

      for day in range(0,sim_days.days):

        try:
          # Track Model Day
          model_date = model_start + timedelta(days=day)

          # Initialize MTBF
          if day == 0:
            model_MTBF = Initial_MTBF

          # Check to see if any prts are finished repair & returned as spare
          RepairList, Inventory_Track = simulation.check_and_execute_prtReturn(model_date,RepairList,Inventory_Track)
          if Inventory_Track >= 0:
            MICAPdayTrack[day] = 0

          # --- DAILY OPERATIONS OCCUR --- Sum Daily Op Hrs Accrued
          if MICAPdayTrack[day] == 0:
            OpHrTracker = OpHrTracker + dailyOpHrs

          # Check to see if failure occured
          failed = simulation.checkForPrtFailure(OpHrTracker,model_MTBF)

          if failed == True:
            # Send Part in for Repair
            RepairList, Repairs_Track = simulation.move2repair(model_date,RepairList,Repairs_Track)

            # Get New MTBF
            set_seed = i*day
            model_MTBF = simulation.getMTBF(set_seed)
            
            # Reset Hour Tracker
            OpHrTracker = 0

            # Reduce Inventory Tracker
            Inventory_Track = Inventory_Track - 1

            if Inventory_Track < 0: # No Spares Exist On-Site & Asset Down -> Log MICAP
              MICAPdayTrack[day] = 1

          # Keep Logging Donwtime As Long As Neccessary Even if No Failures Occured
          if Inventory_Track < 0:
            downTime = downTime + 24  # log asset being down full day until spare arrives
            MICAPdayTrack[day] = 1

          # Update NMCS While Loop Crit
          if day == (sim_days.days - 1):
            possessedHrs = (sim_days.days - 1)*24
            NMCS = (downTime/possessedHrs)*100

        except Exception as e:
          print(f"\n💥 CRASH at day {day}")
          print(e)
          break

    result_per_MC_run[i] = Init_Spare_Inventory

  final_result =round(mean(result_per_MC_run))
  return final_result