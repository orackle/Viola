import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# ================================================================================
# // Q1 
#   Prompt user for range of years and crime type.
#   The month wise total count of the number of the crime incidents occured in the
#   given range is displayed on a bar plot.
# ================================================================================

conn = sqlite3.connect("./a4-sampled.db")
c = conn.cursor()
strt_year = int(input("Enter start year (YYYY):"))
end_year = int(input("Enter end_year (YYYY):"))
crime_type = input("Enter a crime type:")

q1 = '''
    SELECT Month, Crime_Type, count(Incidents_Count) as I_C
    From crime_incidents 
    WHERE Crime_Type = '{}' and Year >= {} and Year <= {} 
    group by Month
'''.format(crime_type,strt_year,end_year)
df = pd.read_sql_query(q1, conn)
found = df['Month']
arr = []

for i in range(1, 13):
    if not (found==i).any():
        arr.append(i)
    else:
        i=i+1

for k in arr:
    df.loc[len(df)] = [k, 'Homicide', 0]

df = df.sort_values(by='Month')
print(df.to_string(index=False))

plot = df.plot.bar(x="Month")
plt.plot()
plt.show()
plt.close()

conn.close()
