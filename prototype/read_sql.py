import pandas as pd
import sqlite3

con = sqlite3.connect('F:\\alphatims_test\\pen12_ms2_1_36_1_400.d\\analysis.tdf')
cur = con.cursor()

#print(pd.read_sql_query('SELECT * FROM PasefFrameMsMsInfo', con))

#print(pd.read_sql_query('SELECT * FROM PasefFrameMsMsInfo GROUP BY ScanNumBegin, ScanNumEnd HAVING COUNT(*) = 0', con))

#print(pd.read_sql_query('SELECT CASE WHEN IsolationMz = 1223.00009404376 THEN * FROM PasefFrameMsMsInfo GROUP BY ScanNumBegin, ScanNumEnd HAVING COUNT(*) = 0', con))

query = 'SELECT * FROM PasefFrameMsMsInfo WHERE IsolationMz BETWEEN 1223.00009404376-0.00000000001 AND 1223.00009404376+0.00000000001 AND FRAME = 2 GROUP BY Precursor, IsolationMz, IsolationWidth, ScanNumBegin, ScanNumEnd'
query = 'SELECT * FROM PasefFrameMsMsInfo WHERE Precursor = 1 GROUP BY Precursor, IsolationMz, IsolationWidth, ScanNumBegin, ScanNumEnd'

print(pd.read_sql_query(query, con))

df = pd.read_sql_query('SELECT * FROM PasefFrameMsMsInfo', con)
print(df)
print(df.loc[df['Precursor'] == 1].groupby(by=['Precursor', 'IsolationMz', 'IsolationWidth', 'ScanNumBegin', 'ScanNumEnd']))
print(df.loc[df['Precursor'] == 1].shape[0])