import os
from datetime import datetime
import numpy as np
import metview as mv

########################################################################################################
# CODE DESCRIPTION
# 01_Plot_Climate_NWP_field.py plots the full fields for the NWP modelled rainfall climatologies.
# Code runtime: negligible

# DESCRIPTION OF INPUT PARAMETERS
# YearS (number, in YYYY format): start year to consider.
# YearF (number, in YYYY format): final year to consider.
# Acc (number, in hours): rainfall accumulation period.
# RP_2_Plot_list (list of integers, in years): list of return periods to plot.
# Dataset_SystemFC (string): name of the dataset and forecasting system to consider.
# Git_Repo (string): path of local github repository.
# DirIN (string): relative path for the directory containing the NWP modelled climatology.
# DirOUT (string): relative path for the directory containing the map plots.

# INPUT PARAMETERS
YearS = 2000
YearF = 2019
Acc = 24
RP_2_Plot_list = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
Dataset_SystemFC_list = ["Reforecasts/ECMWF_46r1", "Reanalysis/ERA5_EDA", "Reanalysis/ERA5", "Reanalysis/ERA5_ecPoint"]
Git_Repo = "/ec/vol/ecpoint_dev/mofp/Papers_2_Write/Verif_ClimateNWP_4Points"
DirIN = "Data/Raw/Climate_NWP"
DirOUT = "Data/Plot/01_Climate_NWP_field"
########################################################################################################


# Selecting the forecasting system to consider
for Dataset_SystemFC in Dataset_SystemFC_list:

      print()
      print("Plotting NWP modelled rainfall climatology from " + Dataset_SystemFC)

      # Setting main input/output directories
      MainDirIN = Git_Repo + "/" + DirIN + "/tp_" + f'{Acc:02d}' + "h_" + str(YearS) + "_" + str(YearF)  + "/" +  Dataset_SystemFC  
      MainDirOUT = Git_Repo + "/" + DirOUT + "/tp_" + f'{Acc:02d}' + "h_" + str(YearS) + "_" + str(YearF)  + "/" +  Dataset_SystemFC
      if not os.path.exists(MainDirOUT):
            os.makedirs(MainDirOUT)

      # Reading the computed climate field and correspondent return period values
      climate = mv.read(MainDirIN + "/Climate.grib")
      RP_list = np.load(MainDirIN + "/RP.npy")

      # Plotting the modelled climatologies 
      for ind_RP in range(len(RP_2_Plot_list)):

            RP = RP_2_Plot_list[ind_RP]
            index = np.where(RP_list == RP)[0]

            if len(index) == 0: 
                  
                  print("     - The " + str(RP) + "-year return period is not available") 

            else:
                  
                  print("     - For the " + str(RP) + "-year return period")
                  climate_RP = climate[index]
                  
                  # Plotting the modelled climatology
                  coastlines = mv.mcoast(
                        map_coastline_colour = "charcoal",
                        map_coastline_thickness = 5,
                        map_coastline_resolution = "low",
                        map_coastline_sea_shade = "on", # comments this line to see the rainfall totals over the sea
                        map_coastline_sea_shade_colour = "white", # # comments this line to see the rainfall totals over the sea
                        map_boundaries = "on",
                        map_boundaries_colour = "charcoal",
                        map_boundaries_thickness = 5,
                        map_administrative_boundaries = "of",
                        map_grid_latitude_increment = 30,
                        map_grid_longitude_increment = 60,
                        map_label_right = "off",
                        map_label_top = "off",
                        map_label_colour = "charcoal",
                        map_grid_thickness = 5,
                        map_grid_colour = "charcoal",
                        map_label_height = 3
                        )

                  contouring = mv.mcont(
                        legend = "on",
                        contour = "off",
                        contour_level_selection_type = "level_list",
                        contour_level_list = [0,0.5,2,5,10,20,30,40,50,60,80,100,125,150,200,300,500,1000,50000],
                        contour_label = "off",
                        contour_shade = "on",
                        contour_shade_colour_method = "list",
                        contour_shade_method = "area_fill",
                        contour_shade_colour_list = ["white","RGB(0.75,0.95,0.93)","RGB(0.45,0.93,0.78)","RGB(0.07,0.85,0.61)","RGB(0.53,0.8,0.13)","RGB(0.6,0.91,0.057)","RGB(0.9,1,0.4)","RGB(0.89,0.89,0.066)","RGB(1,0.73,0.0039)","RGB(1,0.49,0.0039)","red","RGB(0.85,0.0039,1)","RGB(0.63,0.0073,0.92)","RGB(0.37,0.29,0.91)","RGB(0.04,0.04,0.84)","RGB(0.042,0.042,0.43)","RGB(0.8,0.8,0.8)","RGB(0.4,0.4,0.4)"]
                        )

                  legend = mv.mlegend(
                        legend_text_colour = "charcoal",
                        legend_text_font = "arial",
                        legend_text_font_size = 3,
                        legend_entry_plot_direction = "row",
                        legend_automatic_poistion = "top",
                        )

                  Acc_STR = DirOUT.split("/")[-1].split("_")[1]
                  YearS_STR = DirOUT.split("/")[-1].split("_")[2]
                  YearF_STR = DirOUT.split("/")[-1].split("_")[3]
                  title = mv.mtext(
                        text_line_count = 2,
                        text_line_1 = Acc_STR + " rainfall climatology (" + str(RP) + " year return period) - " + Dataset_SystemFC + " - Period: " + YearS_STR + " to " + YearF_STR,
                        text_line_2 = " ",
                        text_colour = "charcoal",
                        text_font = "arial",
                        text_font_size = 4
                        )

                  # Saving the plot of the modelled climatology
                  FileOUT_temp = "Climate_" + str(RP) + "RP" + ".grib"
                  png = mv.png_output(output_width = 5000, output_name = MainDirOUT + "/" + FileOUT_temp)
                  mv.setoutput(png)
                  mv.plot(climate_RP, coastlines, contouring, title, legend)