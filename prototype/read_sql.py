import pandas as pd
import sqlite3

con = sqlite3.connect('F:\\alphatims_test\\pen12_ms2_1_36_1_400.d\\analysis.tdf')
cur = con.cursor()

#print(pd.read_sql_query('SELECT * FROM PasefFrameMsMsInfo', con))

#print(pd.read_sql_query('SELECT * FROM PasefFrameMsMsInfo GROUP BY ScanNumBegin, ScanNumEnd HAVING COUNT(*) = 0', con))

#print(pd.read_sql_query('SELECT CASE WHEN IsolationMz = 1223.00009404376 THEN * FROM PasefFrameMsMsInfo GROUP BY ScanNumBegin, ScanNumEnd HAVING COUNT(*) = 0', con))

#query = 'SELECT * FROM PasefFrameMsMsInfo WHERE IsolationMz BETWEEN 1223.00009404376-0.00000000001 AND 1223.00009404376+0.00000000001 AND FRAME = 2 GROUP BY Precursor, IsolationMz, IsolationWidth, ScanNumBegin, ScanNumEnd'
#query = 'SELECT * FROM PasefFrameMsMsInfo WHERE Precursor = 1 GROUP BY Precursor, IsolationMz, IsolationWidth, ScanNumBegin, ScanNumEnd'

#print(pd.read_sql_query(query, con))

'''df = pd.read_sql_query('SELECT * FROM PasefFrameMsMsInfo', con)
#print(df)
df2 = pd.read_sql_query('SELECT * FROM Properties', con)
merged = df.merge(df2, on='Frame')
#print(merged)
groupby_keys = ['Precursor', 'IsolationMz', 'IsolationWidth', 'ScanNumBegin', 'ScanNumEnd']
grouped = merged.loc[merged['Precursor'] == 1].groupby(by=groupby_keys)
print(list(list(grouped.groups.keys())[0]))
for i, j in zip(groupby_keys, list(list(grouped.groups.keys())[0])):
    print(i, j)
grouped2 = merged.loc[merged['Property'] == 1229]
print(grouped2)
grouped2 = grouped2.loc[grouped2['Frame'] == 2]
print(grouped2)'''
#print(df)
#grouped = df.loc[df['Precursor'] == 1].groupby(by=['Precursor', 'IsolationMz', 'IsolationWidth', 'ScanNumBegin', 'ScanNumEnd'])

#print(df.loc[df['Precursor'] == 1].shape[0])

#query = 'SELECT * FROM PasefFrameMsMsInfo WHERE Precursor = 1 GROUP BY Precursor, IsolationMz, IsolationWidth, ScanNumBegin, ScanNumEnd'
#query = 'SELECT * FROM PasefFrameMsMsInfo JOIN Properties ON Properties.Frame = PasefFrameMsMsInfo.Frame'

#print(pd.read_sql_query(query, con))

df = pd.read_sql_query('SELECT * FROM PasefFrameMsMsInfo WHERE Precursor = 1', con)
print(min(df['Frame'].values.tolist()))
print(max(df['Frame'].values.tolist()))
df2 = pd.read_sql_query('SELECT * FROM Properties WHERE Frame BETWEEN ' + str(min(df['Frame'].values.tolist())) +
                        ' AND ' + str(max(df['Frame'].values.tolist())), con)
df2 = list(set(df2.loc[df2['Property'] == 1229]['Value'].values.tolist()))
print(df, df2)

con.close()
