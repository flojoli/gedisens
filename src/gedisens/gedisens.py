import argparse
from pathlib import Path
from gedisens import calc, io_vec, plot, preprocess, stats, get       


def gedisens():

    parser = argparse.ArgumentParser()
    parser.add_argument(
           "-data-file",
           dest="data_file",
           type=str,
           required=True,
           help="Filename of input data.",
    )
    parser.add_argument(
         "-layers",
         dest="layers",
         type=str,
         required=False,
         help="Layers are calculated."
    )
    parser.add_argument(
           "-structure-plot",
           dest="structure_plot",
           action="store_true",
           required=False,
           help="ALS and GEDI structure are plotted."
    )
    parser.add_argument(
           "-shot-number",
           dest="shot_number",
           type=str,
           required=False,
           help="Shot number which should be analyzed.",
    )
    parser.add_argument(
           "-dz",
           dest="dz",
           type=int,
           required=False,
           help="Vertical height of layers.",
    )
    parser.add_argument(
           "-add-info",
           dest="add_info",
           choices=["fhd","stdv_var","numb_lay"],
           type=str,
           required=False,
           help="Adds additional info to plot."
    )
    parser.add_argument(
           "-correlation-plot",
           dest="correlation_plot",
           action="store_true",
           required=False,
           help="Plot correlation."
    )
    parser.add_argument(
           "-x-var",
           dest="x_var",
           type=str,
           required=False,
           help="x variable for correlation plot."
    )
    parser.add_argument(
           "-y-var",
           dest="y_var",
           type=str,
           required=False,
           help="y variable for correlation plot."
    )
    parser.add_argument(
           "-boxplot",
           dest="boxplot",
           action="store_true",
           help="Boxplot of variable."
    )
    parser.add_argument(
           "-group",
           dest="group",
           choices=["StrucGEDI","StrucALS"],
           type=str,
           help="Group data by this group name.",
    )
    parser.add_argument(
           "-group-var",
           dest="group_var",
           choices=["gediFHDcal","gediFHDl2b,alsFHD,alsFHDco"],
           type=str,
           help="Choose variable for boxplot."
    )
    parser.add_argument(
           "-out-dir",
           dest="output_dir",
           type=str,
           help="Output directory to store plot.",
    )


    args = parser.parse_args()

    if args.data_file and not Path(args.data_file).exists():
            parser.error(
                    f"File {args.data_file} does not exist.")



    data = io_vec.shp2df(args.data_file)

    if args.layers:
         

    if args.structure_plot:
        plot.plot_gedi_als_structure(data,args.shot_number,args.dz,
                                     add_info=args.add_info,
                                     output_dir=args.output_dir)

    if args.correlation_plot:
        #TODO should not be part of CLI
        data = data[data[args.x_var]!=0]
        df, model, x, r2, predictions, rmse = stats.ols_regression(
            data,y_var = args.y_var,x_var=args.x_var)

        plot.plot_correlation(df,args.x_var,args.y_var,model,r2,
                              predictions,rmse,
                              output_dir=args.output_dir)

    if args.boxplot:
        grouped_data_list = preprocess.group_data(
            df = data,
            group = args.group,
            group_var=args.group_var)
        print(len(grouped_data_list))
        variance_list = calc.calc_variance(grouped_data_list)

        plot.plot_boxplot(data = grouped_data_list,
                          variance = variance_list,
                          output_dir = args.output_dir)
