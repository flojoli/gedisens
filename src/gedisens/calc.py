def vector_preperation(df, data_name):
    """Rotates vector and drops zeros.

    Args:

       df (pandas dataframe)

       vector_name (str) : in this study either Amplitude
                           or Pulse.

    Returns: vector with dropped 0s

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
