import pandas as pd
import matplotlib.pyplot as plt
from get import _get_waveform_series
from calc import vector_preperation
from stats import Stats

def plot_gedi_als_structure(df,shot_number, dz=1, output_dir=False,
                            fhd=False, stdv_var=False, numb_lay=False):
    """Plot GEDI and ALS amplitude/pulse vertical structure.

    Command: plot_gedi_als_structure(df,shot_number="35070300200196495",dz=1,output_dir=".",numb_lay=True)

    Args:

        df (pandas dataframe)

        shot_number (str): shot_number of interest in df

        dz (int): vertical step size. Default is 1.
                  if other vertical steps are calculated
                  other dz can be used.

        fhd (bool): optional if fhd values are broadcasted

        numb_lay (bool): optional if number of layer values are broadcasted

        stdv_var (bool): optional if stdv and variance are broadcasted

        output_dir (str): where plot is saved

    Returns: Plot with GEDI and ALS structure and calculated features of footprint

    """

    # tree height from 1m to 50m
    df = df[df["Shot_Numbe"] == shot_number]
    als_df = df[["Shot_Numbe"] +
                    [f"Pulse{i}_{i+dz}" for i in range(1, 49, dz)]]

    gedi_df = df[["Shot_Numbe"] +
                      [f"Amp{i}_{i+dz}" for i in range(1,49, dz)]]


    fig = plt.figure(figsize=(30,30))
    # ax1 = fig.add_subplot(1, 1, 1)
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
    ax1 = fig.add_subplot(1, 1, 1)
    # ALS plot set up
    x_als, y_als = _get_waveform_series(als_df,dz,data_name="Pulse")

    # GEDI plot set up
    x_gedi, y_gedi = _get_waveform_series(gedi_df,dz,data_name="Amplitude")

    wave_amp = pd.concat(([y_gedi, x_gedi]), axis=1)
    wave_amp = wave_amp[wave_amp.Amplitude > 0]
    wave_amp["Amplitude"] = wave_amp.Amplitude/wave_amp.Amplitude.sum()*100

    # ALS plot
    h1 = ax1.barh(y_als, x_als, height=dz-0.3,color="forestgreen",
                  alpha=0.75, label="ALS return")
    # GEDI plot
    ax2 = ax1.twiny()
    h2 = ax2.plot(wave_amp.Amplitude, wave_amp.Elevation, color="black",
                   linewidth=4, label="GEDI waveform")

    ax1.set_xlabel("ALS returns [%]",fontsize=30,labelpad=14)
    ax1.set_ylabel("Height [m]",fontsize=30,labelpad=14)
    ax1.set_ylim(0,51)
    ax1.set_yticks([0,5,10,15,20,25,30,35,40,45,50])
    ax1.grid()
    ax1.tick_params(labelsize=30)

    ax2.set_xlabel("GEDI amplitude [%]",fontsize=30,labelpad=14)
    ax2.set_xlim(0,10)
    ax2.tick_params(labelsize=30)

    if fhd == True:
       gedi_fhd_l2b = float(df["gediFHDl2b"])
       gedi_fhd_cal = float(df["gediFHDcal"])
       als_fhd = float(df["alsFHD"])
       als_fhd_co = float(df["alsFHDco"])

       ax2.set_title("GEDI shot ID: " + shot_number + "\n"
                      + r"GEDI FHD$_{\mathrm{L2B}}$:  " +
                       str(round(gedi_fhd_l2b, 2)) + "\n"
                      + r"GEDI FHD$_{\mathrm{calc}}$: " +
                       str(gedi_fhd_cal) + "\n"
                      + "ALS FHD :  " + str(als_fhd) + "\n"
                      + "ALS$_{\mathrm{co}}$ FHD :  " +
                       str(als_fhd_co),
                      loc="right", fontsize="30", x=0.97, y=0.9,
                      bbox=dict(facecolor='1', edgecolor='black', pad=5))

    elif numb_lay == True:
         ax2.set_title("GEDI shot ID: " + shot_number + "\n"
                       + "GEDI NoL: " + str(int(df["NoL_GEDI"])) + "\n"
                       + "ALS$_{\mathrm{co}}$ NoL: " + str(int(df["NoL_ALS"])),
                       loc="right", fontsize="30", x=0.97, y=0.9,
                       bbox=dict(facecolor='1', edgecolor='black', pad=5))

    elif stdv_var == True:

         gedi_variance = Stats(vector_preperation(gedi_df, "Amplitude")).variance
         gedi_variance = round(gedi_variance, 2)
         gedi_stdv = Stats(vector_preperation(gedi_df, "Amplitude")).stdv
         gedi_stdv = round(gedi_stdv, 2)

         als_variance = Stats(vector_preperation(als_df, "Pulse")).variance
         als_variance = round(als_variance, 2)
         als_stdv = Stats(vector_preperation(als_df, "Pulse")).stdv
         als_stdv = round(als_stdv, 2)

         ax2.set_title("GEDI shot ID: " + shot_number + "\n"
                       + "GEDI variance: " + str(gedi_variance) + "\n"
                       + "GEDI stdv: " + str(gedi_stdv) + "\n"
                       + "ALS$_{\mathrm{co}}$ variance: " + str(als_variance) + "\n"
                       + "ALS$_{\mathrm{co}}$ stdv: " + str(als_stdv),
                       loc="right", fontsize="30", x=0.97, y=0.85,
                       bbox=dict(facecolor='1', edgecolor='black', pad=5))

    else:
        ax2.set_title("GEDI shot ID: " + shot_number,
                       loc="right", fontsize="30", x=0.97, y=0.9,
                       bbox=dict(facecolor='1', edgecolor='black', pad=5))

    fig.legend((h1, h2), labels=["ALS", "GEDI"],loc="lower right",
               bbox_to_anchor=(0.899, 0.13), fontsize=30)

    if output_dir:
        fig.savefig(f"{output_dir}/GEDIamp_vs_ALSpulse.png",dpi=300,
                    bbox_inches='tight')
        plt.close()

    else:
        plt.show()
