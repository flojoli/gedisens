def vector_preperation(df, data_name):
    """Rotates vector and drops zeros.

    Args:

       df (pandas dataframe)

       data_name (str) : in this study either Amplitude
                           or Pulse.

    Returns: vector with dropped 0s.

    """

    df = df.drop(columns=("Shot_Numbe"))
    df = df.T
    df = df.iloc[::-1]

    df = df.reset_index()
    df = df.drop(columns="index")
    # search for first non zero
    limit = df.ne(0).idxmax()

    df = df.drop(df.index[0:int(limit)])
    df = df.iloc[::-1]

    df = df.reset_index(drop=True)
    df.index += 1
    df["Index"] = df.index
    df.rename(columns={df.columns[0]: data_name}, inplace=True)

    values = list(df[["Index", data_name]].apply(tuple, axis=1))

    return values


def calc_variance(data):
    """Calculates variance of grouped variable.

    Args:

        data (list): list of grouped data.

    Returns: list of variance for each group.
    
    """

    variance_list = [group.var().round(2) for group in data]

    return variance_list


def calc_upper_percentage(row):
    """Calculates the percentage of pulse contained in upper layer.
    
    Function will be passed to apply, therefore calculation is rowwise.

    Args:

        row (pandas dataframe): dataframe with one row used in apply func.

    Returns: dataframe of one row with upper percentage.

    """

    col_list = [f"Pulse{i-1}_{i}" for i in range(row.max_height_lower,row.max_height_upper)]

    above_max_lower = row[col_list].sum()

    row["amp_sum_total"] = row.filter(regex="Pulse").sum()

    row["upper_percentage"] = round((above_max_lower / row.amp_sum_total),2)

    return row

def calc_layers(row,lim_low=0.3,lim_up=0.5)
    """Calculates the number of layers of each footprint.
    
    Args:
    
        row (pandas dataframe): dataframe with one row.

        lim_low/lim_up: thresholds for applying which layer.
                        (default:0.3;0.5)
        
    Returns: dataframe with one row with calculated layer.
    
    """

    if row.upper_percentage < lim_low:
        print("footprint has multiple layers")
        row["NoL"] = 3

    elif row.upper_percentage > lim_up:
        print("footprint has 1 layer")
        row["NoL"] = 1

    elif (row.upper_percentage >= lim_low) and (row.upper_percentage < lim_up) and (row.max_height_upper > 6):
        # comment: somehow problems with max_height_lower range and last point to search for
        
        start = np.ceil(row.max_height_upper/6).astype(int)
        
        max_search = row.max_height_lower - start  # search_range
       
        if start > max_search:
            row["NoL"] = 1

        else:
            
            for sextile in range(start, max_search + 1, 1):
                
                col_list = [f"Pulse{amp_up}_{amp_up+1}"
                for amp_up in range(sextile - start+1, sextile + start, 1)]
                
                amp_sum_lower = row[col_list].sum()
    
                lower_percentage = amp_sum_lower / row.amp_sum_total
                
                if lower_percentage >= lim_low:
                    print("footprint has 2 layers")
                    row["NoL"] = 2
                    break
                else:
                    continue

            if lower_percentage < lim_low:
                print("footprint has 2 layers")
                row["NoL"] = 3
    return row


def calc_fhd(df,attr_name):
    """Calculates foliage height diversity.
    
    Args:
    
        df (pandas dataframe): input dataframe has one row with pulses and or
                               other attribute to calc fhd on.

        attr_name (string): name of attribute on which fhd is calculated (e.g. Pulse). 
        
    Returns: pandas dataframe with calculated fhd values.
                        
    """
    
    attr_df = df[[i for i in df.columns if i.startswith(attr_name)]]
        
    if f"{attr_name}0_1" in attr_df.columns:
        
        attr_df = attr_df.drop(columns=f"{attr_name}0_1")
       
        
    if int(attr_df.sum(axis=1,numeric_only=True)) == 0:
        
        df = df.reset_index()
        df["fhd"] = np.nan   
                
    else:
        
        attr_df = attr_df.T
        attr_df.replace(0, np.nan, inplace=True)
        attr_df = attr_df/attr_df.sum()
        #attr_df.replace(0, np.nan, inplace=True)
        attr_df = attr_df.dropna()
     
        log_portion = np.log(attr_df)
        fhd = round(- (attr_df * log_portion).sum(),2)
        df["fhd"] = fhd
       
    return df
