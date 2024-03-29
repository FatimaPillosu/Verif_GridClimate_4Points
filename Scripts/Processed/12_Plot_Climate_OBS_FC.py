import os
from os.path import exists
import numpy as np
import metview as mv

#####################################################################################################################################################
# CODE DESCRIPTION
# 12_Plot_Climate_OBS_FC.py plots observational and modelled rainfall climatologies at points. The script generates the map plots as static svg figures or in a Metview interactive 
# window. When plotting interactively, the user must specify a percentile to plot. When plotting static maps, the percentiles to plot are defined on the basis of the considered 
# forecasting system to plot.
# Code runtime: ~ 5 minutes for the observational climatologies and 30 minutes for the modelled climatologies.

# DESCRIPTION OF INPUT PARAMETERS
# YearS (number, in YYYY format): start year to consider.
# YearF (number, in YYYY format): final year to consider.
# Acc (number, in hours): rainfall accumulation period.
# RunType (string): type of run. Valid values are:
#                                   - "Interactive": to open the plot on an interacive Metview window.
#                                   - "Static": to save the plot on a static svg map.
# DatasetType_OBS_FC (string): defines the type of dataset to plot. Valid values are:
#                                                         - "OBS": for observational climatologies
#                                                         - "FC": for modelled climatologies
# SystemFC_list (list of string): list of forecasting systems to consider. This parameter is used only when DatasetType_OBS_FC="FC"
# MinDays_Perc_list (list of number, from 0 to 1): list of percentages of minimum n. of days over the considered period with valid observations to compute the climatologies.
# NameOBS_list (list of strings): list of the names of the observations to quality check
# Coeff_Grid2Point_list (list of integer number): list of coefficients used to compare CPC's gridded rainfall values with  STVL's point rainfall observations. 
# ClimateType_list (list of strings): types of climatology to plot. Valid values are:
#                                                               - "Year": for the year climatology
#                                                               - "DJF": for the seasonal climatology, winter months (December, January, February)
#                                                               - "MAM": for the seasonal climatology, spring months (March, April, May)
#                                                               - "JJA": for the seasonal climatology, summer months (June, July, August)
#                                                               - "SON": for the seasonal climatology, autumn months (September, October, November)
# Perc_list (list of float number, from 0 to 100): list of percentiles to plot.
# Git_repo (string): path of local github repository.
# DirIN (string): relative path for the input directory.
# DirOUT (string): relative path for the output directory .

# INPUT PARAMETERS
YearS = 2000
YearF = 2019
Acc = 24
RunType = "Interactive"
DatasetType_OBS_FC = "FC"
SystemFC_list = ["Reforecasts_46r1"]
#SystemFC_list = ["Reforecasts_46r1", "ERA5_ShortRange", "ERA5_EDA_ShortRange", "ERA5_LongRange", "ERA5_EDA_LongRange", "ERA5_ecPoint/Grid_BC_VALS", "ERA5_ecPoint/Pt_BC_PERC"]
MinDays_Perc_list = [0.75]
NameOBS_list = [ "08_AlignOBS_CleanSTVL"]
Coeff_Grid2Point_list = [20]
#ClimateType_list = ["DJF", "MAM", "JJA", "SON"]
#Perc_list = [90, 95, 98, 99, 99.5, 99.8, 99.9]
ClimateType_list = ["Year"]
Perc_list = [99.98]
#Perc_list = [90, 95, 98, 99, 99.5, 99.8,  99.9, 99.95, 99.98]
Git_repo = "/ec/vol/ecpoint_dev/mofp/Papers_2_Write/ecPoint_Climate"
DirIN = "Data/Compute"
DirOUT= "Data/Plot/12_Climate_OBS_FC"
#####################################################################################################################################################

# Costum functions

def plot_climate(RunType, ClimateType, Perc, Title_text_line_1, Title_text_line_2, DirIN, DirOUT):

    # Reading the considered climatology and the correspondent percentiles, and the rainfall stations coordinates
    climate_array = np.load(DirIN + "/Climate_" + ClimateType + ".npy")
    lats = np.load(DirIN + "/" + "Stn_lats_" + ClimateType + ".npy")
    lons = np.load(DirIN + "/" + "Stn_lons_" + ClimateType + ".npy")
    if ClimateType == "Year":
        percs = np.load(DirIN + "/Percentiles_Year.npy")
    else:
        percs = np.load(DirIN + "/Percentiles_Season.npy")

    # Selecting the climatology to plot based on the considered percentile
    ind_perc = np.where(percs == Perc) 
    climate_perc_array = climate_array[:,ind_perc[0][0]]

    # Converting the climatology to geopoint
    climate_perc_geo = mv.create_geo(
        type = 'xyv',
        latitudes =  lats,
        longitudes = lons,
        values = climate_perc_array
        )

    # Plotting the climatology
    coastlines = mv.mcoast(
            map_coastline_thickness = 1,
            map_coastline_colour = "rgb(0.4902,0.4902,0.4902)",
            map_coastline_resolution = "low",
            map_boundaries = "on",
            map_boundaries_colour = "grey",
            map_boundaries_thickness = 1,
            map_grid = "on",
            map_grid_colour              = "rgb(0.7686,0.7686,0.7686)",
            map_grid_latitude_increment  = 30,
            map_grid_longitude_increment = 60,
            map_label = "on"
            )

    markers = mv.psymb(
        symbol_type = "MARKER",
        symbol_table_mode = "ON",
        legend = "ON",
        symbol_quality = "HIGH",
        symbol_min_table = [ 0,0.5,2,5,10,20,30,40,50,60,80,100,125,150,200,300,500],
        symbol_max_table = [ 0.5,2,5,10,20,30,40,50,60,80,100,125,150,200,300,500,10000],
        symbol_marker_table = [ 15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
        symbol_colour_table = ["black","RGB(0.75,0.95,0.93)","RGB(0.45,0.93,0.78)","RGB(0.07,0.85,0.61)","RGB(0.53,0.8,0.13)","RGB(0.6,0.91,0.057)","RGB(0.9,1,0.4)","RGB(0.89,0.89,0.066)","RGB(1,0.73,0.0039)","RGB(1,0.49,0.0039)","red","RGB(0.85,0.0039,1)","RGB(0.63,0.0073,0.92)","RGB(0.37,0.29,0.91)","RGB(0.04,0.04,0.84)","RGB(0.042,0.042,0.43)","RGB(0.45,0.45,0.45)"],
        symbol_height_table = [ 0.1,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2]
        )

    legend = mv.mlegend(
        legend_text_font = "arial",
        legend_text_font_size = 0.30
        )
    
    title = mv.mtext(
        text_line_count = 3,
        text_line_1 = Title_text_line_1,
        text_line_2 =  Title_text_line_2,
        text_line_3 = " ",
        text_colou ="charcoal",
        text_font ="courier",
        text_font_size = 0.4
        )

    # Create plots
    if RunType == "Interactive":
        mv.plot(climate_perc_geo, coastlines, markers, legend, title)
    else:
        svg = mv.svg_output(output_name = DirOUT + "/" + ClimateType + "_" + str(Perc*100))
        mv.setoutput(svg)
        mv.plot(climate_perc_geo, coastlines, markers, legend, title)
#######################################################################################################################


if DatasetType_OBS_FC == "OBS":

    # Setting generic parameters depending on whether observational or modelled climatologies are plotted
    Dataset_title = "observational"
    DirIN = DirIN + "/09_Climate_OBS"
    DirOUT = DirOUT + "/Climate_OBS"

    # Plotting observational rainfall climatologies at points
    for MinDays_Perc in MinDays_Perc_list:

        for NameOBS in NameOBS_list:

            if (NameOBS == "06_AlignOBS_Combine_Years_RawSTVL") or (NameOBS == "07_AlignOBS_Extract_GridCPC"):

                print(" ")
                print("Plotting the " + Dataset_title + " climatology for "+ NameOBS + " with a minimum of " + str(int(MinDays_Perc*100)) + "% of days over the considered period with valid observations to compute the climatologies")
                Dataset_temp = NameOBS.split("_")[-1]     
                Title_text_line_2 = Dataset_temp + " - Minum of " + str(int(MinDays_Perc*100)) + "% of days with valid observations" 
                
                # Setting main input/output directories
                MainDirIN = Git_repo + "/" + DirIN + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS
                MainDirOUT = Git_repo + "/" + DirOUT + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS
                if not exists(MainDirOUT):
                    os.makedirs(MainDirOUT)

                # Plotting climatologies
                for ClimateType in ClimateType_list:               
                    for Perc in Perc_list:
                        print(" - " + ClimateType + ", " + str(Perc) + "th percentile")
                        Title_text_line_1 = str(Acc) + "-hourly " + Dataset_title + " rainfall climatology between " + str(YearS) + " and " + str(YearF) + " - " + ClimateType + " - " + str(Perc) + "th percentile"
                        plot_climate(RunType, ClimateType, Perc, Title_text_line_1, Title_text_line_2, MainDirIN, MainDirOUT)

            elif NameOBS == "08_AlignOBS_CleanSTVL":

                for Coeff_Grid2Point in Coeff_Grid2Point_list:
                            
                    print(" ")
                    print("Plotting the " + Dataset_title + " climatology for "+ NameOBS + " (Coeff_Grid2Point=" + str(Coeff_Grid2Point) + ") with a minimum of " + str(int(MinDays_Perc*100)) + "% of days over the considered period with valid observations to compute the climatologies")
                    Dataset_temp = NameOBS.split("_")[-1] + " (Coeff_Grid2Point=" + str(Coeff_Grid2Point) + ")"
                    Title_text_line_2 = Dataset_temp + " - Minum of " + str(int(MinDays_Perc*100)) + "% of days with valid observations" 

                    # Setting main input/output directories
                    MainDirIN = Git_repo + "/" + DirIN + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS + "/Coeff_Grid2Point_" + str(Coeff_Grid2Point)
                    MainDirOUT = Git_repo + "/" + DirOUT + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS + "/Coeff_Grid2Point_" + str(Coeff_Grid2Point)
                    if not exists(MainDirOUT):
                        os.makedirs(MainDirOUT)

                    # Plotting climatologies
                    for ClimateType in ClimateType_list:               
                        for Perc in Perc_list:
                            print(" - " + ClimateType + ", " + str(Perc) + "th percentile")
                            Title_text_line_1 = str(Acc) + "-hourly " + Dataset_title + " rainfall climatology between " + str(YearS) + " and " + str(YearF) + " - " + ClimateType + " - " + str(Perc) + "th percentile"
                            plot_climate(RunType, ClimateType, Perc, Title_text_line_1, Title_text_line_2, MainDirIN, MainDirOUT)

elif DatasetType_OBS_FC == "FC":

    for SystemFC in SystemFC_list:

        # Setting generic parameters depending on whether observational or modelled climatologies are plotted
        Dataset_title = "modelled (" + SystemFC + ")"
        DirIN_temp = DirIN + "/11_ClimateFC_atOBS/" + SystemFC
        DirOUT_temp = DirOUT + "/Climate_FC/" + SystemFC

        # Plotting modelled rainfall climatologies at points
        for MinDays_Perc in MinDays_Perc_list:

            for NameOBS in NameOBS_list:

                if (NameOBS == "06_AlignOBS_Combine_Years_RawSTVL") or (NameOBS == "07_AlignOBS_Extract_GridCPC"):

                    print(" ")
                    print("Plotting the " + Dataset_title + " climatology for "+ NameOBS + " with a minimum of " + str(int(MinDays_Perc*100)) + "% of days over the considered period with valid observations to compute the climatologies")
                    Dataset_temp = NameOBS.split("_")[-1]     
                    Title_text_line_2 = Dataset_temp + " - Minum of " + str(int(MinDays_Perc*100)) + "% of days with valid observations" 
                    
                    # Setting main input/output directories
                    MainDirIN = Git_repo + "/" + DirIN_temp + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS
                    MainDirOUT = Git_repo + "/" + DirOUT_temp + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS
                    if not exists(MainDirOUT):
                        os.makedirs(MainDirOUT)

                    # Plotting climatologies
                    for ClimateType in ClimateType_list:               
                        for Perc in Perc_list:
                            print(" - " + ClimateType + ", " + str(Perc) + "th percentile")
                            Title_text_line_1 = str(Acc) + "-hourly " + Dataset_title + " rainfall climatology between " + str(YearS) + " and " + str(YearF) + " - " + ClimateType + " - " + str(Perc) + "th percentile"
                            plot_climate(RunType, ClimateType, Perc, Title_text_line_1, Title_text_line_2, MainDirIN, MainDirOUT)

                elif NameOBS == "08_AlignOBS_CleanSTVL":

                    for Coeff_Grid2Point in Coeff_Grid2Point_list:
                                
                        print(" ")
                        print("Plotting the " + Dataset_title + " climatology for "+ NameOBS + " (Coeff_Grid2Point=" + str(Coeff_Grid2Point) + ") with a minimum of " + str(int(MinDays_Perc*100)) + "% of days over the considered period with valid observations to compute the climatologies")
                        Dataset_temp = NameOBS.split("_")[-1] + " (Coeff_Grid2Point=" + str(Coeff_Grid2Point) + ")"
                        Title_text_line_2 = Dataset_temp + " - Minum of " + str(int(MinDays_Perc*100)) + "% of days with valid observations" 

                        # Setting main input/output directories
                        MainDirIN = Git_repo + "/" + DirIN_temp + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS + "/Coeff_Grid2Point_" + str(Coeff_Grid2Point)
                        MainDirOUT = Git_repo + "/" + DirOUT_temp + "/MinDays_Perc" + str(int(MinDays_Perc*100)) + "/" + NameOBS + "/Coeff_Grid2Point_" + str(Coeff_Grid2Point)
                        if not exists(MainDirOUT):
                            os.makedirs(MainDirOUT)

                        # Plotting climatologies
                        for ClimateType in ClimateType_list:               
                            for Perc in Perc_list:
                                print(" - " + ClimateType + ", " + str(Perc) + "th percentile")
                                Title_text_line_1 = str(Acc) + "-hourly " + Dataset_title + " rainfall climatology between " + str(YearS) + " and " + str(YearF) + " - " + ClimateType + " - " + str(Perc) + "th percentile"
                                plot_climate(RunType, ClimateType, Perc, Title_text_line_1, Title_text_line_2, MainDirIN, MainDirOUT)
