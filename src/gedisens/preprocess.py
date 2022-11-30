def group_data(df,group,group_var):
    """Group var vals and drops nans.

     Args:

        df (pandas dataframe): dataframe

        group (str): either StrucGEDI or StrucALS

        group_vr (str): variable which is grouped and plotted

    Returns: list of grouped variable
    """
    df = df[df[group]!=0]
    df = df[df[group_var]!=0]
    df = df.dropna(subset=[group],how="any")

    grouped_data_list = [data_vals for _, data_vals in df.groupby(
        group)[group_var]]

    return grouped_data_list
