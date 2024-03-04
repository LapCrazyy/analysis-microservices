import pandas as pd

def readCsv(filepath):
	try:
	    csv = pd.read_csv(filepath)
	except:
	    print(f"Cannot read: {filepath} not found, check its existance on minio")
	    return pd.DataFrame()
	return csv

def joinDf(df1, df2):
	#join 2 DataFrames throws exception if df1, df2 are empty
	if df1.empty and df2.empty:
	    return False
	elif not df1.empty:
	    if not df2.empty:
	        data = pd.concat([df1, df2], axis=0)
	    else:
	        data = df1
	elif not df2.empty:
	    data = df2
	return data