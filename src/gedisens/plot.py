import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gedisens.get import _get_waveform_series
from gedisens.calc import vector_preperation
from gedisens.stats import Stats

def plot_gedi_als_structure(df,shot_number, dz=1, add_info="",output_dir=""):
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
                    [f"Pulse{i}_{i+dz}" for i in range(1, 50, dz)]]

    gedi_df = df[["Shot_Numbe"] +
                      [f"Amp{i}_{i+dz}" for i in range(1,50, dz)]]


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

    if add_info == "fhd":
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
                      loc="right", fontsize="30", x=0.97, y=0.85,
                      bbox=dict(facecolor='1', edgecolor='black', pad=5))

    elif add_info == "numb_lay":
         ax2.set_title("GEDI shot ID: " + shot_number + "\n"
                       + "GEDI NoL: " + str(int(df["NoL_GEDI"])) + "\n"
                       + "ALS$_{\mathrm{co}}$ NoL: " + str(int(df["NoL_ALS"])),
                       loc="right", fontsize="30", x=0.97, y=0.9,
                       bbox=dict(facecolor='1', edgecolor='black', pad=5))

    elif add_info == "stdv_var":

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

        plt.savefig(f"{output_dir}/GEDIamp_vs_ALSpulse.png",
                    bbox_inches='tight')
        plt.close()

    else:
        plt.rcParams["figure.dpi"] = 300
        plt.show()


def plot_correlation(df,x_var,y_var,model,r2,predictions,rmse,output_dir):
    """Plot correlation between two variables.

    Args:

        df (pandas dataframe): containing the variables

        model (Regression Wrapper): statsmodels output

        x_var (str): use ALS variable here

        y_var (str): use GEDI variable here

        model (Regression Wrapper): statsmodels output

        r2 (np.float64): R squared of OLS model

        prediction (pandas series): predictions of the variable

        rmse (float): root mean squared error of estimation

        output_dir (str): where plot is saved

    Returns: Correlation plot

    """


    fig, ax = plt.subplots(figsize=(20,15))

    ax.axline((1,1), slope=1, color="black", linewidth=4, linestyle="--")

    ax.plot(df[x_var], df[y_var], linestyle="none",marker=".",markersize=15,
            label=f"data points: {len(df)}")

    ax.plot(df[x_var], predictions, linewidth=8, color="red",
            label=f"""Regression line: y = {model.params[0].round(2)}+
                   {model.params[1].round(2)}x""")

    ax.plot([],[],marker="",label=f"RMSE: {rmse}",color="None")
    ax.plot([],[],marker="",label=f"R²: {r2}",color="None")

    ax.tick_params(axis="both",labelsize=20)

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_xlabel(x_var, fontsize=25)
    ax.set_ylabel(y_var, fontsize=25)
    ax.set_title(f"Correlation of {x_var} and {y_var}",fontsize=30)

    plt.legend(fontsize=25, markerscale=2, loc="lower right", labelspacing=1)
    plt.grid()

    if output_dir:
        plt.savefig(f"{output_dir}/correlation_plot_{y_var}_vs_{x_var}.png",dpi=300,
                    bbox_inches='tight')
        plt.close()

    else:
        plt.rcParams["figure.dpi"] = 300
        plt.show()


def plot_boxplot(data,variance,output_dir=""):
    """Plots fhd values seperated into interpreted structure.

    Args:

        data (list): list of values separated in structure

        variance (list): list of variance for each category

        output_dir (str): where plot is saved

    Returns: FHD boxplot
    """

    fig, ax = plt.subplots()

    meanpointprops = dict(marker="D", markeredgecolor="black",
                          markerfacecolor="firebrick",markersize=20)

    bp = ax.boxplot(data,meanprops=meanpointprops, showmeans=True)

    for median in bp["medians"]:
        median.set(color="black",linewidth=2)
    for whiskers in bp["whiskers"]:
        whiskers.set(linewidth=2)
    for caps in bp["caps"]:
        caps.set(linewidth=2)

    ax.set_xlabel("Structure", fontsize=25)
    ax.set_ylabel("FHD",fontsize=25)
    ax.tick_params("both",labelsize=20)
    ax.set_xticks([1,2,3],["low","medium","high"])
    ax.grid()

    for (sub_meds,sub_caps,sub_variance) in zip(
            range(0,len(bp["medians"])),range(0,len(bp["caps"]),2),range(0,len(variance))):

        med = bp["medians"][sub_meds]
        mean = bp["means"][sub_meds]
        vari = variance[sub_variance]
        xpos = med.get_xdata()
        xoff = 0.1 *(xpos[1] - xpos[0])
        xlabel= xpos[1] - xoff
        capbottom = bp["caps"][sub_caps].get_ydata()[0]

        ax.text(xlabel,capbottom,
                f"n = {str(len(data[sub_meds]))}", va="center", fontsize=20, fontweight="bold")
        ax.text(xpos[1] + xoff, mean.get_ydata()[0],
                f"mean = {str(mean.get_ydata()[0].round(2))}", fontsize=20, fontweight="bold")
        ax.text(xpos[1] + xoff, mean.get_ydata()[0] - 0.05,
                f"variance = {str((vari))}", va = "center", fontsize=20, fontweight="bold")

    for i in range(len(data)):
        x = np.repeat(i+1, len(data[i]))
        y = data[i]
        ax.scatter(x,y,s=50)

    if output_dir:
       plt.savefig(f"{output_dir}/boxplot.png",dpi=300,
                   bbox_inches='tight')
       plt.close()

    else:
        plt.rcParams["figure.dpi"] = 300
        plt.show()
