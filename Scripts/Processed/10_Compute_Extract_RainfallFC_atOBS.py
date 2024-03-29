import sys
import os
from os.path import exists
from datetime import date, timedelta
from calendar import monthrange
import numpy as np
import metview as mv

############################################################################################################################################
# CODE DESCRIPTION
# 10_Compute_Extract_RainfallFC_atOBS.py extracts rainfall realizations from different forecasting systems, at the location of available point rainfall climatologies on a 
# given year.
# Code runtime: Depends on the number of datasets processed, but it is on the order of 2 hour for all datasets.
# Note: this script must be run on the HPC because it is memory demanding.

# DESCRIPTION OF INPUT PARAMETERS
# Year (number, in YYYY format): year to consider.
# SystemFC_list (list of string): list of forecasting systems to consider.
# Acc (number, in hours): rainfall accumulation period.
# MinDays_Perc_list (list of number, from 0 to 1): list of percentages of minimum n. of days over the considered period with valid observations to compute the climatologies.
# NameOBS_list (list of strings): list of the names of the observations to quality check.
# Coeff_Grid2Point_list (list of integer number): list of coefficients used to compare CPC's gridded rainfall values with  STVL's point rainfall observations. 
# Git_repo (string): path of local github repository.
# DirIN_ClimateOBS (string): relative path for the input directory containing the point observational climatologies.
# DirIN_FC (string): relative path for the input directory containing the raw analysis/forecasts.
# DirOUT (string): relative path for the output directory containing the extracted indipendent rainfall realizations.

# INPUT PARAMETERS
Year = int(sys.argv[1])
SystemFC_list = sys.argv[2].split(',')
Acc = 24
MinDays_Perc_list = [0.75]
NameOBS_list = ["08_AlignOBS_CleanSTVL"]
Coeff_Grid2Point_list = [20]
Git_repo = "/ec/vol/ecpoint_dev/mofp/Papers_2_Write/ecPoint_Climate"
DirIN_ClimateOBS = "Data/Compute/09_Climate_OBS"
DirIN_FC = "Data/Raw/FC"
DirOUT = "Data/Compute/10_Extract_RainfallFC_atOBS"
############################################################################################################################################

# Costum functions

##############################################
# Compute independent rainfall realizations from HRES # 
##############################################
def rainfall_HRES(BaseDateS, BaseDateF, Acc, DirIN_ClimateOBS, DirIN_FC, DirOUT):

      # Specific parameters for the considered forecasting system
      BaseTime = 0
      StepS = 0
      StepF = 240
      NumEM = 1

      # Loading the stations for year and seasonal climatologies
      stn_lats_year = np.load(DirIN_ClimateOBS + "/Stn_lats_Year.npy")
      stn_lons_year = np.load(DirIN_ClimateOBS + "/Stn_lons_Year.npy")
      stn_lats_DJF = np.load(DirIN_ClimateOBS + "/Stn_lats_DJF.npy")
      stn_lons_DJF = np.load(DirIN_ClimateOBS + "/Stn_lons_DJF.npy")
      stn_lats_MAM = np.load(DirIN_ClimateOBS + "/Stn_lats_MAM.npy")
      stn_lons_MAM = np.load(DirIN_ClimateOBS + "/Stn_lons_MAM.npy")
      stn_lats_JJA = np.load(DirIN_ClimateOBS + "/Stn_lats_JJA.npy")
      stn_lons_JJA = np.load(DirIN_ClimateOBS + "/Stn_lons_JJA.npy")
      stn_lats_SON = np.load(DirIN_ClimateOBS + "/Stn_lats_SON.npy")
      stn_lons_SON = np.load(DirIN_ClimateOBS + "/Stn_lons_SON.npy")

      # Defining the n. of stations in the year and seasonal climatologies
      NumStn_year = len(stn_lats_year)
      NumStn_DJF = len(stn_lats_DJF)
      NumStn_MAM = len(stn_lats_MAM)
      NumStn_JJA = len(stn_lats_JJA)
      NumStn_SON = len(stn_lats_SON)

      # Defining the n. of total realizations for year and seasonal climatologies
      NumRealizations_Day = int(((StepF - StepS) / Acc) * NumEM)
      NumDays_Year = (BaseDateF - BaseDateS).days + 1
      NumDays_DJF = monthrange(BaseDateS.year, 12)[1] + monthrange(BaseDateS.year, 1)[1] + monthrange(BaseDateS.year, 2)[1]
      NumDays_MAM = monthrange(BaseDateS.year, 3)[1] + monthrange(BaseDateS.year, 4)[1] + monthrange(BaseDateS.year, 5)[1]
      NumDays_JJA = monthrange(BaseDateS.year, 6)[1] + monthrange(BaseDateS.year, 7)[1] + monthrange(BaseDateS.year, 8)[1]
      NumDays_SON = monthrange(BaseDateS.year, 9)[1] + monthrange(BaseDateS.year, 10)[1] + monthrange(BaseDateS.year, 11)[1]
      NumRealizations_Year = int(NumDays_Year * NumRealizations_Day * NumEM)
      NumRealizations_DJF = int(NumDays_DJF * NumRealizations_Day * NumEM)
      NumRealizations_MAM = int(NumDays_MAM * NumRealizations_Day * NumEM)
      NumRealizations_JJA = int(NumDays_JJA * NumRealizations_Day * NumEM)
      NumRealizations_SON = int(NumDays_SON * NumRealizations_Day * NumEM)

      # Initializing the variables that will store the indipendent rainfall realizations
      tp_year = np.float16(np.empty([NumStn_year, NumRealizations_Year]) * np.nan)
      tp_DJF = np.float16(np.empty([NumStn_DJF, NumRealizations_DJF]) * np.nan)
      tp_MAM = np.float16(np.empty([NumStn_MAM, NumRealizations_MAM]) * np.nan)
      tp_JJA = np.float16(np.empty([NumStn_JJA, NumRealizations_JJA]) * np.nan)
      tp_SON = np.float16(np.empty([NumStn_SON, NumRealizations_SON]) * np.nan)

      # Computing the independent rainfall realizations for the year/seasonal climatologies
      print(" - Computing the independent rainfall realizations for the year/seasonal climatologies. Processing " + str(Acc) + "-hourly accumulation period ending on:")
      ind_year = 0
      ind_DJF = 0
      ind_MAM = 0
      ind_JJA = 0
      ind_SON = 0
      
      # Extracting the independent rainfall realizations for year/seasonal climatologies
      BaseDate = BaseDateS
      while BaseDate <= BaseDateF:

            print("     ", BaseDate)
            
            for Step1 in np.arange( StepS, (StepF-Acc+1), Acc ):
                        
                  Step2 = Step1 + Acc
                  DirIN_temp = DirIN_FC + "/" + BaseDate.strftime("%Y%m%d") + f'{BaseTime:02d}'
                  FileIN_1 =  DirIN_temp + "/tp_" + BaseDate.strftime("%Y%m%d") + "_" + f'{BaseTime:02d}' + "_" + f'{Step1:03d}' + ".grib"
                  FileIN_2 =  DirIN_temp + "/tp_" + BaseDate.strftime("%Y%m%d") + "_" + f'{BaseTime:02d}' + "_" + f'{Step2:03d}' + ".grib"

                  if exists(FileIN_1) and exists(FileIN_2):
                        
                        # Reading the forecasts for the considered day
                        tp1 = mv.read(FileIN_1)
                        tp2 = mv.read(FileIN_2)
                        tp = (tp2 - tp1) * 1000
                        
                        # Extracting the independent rainfall realizations for the year climatology
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_year, stn_lons_year)), decimals =1)
                        tp_year[:, ind_year] = tp_obs_temp
                        ind_year += 1
                        
                        # Populating the variables that contains the independent rainfall realizations for the seasonal climatologies
                        if BaseDate.month == 12 or BaseDate.month == 1 or BaseDate.month == 2:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_DJF, stn_lons_DJF)), decimals =1)
                              tp_DJF[:, ind_DJF] = tp_obs_temp
                              ind_DJF += 1
                        elif BaseDate.month == 3 or BaseDate.month == 4 or BaseDate.month == 5:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_MAM, stn_lons_MAM)), decimals =1)
                              tp_MAM[:, ind_MAM] = tp_obs_temp
                              ind_MAM += 1
                        elif BaseDate.month == 6 or BaseDate.month == 7 or BaseDate.month == 8:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_JJA, stn_lons_JJA)), decimals =1)
                              tp_JJA[:, ind_JJA] = tp_obs_temp
                              ind_JJA += 1
                        elif BaseDate.month == 9 or BaseDate.month == 10 or BaseDate.month == 11:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_SON, stn_lons_SON)), decimals =1)
                              tp_SON[:, ind_SON] = tp_obs_temp
                              ind_SON += 1

                  else:

                        print("Forecast not availbale in the database.")
     
            BaseDate += timedelta(days=1)
      
      # Saving the year/seasonal climatologies and their correspondent metadata
      print(" - Saving the year/seasonal rainfall realizations")
      np.save(DirOUT + "/tp_Year_" + str(Year) + ".npy", tp_year)
      np.save(DirOUT + "/tp_DJF_" + str(Year) + ".npy", tp_DJF)
      np.save(DirOUT + "/tp_MAM_" + str(Year) + ".npy", tp_MAM)
      np.save(DirOUT + "/tp_JJA_" + str(Year) + ".npy", tp_JJA)
      np.save(DirOUT + "/tp_SON_" + str(Year) + ".npy", tp_SON)

####################################################
# Compute independent rainfall realizations from Reforecasts  # 
####################################################
def rainfall_REFORECAST(BaseDateS, BaseDateF, Acc, DirIN_ClimateOBS, DirIN_FC, DirOUT):

      # Specific parameters for the considered forecasting system
      BaseTime = 0
      StepS = 0
      StepF = 240
      NumEM = 1

      # Loading the stations for year and seasonal climatologies
      stn_lats_year = np.load(DirIN_ClimateOBS + "/Stn_lats_Year.npy")
      stn_lons_year = np.load(DirIN_ClimateOBS + "/Stn_lons_Year.npy")
      stn_lats_DJF = np.load(DirIN_ClimateOBS + "/Stn_lats_DJF.npy")
      stn_lons_DJF = np.load(DirIN_ClimateOBS + "/Stn_lons_DJF.npy")
      stn_lats_MAM = np.load(DirIN_ClimateOBS + "/Stn_lats_MAM.npy")
      stn_lons_MAM = np.load(DirIN_ClimateOBS + "/Stn_lons_MAM.npy")
      stn_lats_JJA = np.load(DirIN_ClimateOBS + "/Stn_lats_JJA.npy")
      stn_lons_JJA = np.load(DirIN_ClimateOBS + "/Stn_lons_JJA.npy")
      stn_lats_SON = np.load(DirIN_ClimateOBS + "/Stn_lats_SON.npy")
      stn_lons_SON = np.load(DirIN_ClimateOBS + "/Stn_lons_SON.npy")

      # Defining the n. of stations in the year and seasonal climatologies
      NumStn_year = len(stn_lats_year)
      NumStn_DJF = len(stn_lats_DJF)
      NumStn_MAM = len(stn_lats_MAM)
      NumStn_JJA = len(stn_lats_JJA)
      NumStn_SON = len(stn_lats_SON)

      # Defining the n. of total realizations for year and seasonal climatologies
      NumRealizations_Day = int(((StepF - StepS) / Acc) * NumEM)
      NumDays_Year = (BaseDateF - BaseDateS).days + 1
      NumDays_DJF = monthrange(BaseDateS.year, 12)[1] + monthrange(BaseDateS.year, 1)[1] + monthrange(BaseDateS.year, 2)[1]
      NumDays_MAM = monthrange(BaseDateS.year, 3)[1] + monthrange(BaseDateS.year, 4)[1] + monthrange(BaseDateS.year, 5)[1]
      NumDays_JJA = monthrange(BaseDateS.year, 6)[1] + monthrange(BaseDateS.year, 7)[1] + monthrange(BaseDateS.year, 8)[1]
      NumDays_SON = monthrange(BaseDateS.year, 9)[1] + monthrange(BaseDateS.year, 10)[1] + monthrange(BaseDateS.year, 11)[1]
      NumRealizations_Year = int(NumDays_Year * NumRealizations_Day * NumEM)
      NumRealizations_DJF = int(NumDays_DJF * NumRealizations_Day * NumEM)
      NumRealizations_MAM = int(NumDays_MAM * NumRealizations_Day * NumEM)
      NumRealizations_JJA = int(NumDays_JJA * NumRealizations_Day * NumEM)
      NumRealizations_SON = int(NumDays_SON * NumRealizations_Day * NumEM)
      
      # Initializing the variables that will store the indipendent rainfall realizations
      tp_year = np.float16(np.empty([NumStn_year, NumRealizations_Year]) * np.nan)
      tp_DJF = np.float16(np.empty([NumStn_DJF, NumRealizations_DJF]) * np.nan)
      tp_MAM = np.float16(np.empty([NumStn_MAM, NumRealizations_MAM]) * np.nan)
      tp_JJA = np.float16(np.empty([NumStn_JJA, NumRealizations_JJA]) * np.nan)
      tp_SON = np.float16(np.empty([NumStn_SON, NumRealizations_SON]) * np.nan)

      # Computing the independent rainfall realizations for the year/seasonal climatologies
      print(" - Computing the independent rainfall realizations for the year/seasonal climatologies. Processing " + str(Acc) + "-hourly accumulation period ending on:")
      ind_year = 0
      ind_DJF = 0
      ind_MAM = 0
      ind_JJA = 0
      ind_SON = 0
      
      # Extracting the independent rainfall realizations for year/seasonal climatologies
      BaseDate = BaseDateS
      while BaseDate <= BaseDateF:

            print("     ", BaseDate)
            
            for Step1 in np.arange( StepS, (StepF-Acc+1), Acc ):
                        
                  Step2 = Step1 + Acc
                  DirIN_temp = DirIN_FC + "/" + BaseDate.strftime("%Y") + "/" + BaseDate.strftime("%Y%m%d") + f'{BaseTime:02d}'
                  FileIN_1 =  DirIN_temp + "/tp_" + BaseDate.strftime("%Y%m%d") + "_" + f'{BaseTime:02d}' + "_" + f'{Step1:03d}' + ".grib"
                  FileIN_2 =  DirIN_temp + "/tp_" + BaseDate.strftime("%Y%m%d") + "_" + f'{BaseTime:02d}' + "_" + f'{Step2:03d}' + ".grib"

                  if exists(FileIN_1) and exists(FileIN_2):
                        
                        # Reading the forecasts for the considered day
                        tp1 = mv.read(FileIN_1)
                        tp2 = mv.read(FileIN_2)
                        tp = (tp2 - tp1) * 1000
                        
                        # Extracting the independent rainfall realizations for the year climatology
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_year, stn_lons_year)), decimals =1)
                        tp_year[:, ind_year] = tp_obs_temp
                        ind_year += 1
                        
                        # Populating the variables that contains the independent rainfall realizations for the seasonal climatologies
                        if BaseDate.month == 12 or BaseDate.month == 1 or BaseDate.month == 2:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_DJF, stn_lons_DJF)), decimals =1)
                              tp_DJF[:, ind_DJF] = tp_obs_temp
                              ind_DJF += 1
                        elif BaseDate.month == 3 or BaseDate.month == 4 or BaseDate.month == 5:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_MAM, stn_lons_MAM)), decimals =1)
                              tp_MAM[:, ind_MAM] = tp_obs_temp
                              ind_MAM += 1
                        elif BaseDate.month == 6 or BaseDate.month == 7 or BaseDate.month == 8:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_JJA, stn_lons_JJA)), decimals =1)
                              tp_JJA[:, ind_JJA] = tp_obs_temp
                              ind_JJA += 1
                        elif BaseDate.month == 9 or BaseDate.month == 10 or BaseDate.month == 11:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_SON, stn_lons_SON)), decimals =1)
                              tp_SON[:, ind_SON] = tp_obs_temp
                              ind_SON += 1

                  else:

                        print("Forecast not availbale in the database.")
     
            BaseDate += timedelta(days=1)
      
      # Saving the year/seasonal climatologies and their correspondent metadata
      print(" - Saving the year/seasonal rainfall realizations")
      np.save(DirOUT + "/tp_Year_" + str(Year) + ".npy", tp_year)
      np.save(DirOUT + "/tp_DJF_" + str(Year) + ".npy", tp_DJF)
      np.save(DirOUT + "/tp_MAM_" + str(Year) + ".npy", tp_MAM)
      np.save(DirOUT + "/tp_JJA_" + str(Year) + ".npy", tp_JJA)
      np.save(DirOUT + "/tp_SON_" + str(Year) + ".npy", tp_SON)

########################################################
# Compute independent rainfall realizations from short-range ERA5 # 
########################################################
def rainfall_24h_ERA5_SR(BaseDateS, BaseDateF, Acc, DirIN_ClimateOBS, DirIN_FC, DirOUT):

      # Specific parameters for the considered forecasting system
      NumEM = 1
      NumRealizations_Day = 1

      # Loading the stations for year and seasonal climatologies
      stn_lats_year = np.load(DirIN_ClimateOBS + "/Stn_lats_Year.npy")
      stn_lons_year = np.load(DirIN_ClimateOBS + "/Stn_lons_Year.npy")
      stn_lats_DJF = np.load(DirIN_ClimateOBS + "/Stn_lats_DJF.npy")
      stn_lons_DJF = np.load(DirIN_ClimateOBS + "/Stn_lons_DJF.npy")
      stn_lats_MAM = np.load(DirIN_ClimateOBS + "/Stn_lats_MAM.npy")
      stn_lons_MAM = np.load(DirIN_ClimateOBS + "/Stn_lons_MAM.npy")
      stn_lats_JJA = np.load(DirIN_ClimateOBS + "/Stn_lats_JJA.npy")
      stn_lons_JJA = np.load(DirIN_ClimateOBS + "/Stn_lons_JJA.npy")
      stn_lats_SON = np.load(DirIN_ClimateOBS + "/Stn_lats_SON.npy")
      stn_lons_SON = np.load(DirIN_ClimateOBS + "/Stn_lons_SON.npy")

      # Defining the n. of stations in the year and seasonal climatologies
      NumStn_year = len(stn_lats_year)
      NumStn_DJF = len(stn_lats_DJF)
      NumStn_MAM = len(stn_lats_MAM)
      NumStn_JJA = len(stn_lats_JJA)
      NumStn_SON = len(stn_lats_SON)
      
      # Defining the n. of total realizations for year and seasonal climatologies
      NumDays_Year = (BaseDateF - BaseDateS).days + 1
      NumDays_DJF = monthrange(BaseDateS.year, 12)[1] + monthrange(BaseDateS.year, 1)[1] + monthrange(BaseDateS.year, 2)[1]
      NumDays_MAM = monthrange(BaseDateS.year, 3)[1] + monthrange(BaseDateS.year, 4)[1] + monthrange(BaseDateS.year, 5)[1]
      NumDays_JJA = monthrange(BaseDateS.year, 6)[1] + monthrange(BaseDateS.year, 7)[1] + monthrange(BaseDateS.year, 8)[1]
      NumDays_SON = monthrange(BaseDateS.year, 9)[1] + monthrange(BaseDateS.year, 10)[1] + monthrange(BaseDateS.year, 11)[1]
      NumRealizations_Year = int(NumDays_Year * NumRealizations_Day * NumEM)
      NumRealizations_DJF = int(NumDays_DJF * NumRealizations_Day * NumEM)
      NumRealizations_MAM = int(NumDays_MAM * NumRealizations_Day * NumEM)
      NumRealizations_JJA = int(NumDays_JJA * NumRealizations_Day * NumEM)
      NumRealizations_SON = int(NumDays_SON * NumRealizations_Day * NumEM)
      
      # Initializing the variables that will store the indipendent rainfall realizations
      tp_year = np.float16(np.empty([NumStn_year, NumRealizations_Year]) * np.nan)
      tp_DJF = np.float16(np.empty([NumStn_DJF, NumRealizations_DJF]) * np.nan)
      tp_MAM = np.float16(np.empty([NumStn_MAM, NumRealizations_MAM]) * np.nan)
      tp_JJA = np.float16(np.empty([NumStn_JJA, NumRealizations_JJA]) * np.nan)
      tp_SON = np.float16(np.empty([NumStn_SON, NumRealizations_SON]) * np.nan)
      
      # Computing the independent rainfall realizations for the year/seasonal climatologies
      print(" - Computing the independent rainfall realizations for the year/seasonal climatologies. Processing " + str(Acc) + "-hourly accumulation period ending on:")
      ind_year = 0
      ind_DJF = 0
      ind_MAM = 0
      ind_JJA = 0
      ind_SON = 0
      
      # Extracting the independent rainfall realizations for year/seasonal climatologies
      BaseDate = BaseDateS
      while BaseDate <= BaseDateF:
            
            # Reading the forecasts for the considered day
            BaseTime_0 = BaseDate
            BaseTime_1 = BaseDate + timedelta(days=1)
            DirIN_temp0 = DirIN_FC + "/" + BaseTime_0.strftime("%Y") + "/" + BaseTime_0.strftime("%Y%m%d") + "18"
            DirIN_temp1 = DirIN_FC + "/" + BaseTime_1.strftime("%Y") + "/" + BaseTime_1.strftime("%Y%m%d") + "06"
            tp = 0
            
            if exists(DirIN_temp0) and exists(DirIN_temp1): 
                  
                  print("     ", BaseDate) 
                  for Step in range(7,(12+1)):
                        FileIN_0 =  DirIN_temp0 + "/tp_" + BaseTime_0.strftime("%Y%m%d") + "_18_" + f'{Step:03d}' + ".grib"
                        tp = tp + mv.read(FileIN_0)
                  for Step in range(1,(18+1)):
                        FileIN_1 =  DirIN_temp1 + "/tp_" + BaseTime_1.strftime("%Y%m%d") + "_06_" + f'{Step:03d}' + ".grib"
                        tp = tp + mv.read(FileIN_1)
                  tp = tp *1000
                  
                  # Extracting the independent rainfall realizations for the year climatology
                  tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_year, stn_lons_year)), decimals =1)
                  tp_year[:, ind_year] = tp_obs_temp
                  ind_year += 1
                              
                  # Populating the variables that contains the independent rainfall realizations for the seasonal climatologies
                  if BaseDate.month == 12 or BaseDate.month == 1 or BaseDate.month == 2:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_DJF, stn_lons_DJF)), decimals =1)
                        tp_DJF[:, ind_DJF] = tp_obs_temp
                        ind_DJF += 1
                  elif BaseDate.month == 3 or BaseDate.month == 4 or BaseDate.month == 5:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_MAM, stn_lons_MAM)), decimals =1)
                        tp_MAM[:, ind_MAM] = tp_obs_temp
                        ind_MAM += 1
                  elif BaseDate.month == 6 or BaseDate.month == 7 or BaseDate.month == 8:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_JJA, stn_lons_JJA)), decimals =1)
                        tp_JJA[:, ind_JJA] = tp_obs_temp
                        ind_JJA += 1
                  elif BaseDate.month == 9 or BaseDate.month == 10 or BaseDate.month == 11:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_SON, stn_lons_SON)), decimals =1)
                        tp_SON[:, ind_SON] = tp_obs_temp
                        ind_SON += 1
            
            else:

                  print("Forecast not availbale in the database.")

            BaseDate += timedelta(days=1)

      # Saving the year/seasonal climatologies and their correspondent metadata
      print(" - Saving the year/seasonal rainfall realizations")
      np.save(DirOUT + "/tp_Year_" + str(Year) + ".npy", tp_year)
      np.save(DirOUT + "/tp_DJF_" + str(Year) + ".npy", tp_DJF)
      np.save(DirOUT + "/tp_MAM_" + str(Year) + ".npy", tp_MAM)
      np.save(DirOUT + "/tp_JJA_" + str(Year) + ".npy", tp_JJA)
      np.save(DirOUT + "/tp_SON_" + str(Year) + ".npy", tp_SON)

#############################################################
# Compute independent rainfall realizations from short-range ERA5_EDA  # 
#############################################################
def rainfall_24h_ERA5_EDA_SR(BaseDateS, BaseDateF, Acc, DirIN_ClimateOBS, DirIN_FC, DirOUT):

      # Specific parameters for the considered forecasting system
      NumEM = 10
      NumRealizations_Day = 1

      # Loading the stations for year and seasonal climatologies
      stn_lats_year = np.load(DirIN_ClimateOBS + "/Stn_lats_Year.npy")
      stn_lons_year = np.load(DirIN_ClimateOBS + "/Stn_lons_Year.npy")
      stn_lats_DJF = np.load(DirIN_ClimateOBS + "/Stn_lats_DJF.npy")
      stn_lons_DJF = np.load(DirIN_ClimateOBS + "/Stn_lons_DJF.npy")
      stn_lats_MAM = np.load(DirIN_ClimateOBS + "/Stn_lats_MAM.npy")
      stn_lons_MAM = np.load(DirIN_ClimateOBS + "/Stn_lons_MAM.npy")
      stn_lats_JJA = np.load(DirIN_ClimateOBS + "/Stn_lats_JJA.npy")
      stn_lons_JJA = np.load(DirIN_ClimateOBS + "/Stn_lons_JJA.npy")
      stn_lats_SON = np.load(DirIN_ClimateOBS + "/Stn_lats_SON.npy")
      stn_lons_SON = np.load(DirIN_ClimateOBS + "/Stn_lons_SON.npy")
      
      # Defining the n. of stations in the year and seasonal climatologies
      NumStn_year = len(stn_lats_year)
      NumStn_DJF = len(stn_lats_DJF)
      NumStn_MAM = len(stn_lats_MAM)
      NumStn_JJA = len(stn_lats_JJA)
      NumStn_SON = len(stn_lats_SON)

      # Defining the n. of total realizations for year and seasonal climatologies
      NumDays_Year = (BaseDateF - BaseDateS).days + 1
      NumDays_DJF = monthrange(BaseDateS.year, 12)[1] + monthrange(BaseDateS.year, 1)[1] + monthrange(BaseDateS.year, 2)[1]
      NumDays_MAM = monthrange(BaseDateS.year, 3)[1] + monthrange(BaseDateS.year, 4)[1] + monthrange(BaseDateS.year, 5)[1]
      NumDays_JJA = monthrange(BaseDateS.year, 6)[1] + monthrange(BaseDateS.year, 7)[1] + monthrange(BaseDateS.year, 8)[1]
      NumDays_SON = monthrange(BaseDateS.year, 9)[1] + monthrange(BaseDateS.year, 10)[1] + monthrange(BaseDateS.year, 11)[1]
      NumRealizations_Year = int(NumDays_Year * NumRealizations_Day * NumEM)
      NumRealizations_DJF = int(NumDays_DJF * NumRealizations_Day * NumEM)
      NumRealizations_MAM = int(NumDays_MAM * NumRealizations_Day * NumEM)
      NumRealizations_JJA = int(NumDays_JJA * NumRealizations_Day * NumEM)
      NumRealizations_SON = int(NumDays_SON * NumRealizations_Day * NumEM)
      
      # Initializing the variables that will store the indipendent rainfall realizations
      tp_year = np.float16(np.empty([NumStn_year, NumRealizations_Year]) * np.nan)
      tp_DJF = np.float16(np.empty([NumStn_DJF, NumRealizations_DJF]) * np.nan)
      tp_MAM = np.float16(np.empty([NumStn_MAM, NumRealizations_MAM]) * np.nan)
      tp_JJA = np.float16(np.empty([NumStn_JJA, NumRealizations_JJA]) * np.nan)
      tp_SON = np.float16(np.empty([NumStn_SON, NumRealizations_SON]) * np.nan)
      
      # Computing the independent rainfall realizations for the year/seasonal climatologies
      print(" - Computing the independent rainfall realizations for the year/seasonal climatologies. Processing " + str(Acc) + "-hourly accumulation period ending on:")
      ind1_year = 0
      ind2_year = ind1_year + (NumRealizations_Day * NumEM)
      ind1_DJF = 0
      ind2_DJF = ind1_DJF + (NumRealizations_Day * NumEM)
      ind1_MAM = 0
      ind2_MAM = ind1_MAM + (NumRealizations_Day * NumEM)
      ind1_JJA = 0
      ind2_JJA = ind1_JJA + (NumRealizations_Day * NumEM)
      ind1_SON = 0
      ind2_SON = ind1_SON + (NumRealizations_Day * NumEM)
      
      # Extracting the independent rainfall realizations for year/seasonal climatologies
      BaseDate = BaseDateS
      while BaseDate <= BaseDateF:
            
            # Reading the forecasts for the considered day
            BaseTime_0 = BaseDate
            BaseTime_1 = BaseDate + timedelta(days = 1)
            DirIN_temp0 = DirIN_FC + "/" + BaseTime_0.strftime("%Y") + "/" + BaseTime_0.strftime("%Y%m%d") + "18"
            DirIN_temp1 = DirIN_FC + "/" + BaseTime_1.strftime("%Y") + "/" + BaseTime_1.strftime("%Y%m%d") + "06"
            tp = 0
            
            if exists(DirIN_temp0) and exists(DirIN_temp1): 
                  
                  print("     ", BaseDate) 
                  for Step in range(9, (12+1), 3):
                        FileIN_0 =  DirIN_temp0 + "/tp_" + BaseTime_0.strftime("%Y%m%d") + "_18_" + f'{Step:03d}' + ".grib"
                        tp = tp + mv.read(FileIN_0)
                  for Step in range(3,(18+1),3):
                        FileIN_1 =  DirIN_temp1 + "/tp_" + BaseTime_1.strftime("%Y%m%d") + "_06_" + f'{Step:03d}' + ".grib"
                        tp = tp + mv.read(FileIN_1)
                  tp = tp *1000

                  # Extracting the independent rainfall realizations for the year climatology
                  tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_year, stn_lons_year)), decimals =1).T
                  tp_year[:, ind1_year:ind2_year] = tp_obs_temp
                  ind1_year = ind2_year
                  ind2_year = ind1_year + NumEM
                              
                  # Populating the variables that contains the independent rainfall realizations for the seasonal climatologies
                  if BaseDate.month == 12 or BaseDate.month == 1 or BaseDate.month == 2:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_DJF, stn_lons_DJF)), decimals =1).T
                        tp_DJF[:, ind1_DJF:ind2_DJF] = tp_obs_temp
                        ind1_DJF = ind2_DJF
                        ind2_DJF = ind1_DJF + NumEM
                  elif BaseDate.month == 3 or BaseDate.month == 4 or BaseDate.month == 5:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_MAM, stn_lons_MAM)), decimals =1).T
                        tp_MAM[:, ind1_MAM:ind2_MAM] = tp_obs_temp
                        ind1_MAM = ind2_MAM
                        ind2_MAM = ind1_MAM + NumEM
                  elif BaseDate.month == 6 or BaseDate.month == 7 or BaseDate.month == 8:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_JJA, stn_lons_JJA)), decimals =1).T
                        tp_JJA[:, ind1_JJA:ind2_JJA] = tp_obs_temp
                        ind1_JJA = ind2_JJA
                        ind2_JJA = ind1_JJA + NumEM
                  elif BaseDate.month == 9 or BaseDate.month == 10 or BaseDate.month == 11:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_SON, stn_lons_SON)), decimals =1).T
                        tp_SON[:, ind1_SON:ind2_SON] = tp_obs_temp
                        ind1_SON = ind2_SON
                        ind2_SON = ind1_SON + NumEM

            else:

                  print("Forecast not availbale in the database.")

            BaseDate += timedelta(days=1)

      # Saving the year/seasonal climatologies and their correspondent metadata
      print(" - Saving the year/seasonal rainfall realizations")
      np.save(DirOUT + "/tp_Year_" + str(Year) + ".npy", tp_year)
      np.save(DirOUT + "/tp_DJF_" + str(Year) + ".npy", tp_DJF)
      np.save(DirOUT + "/tp_MAM_" + str(Year) + ".npy", tp_MAM)
      np.save(DirOUT + "/tp_JJA_" + str(Year) + ".npy", tp_JJA)
      np.save(DirOUT + "/tp_SON_" + str(Year) + ".npy", tp_SON)

#######################################################
# Compute independent rainfall realizations from long-range ERA5 # 
#######################################################
def rainfall_ERA5_LR(BaseDateS, BaseDateF, Acc, DirIN_ClimateOBS, DirIN_FC, DirOUT):

      # Specific parameters for the considered forecasting system
      BaseTime = 0
      StepS = 0
      StepF = 240
      NumEM = 1

      # Loading the stations for year and seasonal climatologies
      stn_lats_year = np.load(DirIN_ClimateOBS + "/Stn_lats_Year.npy")
      stn_lons_year = np.load(DirIN_ClimateOBS + "/Stn_lons_Year.npy")
      stn_lats_DJF = np.load(DirIN_ClimateOBS + "/Stn_lats_DJF.npy")
      stn_lons_DJF = np.load(DirIN_ClimateOBS + "/Stn_lons_DJF.npy")
      stn_lats_MAM = np.load(DirIN_ClimateOBS + "/Stn_lats_MAM.npy")
      stn_lons_MAM = np.load(DirIN_ClimateOBS + "/Stn_lons_MAM.npy")
      stn_lats_JJA = np.load(DirIN_ClimateOBS + "/Stn_lats_JJA.npy")
      stn_lons_JJA = np.load(DirIN_ClimateOBS + "/Stn_lons_JJA.npy")
      stn_lats_SON = np.load(DirIN_ClimateOBS + "/Stn_lats_SON.npy")
      stn_lons_SON = np.load(DirIN_ClimateOBS + "/Stn_lons_SON.npy")

      # Defining the n. of stations in the year and seasonal climatologies
      NumStn_year = len(stn_lats_year)
      NumStn_DJF = len(stn_lats_DJF)
      NumStn_MAM = len(stn_lats_MAM)
      NumStn_JJA = len(stn_lats_JJA)
      NumStn_SON = len(stn_lats_SON)

      # Defining the n. of total realizations for year and seasonal climatologies
      NumRealizations_Day = int(((StepF - StepS) / Acc) * NumEM)
      NumDays_Year = (BaseDateF - BaseDateS).days + 1
      NumDays_DJF = monthrange(BaseDateS.year, 12)[1] + monthrange(BaseDateS.year, 1)[1] + monthrange(BaseDateS.year, 2)[1]
      NumDays_MAM = monthrange(BaseDateS.year, 3)[1] + monthrange(BaseDateS.year, 4)[1] + monthrange(BaseDateS.year, 5)[1]
      NumDays_JJA = monthrange(BaseDateS.year, 6)[1] + monthrange(BaseDateS.year, 7)[1] + monthrange(BaseDateS.year, 8)[1]
      NumDays_SON = monthrange(BaseDateS.year, 9)[1] + monthrange(BaseDateS.year, 10)[1] + monthrange(BaseDateS.year, 11)[1]
      NumRealizations_Year = int(NumDays_Year * NumRealizations_Day * NumEM)
      NumRealizations_DJF = int(NumDays_DJF * NumRealizations_Day * NumEM)
      NumRealizations_MAM = int(NumDays_MAM * NumRealizations_Day * NumEM)
      NumRealizations_JJA = int(NumDays_JJA * NumRealizations_Day * NumEM)
      NumRealizations_SON = int(NumDays_SON * NumRealizations_Day * NumEM)
      
      # Initializing the variables that will store the indipendent rainfall realizations
      tp_year = np.float16(np.empty([NumStn_year, NumRealizations_Year]) * np.nan)
      tp_DJF = np.float16(np.empty([NumStn_DJF, NumRealizations_DJF]) * np.nan)
      tp_MAM = np.float16(np.empty([NumStn_MAM, NumRealizations_MAM]) * np.nan)
      tp_JJA = np.float16(np.empty([NumStn_JJA, NumRealizations_JJA]) * np.nan)
      tp_SON = np.float16(np.empty([NumStn_SON, NumRealizations_SON]) * np.nan)

      # Computing the independent rainfall realizations for the year/seasonal climatologies
      print(" - Computing the independent rainfall realizations for the year/seasonal climatologies. Processing " + str(Acc) + "-hourly accumulation period ending on:")
      ind_year = 0
      ind_DJF = 0
      ind_MAM = 0
      ind_JJA = 0
      ind_SON = 0
      
      BaseDate = BaseDateS
      while BaseDate <= BaseDateF:

            print("     ", BaseDate)
            
            for Step1 in np.arange( StepS, (StepF-Acc+1), Acc ):
                        
                  Step2 = Step1 + Acc
                  DirIN_temp = DirIN_FC + "/" + BaseDate.strftime("%Y")  + "/" + BaseDate.strftime("%Y%m%d") + f'{BaseTime:02d}'
                  FileIN_1 =  DirIN_temp + "/tp_" + BaseDate.strftime("%Y%m%d") + "_" + f'{BaseTime:02d}' + "_" + f'{Step1:03d}' + ".grib"
                  FileIN_2 =  DirIN_temp + "/tp_" + BaseDate.strftime("%Y%m%d") + "_" + f'{BaseTime:02d}' + "_" + f'{Step2:03d}' + ".grib"

                  if exists(FileIN_1) and exists(FileIN_2):
                        
                        # Reading the forecasts for the considered day
                        tp1 = mv.read(FileIN_1)
                        tp2 = mv.read(FileIN_2)
                        tp = (tp2 - tp1) * 1000
                        
                        # Extracting the independent rainfall realizations for the year climatology
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_year, stn_lons_year)), decimals =1)
                        tp_year[:, ind_year] = tp_obs_temp
                        ind_year += 1
                        
                        # Populating the variables that contains the independent rainfall realizations for the seasonal climatologies
                        if BaseDate.month == 12 or BaseDate.month == 1 or BaseDate.month == 2:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_DJF, stn_lons_DJF)), decimals =1)
                              tp_DJF[:, ind_DJF] = tp_obs_temp
                              ind_DJF += 1
                        elif BaseDate.month == 3 or BaseDate.month == 4 or BaseDate.month == 5:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_MAM, stn_lons_MAM)), decimals =1)
                              tp_MAM[:, ind_MAM] = tp_obs_temp
                              ind_MAM += 1
                        elif BaseDate.month == 6 or BaseDate.month == 7 or BaseDate.month == 8:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_JJA, stn_lons_JJA)), decimals =1)
                              tp_JJA[:, ind_JJA] = tp_obs_temp
                              ind_JJA += 1
                        elif BaseDate.month == 9 or BaseDate.month == 10 or BaseDate.month == 11:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_SON, stn_lons_SON)), decimals =1)
                              tp_SON[:, ind_SON] = tp_obs_temp
                              ind_SON += 1

                  else:

                        print("Forecast not availbale in the database.")
      
            BaseDate += timedelta(days=1)

      # Saving the year/seasonal climatologies and their correspondent metadata
      print(" - Saving the year/seasonal rainfall realizations")
      np.save(DirOUT + "/tp_Year_" + str(Year) + ".npy", tp_year)
      np.save(DirOUT + "/tp_DJF_" + str(Year) + ".npy", tp_DJF)
      np.save(DirOUT + "/tp_MAM_" + str(Year) + ".npy", tp_MAM)
      np.save(DirOUT + "/tp_JJA_" + str(Year) + ".npy", tp_JJA)
      np.save(DirOUT + "/tp_SON_" + str(Year) + ".npy", tp_SON)

############################################################
# Compute independent rainfall realizations from long-range ERA5_EDA  # 
############################################################
def rainfall_ERA5_EDA_LR(BaseDateS, BaseDateF, Acc, DirIN_ClimateOBS, DirIN_FC, DirOUT):

      # Specific parameters for the considered forecasting system
      BaseTime = 0
      StepS = 0
      StepF = 240
      NumEM = 1

      # Loading the stations for year and seasonal climatologies
      stn_lats_year = np.load(DirIN_ClimateOBS + "/Stn_lats_Year.npy")
      stn_lons_year = np.load(DirIN_ClimateOBS + "/Stn_lons_Year.npy")
      stn_lats_DJF = np.load(DirIN_ClimateOBS + "/Stn_lats_DJF.npy")
      stn_lons_DJF = np.load(DirIN_ClimateOBS + "/Stn_lons_DJF.npy")
      stn_lats_MAM = np.load(DirIN_ClimateOBS + "/Stn_lats_MAM.npy")
      stn_lons_MAM = np.load(DirIN_ClimateOBS + "/Stn_lons_MAM.npy")
      stn_lats_JJA = np.load(DirIN_ClimateOBS + "/Stn_lats_JJA.npy")
      stn_lons_JJA = np.load(DirIN_ClimateOBS + "/Stn_lons_JJA.npy")
      stn_lats_SON = np.load(DirIN_ClimateOBS + "/Stn_lats_SON.npy")
      stn_lons_SON = np.load(DirIN_ClimateOBS + "/Stn_lons_SON.npy")

      # Defining the n. of stations in the year and seasonal climatologies
      NumStn_year = len(stn_lats_year)
      NumStn_DJF = len(stn_lats_DJF)
      NumStn_MAM = len(stn_lats_MAM)
      NumStn_JJA = len(stn_lats_JJA)
      NumStn_SON = len(stn_lats_SON)

      # Defining the n. of total realizations for year and seasonal climatologies
      NumRealizations_Day = int(((StepF - StepS) / Acc) * NumEM)
      NumDays_Year = (BaseDateF - BaseDateS).days + 1
      NumDays_DJF = monthrange(BaseDateS.year, 12)[1] + monthrange(BaseDateS.year, 1)[1] + monthrange(BaseDateS.year, 2)[1]
      NumDays_MAM = monthrange(BaseDateS.year, 3)[1] + monthrange(BaseDateS.year, 4)[1] + monthrange(BaseDateS.year, 5)[1]
      NumDays_JJA = monthrange(BaseDateS.year, 6)[1] + monthrange(BaseDateS.year, 7)[1] + monthrange(BaseDateS.year, 8)[1]
      NumDays_SON = monthrange(BaseDateS.year, 9)[1] + monthrange(BaseDateS.year, 10)[1] + monthrange(BaseDateS.year, 11)[1]
      NumRealizations_Year = int(NumDays_Year * NumRealizations_Day * NumEM)
      NumRealizations_DJF = int(NumDays_DJF * NumRealizations_Day * NumEM)
      NumRealizations_MAM = int(NumDays_MAM * NumRealizations_Day * NumEM)
      NumRealizations_JJA = int(NumDays_JJA * NumRealizations_Day * NumEM)
      NumRealizations_SON = int(NumDays_SON * NumRealizations_Day * NumEM)
      
      # Initializing the variables that will store the indipendent rainfall realizations
      tp_year = np.float16(np.empty([NumStn_year, NumRealizations_Year]) * np.nan)
      tp_DJF = np.float16(np.empty([NumStn_DJF, NumRealizations_DJF]) * np.nan)
      tp_MAM = np.float16(np.empty([NumStn_MAM, NumRealizations_MAM]) * np.nan)
      tp_JJA = np.float16(np.empty([NumStn_JJA, NumRealizations_JJA]) * np.nan)
      tp_SON = np.float16(np.empty([NumStn_SON, NumRealizations_SON]) * np.nan)

      # Computing the independent rainfall realizations for the year/seasonal climatologies
      print(" - Computing the independent rainfall realizations for the year/seasonal climatologies. Processing " + str(Acc) + "-hourly accumulation period ending on:")
      ind_year = 0
      ind_DJF = 0
      ind_MAM = 0
      ind_JJA = 0
      ind_SON = 0
      
      BaseDate = BaseDateS
      while BaseDate <= BaseDateF:

            print("     ", BaseDate)
            
            for Step1 in np.arange( StepS, (StepF-Acc+1), Acc ):
                        
                  Step2 = Step1 + Acc
                  DirIN_temp = DirIN_FC + "/" + BaseDate.strftime("%Y")  + "/" + BaseDate.strftime("%Y%m%d") + f'{BaseTime:02d}'
                  FileIN_1 =  DirIN_temp + "/tp_" + BaseDate.strftime("%Y%m%d") + "_" + f'{BaseTime:02d}' + "_" + f'{Step1:03d}' + ".grib"
                  FileIN_2 =  DirIN_temp + "/tp_" + BaseDate.strftime("%Y%m%d") + "_" + f'{BaseTime:02d}' + "_" + f'{Step2:03d}' + ".grib"

                  if exists(FileIN_1) and exists(FileIN_2):
                        
                        # Reading the forecasts for the considered day
                        tp1 = mv.read(FileIN_1)
                        tp2 = mv.read(FileIN_2)
                        tp = (tp2 - tp1) * 1000
                        
                        # Extracting the independent rainfall realizations for the year climatology
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_year, stn_lons_year)), decimals =1)
                        tp_year[:, ind_year] = tp_obs_temp
                        ind_year += 1
                        
                        # Populating the variables that contains the independent rainfall realizations for the seasonal climatologies
                        if BaseDate.month == 12 or BaseDate.month == 1 or BaseDate.month == 2:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_DJF, stn_lons_DJF)), decimals =1)
                              tp_DJF[:, ind_DJF] = tp_obs_temp
                              ind_DJF += 1
                        elif BaseDate.month == 3 or BaseDate.month == 4 or BaseDate.month == 5:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_MAM, stn_lons_MAM)), decimals =1)
                              tp_MAM[:, ind_MAM] = tp_obs_temp
                              ind_MAM += 1
                        elif BaseDate.month == 6 or BaseDate.month == 7 or BaseDate.month == 8:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_JJA, stn_lons_JJA)), decimals =1)
                              tp_JJA[:, ind_JJA] = tp_obs_temp
                              ind_JJA += 1
                        elif BaseDate.month == 9 or BaseDate.month == 10 or BaseDate.month == 11:
                              tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_SON, stn_lons_SON)), decimals =1)
                              tp_SON[:, ind_SON] = tp_obs_temp
                              ind_SON += 1

                  else:

                        print("Forecast not availbale in the database.")
      
            BaseDate += timedelta(days=1)

      # Saving the year/seasonal climatologies and their correspondent metadata
      print(" - Saving the year/seasonal rainfall realizations")
      np.save(DirOUT + "/tp_Year_" + str(Year) + ".npy", tp_year)
      np.save(DirOUT + "/tp_DJF_" + str(Year) + ".npy", tp_DJF)
      np.save(DirOUT + "/tp_MAM_" + str(Year) + ".npy", tp_MAM)
      np.save(DirOUT + "/tp_JJA_" + str(Year) + ".npy", tp_JJA)
      np.save(DirOUT + "/tp_SON_" + str(Year) + ".npy", tp_SON)

############################################################################
# Compute independent rainfall realizations from ERA5_ecPoint (grid-scale, bias corrected)   # 
############################################################################
def rainfall_24h_ERA5_ecPoint_gridBC(BaseDateS, BaseDateF, Acc, DirIN_ClimateOBS, DirIN_FC, DirOUT):

      # Specific parameters for the considered forecasting system
      ecPoint_Dataset = DirIN_FC.split("/")[-1]
      NumEM = 1
      NumRealizations_Day = 1
      
      # Loading the stations for year and seasonal climatologies
      stn_lats_year = np.load(DirIN_ClimateOBS + "/Stn_lats_Year.npy")
      stn_lons_year = np.load(DirIN_ClimateOBS + "/Stn_lons_Year.npy")
      stn_lats_DJF = np.load(DirIN_ClimateOBS + "/Stn_lats_DJF.npy")
      stn_lons_DJF = np.load(DirIN_ClimateOBS + "/Stn_lons_DJF.npy")
      stn_lats_MAM = np.load(DirIN_ClimateOBS + "/Stn_lats_MAM.npy")
      stn_lons_MAM = np.load(DirIN_ClimateOBS + "/Stn_lons_MAM.npy")
      stn_lats_JJA = np.load(DirIN_ClimateOBS + "/Stn_lats_JJA.npy")
      stn_lons_JJA = np.load(DirIN_ClimateOBS + "/Stn_lons_JJA.npy")
      stn_lats_SON = np.load(DirIN_ClimateOBS + "/Stn_lats_SON.npy")
      stn_lons_SON = np.load(DirIN_ClimateOBS + "/Stn_lons_SON.npy")

      # Defining the n. of stations in the year and seasonal climatologies
      NumStn_year = len(stn_lats_year)
      NumStn_DJF = len(stn_lats_DJF)
      NumStn_MAM = len(stn_lats_MAM)
      NumStn_JJA = len(stn_lats_JJA)
      NumStn_SON = len(stn_lats_SON)

      # Defining the n. of total realizations for year and seasonal climatologies
      NumDays_Year = (BaseDateF - BaseDateS).days + 1 
      NumDays_DJF = monthrange(BaseDateS.year, 12)[1] + monthrange(BaseDateS.year, 1)[1] + monthrange(BaseDateS.year, 2)[1]
      NumDays_MAM = monthrange(BaseDateS.year, 3)[1] + monthrange(BaseDateS.year, 4)[1] + monthrange(BaseDateS.year, 5)[1]
      NumDays_JJA = monthrange(BaseDateS.year, 6)[1] + monthrange(BaseDateS.year, 7)[1] + monthrange(BaseDateS.year, 8)[1]
      NumDays_SON = monthrange(BaseDateS.year, 9)[1] + monthrange(BaseDateS.year, 10)[1] + monthrange(BaseDateS.year, 11)[1]
      NumRealizations_Year = int(NumDays_Year * NumRealizations_Day * NumEM)
      NumRealizations_DJF = int(NumDays_DJF * NumRealizations_Day * NumEM)
      NumRealizations_MAM = int(NumDays_MAM * NumRealizations_Day * NumEM)
      NumRealizations_JJA = int(NumDays_JJA * NumRealizations_Day * NumEM)
      NumRealizations_SON = int(NumDays_SON * NumRealizations_Day * NumEM)
      
      # Initializing the variables that will store the indipendent rainfall realizations
      tp_year = np.float16(np.empty([NumStn_year, NumRealizations_Year]) * np.nan)
      tp_DJF = np.float16(np.empty([NumStn_DJF, NumRealizations_DJF]) * np.nan)
      tp_MAM = np.float16(np.empty([NumStn_MAM, NumRealizations_MAM]) * np.nan)
      tp_JJA = np.float16(np.empty([NumStn_JJA, NumRealizations_JJA]) * np.nan)
      tp_SON = np.float16(np.empty([NumStn_SON, NumRealizations_SON]) * np.nan)
      
      # Computing the independent rainfall realizations for the year/seasonal climatologies
      print(" - Computing the independent rainfall realizations for the year/seasonal climatologies. Processing " + str(Acc) + "-hourly accumulation period ending on:")
      ind_year = 0
      ind_DJF = 0
      ind_MAM = 0
      ind_JJA = 0
      ind_SON = 0
      
      # Extracting the independent rainfall realizations for year/seasonal climatologies
      BaseDate = BaseDateS
      while BaseDate <= BaseDateF:
            
            print("     ", BaseDate) 
            FileIN_temp = DirIN_FC + "/" + BaseDate.strftime("%Y%m") + "/" + ecPoint_Dataset + "_" + BaseDate.strftime("%Y%m%d") + ".grib2"

            if exists(FileIN_temp):
                  
                  # Reading the forecasts for the considered day
                  tp = mv.read(FileIN_temp)
                  
                  # Extracting the independent rainfall realizations for the year climatology
                  tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_year, stn_lons_year)), decimals =1)
                  tp_year[:, ind_year] = tp_obs_temp
                  ind_year += 1

                  # Populating the variables that contains the independent rainfall realizations for the seasonal climatologies
                  if BaseDate.month == 12 or BaseDate.month == 1 or BaseDate.month == 2:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_DJF, stn_lons_DJF)), decimals =1)
                        tp_DJF[:, ind_DJF] = tp_obs_temp
                        ind_DJF += 1
                  elif BaseDate.month == 3 or BaseDate.month == 4 or BaseDate.month == 5:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_MAM, stn_lons_MAM)), decimals =1)
                        tp_MAM[:, ind_MAM] = tp_obs_temp
                        ind_MAM += 1
                  elif BaseDate.month == 6 or BaseDate.month == 7 or BaseDate.month == 8:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_JJA, stn_lons_JJA)), decimals =1)
                        tp_JJA[:, ind_JJA] = tp_obs_temp
                        ind_JJA += 1
                  elif BaseDate.month == 9 or BaseDate.month == 10 or BaseDate.month == 11:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_SON, stn_lons_SON)), decimals =1)
                        tp_SON[:, ind_SON] = tp_obs_temp
                        ind_SON += 1
            else:

                  print("Forecast not availbale in the database.")

            BaseDate += timedelta(days=1)

      # Saving the year/seasonal climatologies and their correspondent metadata
      print(" - Saving the year/seasonal rainfall realizations")
      np.save(DirOUT + "/tp_Year_" + str(Year) + ".npy", tp_year)
      np.save(DirOUT + "/tp_DJF_" + str(Year) + ".npy", tp_DJF)
      np.save(DirOUT + "/tp_MAM_" + str(Year) + ".npy", tp_MAM)
      np.save(DirOUT + "/tp_JJA_" + str(Year) + ".npy", tp_JJA)
      np.save(DirOUT + "/tp_SON_" + str(Year) + ".npy", tp_SON)

#############################################################################
# Compute independent rainfall realizations from ERA5_ecPoint (point-scale, bias corrected)   # 
#############################################################################
def rainfall_24h_ERA5_ecPoint_pointBC(BaseDateS, BaseDateF, Acc, DirIN_ClimateOBS, DirIN_FC, DirOUT):

      # Specific parameters for the considered forecasting system
      ecPoint_Dataset = DirIN_FC.split("/")[-1]
      NumEM = 99
      NumRealizations_Day = 1
      
      # Loading the stations for year and seasonal climatologies
      stn_lats_year = np.load(DirIN_ClimateOBS + "/Stn_lats_Year.npy")
      stn_lons_year = np.load(DirIN_ClimateOBS + "/Stn_lons_Year.npy")
      stn_lats_DJF = np.load(DirIN_ClimateOBS + "/Stn_lats_DJF.npy")
      stn_lons_DJF = np.load(DirIN_ClimateOBS + "/Stn_lons_DJF.npy")
      stn_lats_MAM = np.load(DirIN_ClimateOBS + "/Stn_lats_MAM.npy")
      stn_lons_MAM = np.load(DirIN_ClimateOBS + "/Stn_lons_MAM.npy")
      stn_lats_JJA = np.load(DirIN_ClimateOBS + "/Stn_lats_JJA.npy")
      stn_lons_JJA = np.load(DirIN_ClimateOBS + "/Stn_lons_JJA.npy")
      stn_lats_SON = np.load(DirIN_ClimateOBS + "/Stn_lats_SON.npy")
      stn_lons_SON = np.load(DirIN_ClimateOBS + "/Stn_lons_SON.npy")

      # Defining the n. of stations in the year and seasonal climatologies
      NumStn_year = len(stn_lats_year)
      NumStn_DJF = len(stn_lats_DJF)
      NumStn_MAM = len(stn_lats_MAM)
      NumStn_JJA = len(stn_lats_JJA)
      NumStn_SON = len(stn_lats_SON)

      # Defining the n. of total realizations for year and seasonal climatologies
      NumDays_Year = (BaseDateF - BaseDateS).days + 1 
      NumDays_DJF = monthrange(BaseDateS.year, 12)[1] + monthrange(BaseDateS.year, 1)[1] + monthrange(BaseDateS.year, 2)[1]
      NumDays_MAM = monthrange(BaseDateS.year, 3)[1] + monthrange(BaseDateS.year, 4)[1] + monthrange(BaseDateS.year, 5)[1]
      NumDays_JJA = monthrange(BaseDateS.year, 6)[1] + monthrange(BaseDateS.year, 7)[1] + monthrange(BaseDateS.year, 8)[1]
      NumDays_SON = monthrange(BaseDateS.year, 9)[1] + monthrange(BaseDateS.year, 10)[1] + monthrange(BaseDateS.year, 11)[1]
      NumRealizations_Year = int(NumDays_Year * NumRealizations_Day * NumEM)
      NumRealizations_DJF = int(NumDays_DJF * NumRealizations_Day * NumEM)
      NumRealizations_MAM = int(NumDays_MAM * NumRealizations_Day * NumEM)
      NumRealizations_JJA = int(NumDays_JJA * NumRealizations_Day * NumEM)
      NumRealizations_SON = int(NumDays_SON * NumRealizations_Day * NumEM)
      
      # Initializing the variables that will store the indipendent rainfall realizations
      tp_year = np.float16(np.empty([NumStn_year, NumRealizations_Year]) * np.nan)
      tp_DJF = np.float16(np.empty([NumStn_DJF, NumRealizations_DJF]) * np.nan)
      tp_MAM = np.float16(np.empty([NumStn_MAM, NumRealizations_MAM]) * np.nan)
      tp_JJA = np.float16(np.empty([NumStn_JJA, NumRealizations_JJA]) * np.nan)
      tp_SON = np.float16(np.empty([NumStn_SON, NumRealizations_SON]) * np.nan)
      
      # Computing the independent rainfall realizations for the year/seasonal climatologies
      print(" - Computing the independent rainfall realizations for the year/seasonal climatologies. Processing " + str(Acc) + "-hourly accumulation period ending on:")
      ind1_year = 0
      ind2_year = ind1_year + (NumEM * NumRealizations_Day)
      ind1_DJF = 0
      ind2_DJF = ind1_DJF + (NumEM * NumRealizations_Day)
      ind1_MAM = 0
      ind2_MAM = ind1_MAM + (NumEM * NumRealizations_Day)
      ind1_JJA = 0
      ind2_JJA = ind1_JJA + (NumEM * NumRealizations_Day)
      ind1_SON = 0
      ind2_SON = ind1_SON + (NumEM * NumRealizations_Day)
      
      BaseDate = BaseDateS
      while BaseDate <= BaseDateF:
            
            print("     ", BaseDate) 
            FileIN_temp = DirIN_FC + "/" + BaseDate.strftime("%Y%m") + "/" + ecPoint_Dataset + "_" + BaseDate.strftime("%Y%m%d") + ".grib2"

            if exists(FileIN_temp):
                  
                  # Reading the forecasts for the considered day
                  tp = mv.read(FileIN_temp)
                  
                  # Extracting the independent rainfall realizations for the year climatology
                  tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_year, stn_lons_year)), decimals =1).T
                  tp_year[:, ind1_year:ind2_year] = tp_obs_temp
                  ind1_year = ind2_year
                  ind2_year = ind1_year + NumEM

                  # Populating the variables that contains the independent rainfall realizations for the seasonal climatologies
                  if BaseDate.month == 12 or BaseDate.month == 1 or BaseDate.month == 2:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_DJF, stn_lons_DJF)), decimals =1).T
                        tp_DJF[:, ind1_DJF:ind2_DJF] = tp_obs_temp
                        ind1_DJF = ind2_DJF
                        ind2_DJF = ind1_DJF + NumEM
                  elif BaseDate.month == 3 or BaseDate.month == 4 or BaseDate.month == 5:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_MAM, stn_lons_MAM)), decimals =1).T
                        tp_MAM[:, ind1_MAM:ind2_MAM] = tp_obs_temp
                        ind1_MAM = ind2_MAM
                        ind2_MAM = ind1_MAM + NumEM
                  elif BaseDate.month == 6 or BaseDate.month == 7 or BaseDate.month == 8:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_JJA, stn_lons_JJA)), decimals =1).T
                        tp_JJA[:, ind1_JJA:ind2_JJA] = tp_obs_temp
                        ind1_JJA = ind2_JJA
                        ind2_JJA = ind1_JJA + NumEM
                  elif BaseDate.month == 9 or BaseDate.month == 10 or BaseDate.month == 11:
                        tp_obs_temp = np.round(np.float16(mv.nearest_gridpoint(tp, stn_lats_SON, stn_lons_SON)), decimals =1).T
                        tp_SON[:, ind1_SON:ind2_SON] = tp_obs_temp
                        ind1_SON = ind2_SON
                        ind2_SON = ind1_SON + NumEM

            else:

                  print("Forecast not availbale in the database.")

            BaseDate += timedelta(days=1)
 
      # Saving the year/seasonal climatologies and their correspondent metadata
      print(" - Saving the year/seasonal rainfall realizations")
      np.save(DirOUT + "/tp_Year_" + str(Year) + ".npy", tp_year)
      np.save(DirOUT + "/tp_DJF_" + str(Year) + ".npy", tp_DJF)
      np.save(DirOUT + "/tp_MAM_" + str(Year) + ".npy", tp_MAM)
      np.save(DirOUT + "/tp_JJA_" + str(Year) + ".npy", tp_JJA)
      np.save(DirOUT + "/tp_SON_" + str(Year) + ".npy", tp_SON)

#############################################################################################################################################

# Defining the dates for the given year
BaseDateS = date(Year,1,1)
BaseDateF = date(Year,12,31)

# Extracting the rainfall realizations
for MinDays_Perc in MinDays_Perc_list:

      for NameOBS in NameOBS_list:

            if (NameOBS == "06_AlignOBS_Combine_Years_RawSTVL") or (NameOBS == "07_AlignOBS_Extract_GridCPC"):

                  # Setting the input directory for the observational climatologies
                  MainDirIN_ClimateOBS = Git_repo + "/" + DirIN_ClimateOBS + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS
                  
                  for SystemFC in SystemFC_list:
                        
                        print(" ")
                        print("Computing modelled (" + SystemFC + ") climatologies at stations for "+ NameOBS + " with a minimum of " + str(int(MinDays_Perc*100)) + "% of days over the considered period with valid observations")

                        # Setting the input directory for the forecasts
                        MainDirIN_FC = Git_repo + "/" + DirIN_FC + "/" + SystemFC
                        
                        # Setting the output directory
                        MainDirOUT = Git_repo + "/" + DirOUT + "/" + SystemFC + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS
                        if not exists(MainDirOUT):
                                    os.makedirs(MainDirOUT)

                        # Computing the independent rainfall realizations for the considering forecasting system
                        if SystemFC == "HRES_46r1":
                              rainfall_HRES(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                        elif SystemFC == "Reforecasts_46r1":
                              rainfall_REFORECAST(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                        elif SystemFC == "ERA5_ShortRange":
                              rainfall_24h_ERA5_SR(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                        elif SystemFC == "ERA5_EDA_ShortRange":
                              rainfall_24h_ERA5_EDA_SR(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                        elif SystemFC == "ERA5_LongRange":
                              rainfall_ERA5_LR(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                        elif SystemFC == "ERA5_EDA_LongRange":
                              rainfall_ERA5_EDA_LR(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                        elif SystemFC == "ERA5_ecPoint/Grid_BC_VALS":
                              rainfall_24h_ERA5_ecPoint_gridBC(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                        elif SystemFC == "ERA5_ecPoint/Pt_BC_PERC":
                              rainfall_24h_ERA5_ecPoint_pointBC(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)

            elif NameOBS == "08_AlignOBS_CleanSTVL":

                  for Coeff_Grid2Point in Coeff_Grid2Point_list:
                        
                        # Setting the input directory for the observational climatologies
                        MainDirIN_ClimateOBS = Git_repo + "/" + DirIN_ClimateOBS + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS + "/Coeff_Grid2Point_" + str(Coeff_Grid2Point)
                        
                        for SystemFC in SystemFC_list:
                              
                              print(" ")
                              print("Computing modelled (" + SystemFC + ") climatologies at stations for "+ NameOBS + " (Coeff_Grid2Point=" + str(Coeff_Grid2Point) + ") with a minimum of " + str(int(MinDays_Perc*100)) + "% of days over the considered period with valid observations")

                              # Setting the input directory for the forecasts
                              MainDirIN_FC = Git_repo + "/" + DirIN_FC + "/" + SystemFC

                              # Setting the output directory
                              MainDirOUT = Git_repo + "/" + DirOUT + "/" + SystemFC + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS + "/Coeff_Grid2Point_" + str(Coeff_Grid2Point)
                              if not exists(MainDirOUT):
                                    os.makedirs(MainDirOUT)
                              
                              # Computing the independent rainfall realizations for the considering forecasting system
                              if SystemFC == "HRES_46r1":
                                    rainfall_HRES(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                              elif SystemFC == "Reforecasts_46r1":
                                    rainfall_REFORECAST(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                              elif SystemFC == "ERA5_ShortRange":
                                    rainfall_24h_ERA5_SR(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                              elif SystemFC == "ERA5_EDA_ShortRange":
                                    rainfall_24h_ERA5_EDA_SR(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                              elif SystemFC == "ERA5_LongRange":
                                    rainfall_ERA5_LR(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                              elif SystemFC == "ERA5_EDA_LongRange":
                                    rainfall_ERA5_EDA_LR(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                              elif SystemFC == "ERA5_ecPoint/Grid_BC_VALS":
                                    rainfall_24h_ERA5_ecPoint_gridBC(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)
                              elif SystemFC == "ERA5_ecPoint/Pt_BC_PERC":
                                    rainfall_24h_ERA5_ecPoint_pointBC(BaseDateS, BaseDateF, Acc, MainDirIN_ClimateOBS, MainDirIN_FC, MainDirOUT)