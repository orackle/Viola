import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import folium

# ================================================================================
# // Global Variables
# ================================================================================
q1_count = 0
q2_count = 0
q3_count = 0
q4_count = 0
# ================================================================================
# // User inputs and error handling
# ================================================================================
def enter_db_name():
    db_name = input("Enter the name of the database you want to access (without .db): \t")
    return db_name
def main():
    database_name = enter_db_name()
    check_connection = 'file:{}.db?mode=rw'.format(database_name)
    try:
        conn = sqlite3.connect(check_connection, uri=True)
        database_name = "./{}.db".format(database_name)
        main_query(database_name)
    except sqlite3.OperationalError:
        print("database doesn't exist, try again!")
        main()
# ================================================================================
# // Main function
# ================================================================================
def main_query(database_name):
    while True:
        print("""
        1. Q1               2. Q2
        3. Q3               4. Q4
        5. QUIT
        """)
        #Ask user to input a number between 1-5
        #Which further calls the respective function
        choice = input('Choose from above: ')
        if choice == '1':
            print('1 option')
            q1(database_name)
        elif choice == '2':
            print('2 option')
            q2(database_name)
        elif choice == '3':
            print('3 option')
            q3(database_name)
        elif choice == '4':
            print('4 option')
            q4(database_name)
        elif choice == '5':
            exit(0)
        else:
            print('Invalid Input. Try again')
# ================================================================================
# // Q1
#   Prompt user for range of years and crime type.
#   The month wise total count of the number of the crime incidents occured in the
#   given range is displayed on a bar plot.
# ================================================================================
def q1(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    #Get user input.
    strt_year = int(input("Enter start year (YYYY):"))
    end_year = int(input("Enter end_year (YYYY):"))
    crime_type = input("Enter a crime type:")
    #For each month, get the crime counts of the entered crime type
    #within the year range.
    q1 = '''
        SELECT Month, Crime_Type, count(Incidents_Count) as I_C
        From crime_incidents 
        WHERE Crime_Type = '{}' and Year >= {} and Year <= {} 
        group by Month
    '''.format(crime_type,strt_year,end_year)
    df = pd.read_sql_query(q1, conn)
    found = df['Month']
    arr = []

    #Create dataframe in order to plot barplot
    for i in range(1, 13):
        if not (found==i).any():
            arr.append(i)
        else:
            i=i+1
    for k in arr:
        df.loc[len(df)] = [k, 'Homicide', 0]
    df = df.sort_values(by='Month')
    print(df.to_string(index=False))

    #Increment counter to save file
    global q1_count
    q1_count += 1
    sav_html_str = './Q1-{}.png'.format(q1_count)

    #Plot the bar graph and save the figure
    plot = df.plot.bar(x="Month")
    plt.plot()
    plt.savefig(sav_html_str)
    plt.show()
    plt.close()

    conn.close()
    main_query(database_name)
# ================================================================================
# // Q2
#   Prompt user for an integer N
#   Show the N-most populous and N-least populous neighbourhoods w/ population count
# ================================================================================
def q2(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    #Get user input
    n_areas = int(input("Enter number of locations:"))
    #Create base for map
    m = folium.Map(location=[53.5444,-113.323], zoom_start=11)
    sql_top_bot = '''
            SELECT p.Neighbourhood_Name, c.Latitude, c.Longitude, (CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE) as Total
            FROM population p, coordinates c
            WHERE p.Neighbourhood_name = c.Neighbourhood_name and total > 0 and c.Latitude != 0 and c.Longitude != 0
            ORDER BY Total
        '''
    #Extra the top N populous and bottom N least populous
    data = pd.read_sql_query(sql_top_bot,conn)
    top_n = data.nlargest(n_areas,'Total',keep='all')
    bot_n = data.nsmallest(n_areas,'Total',keep='all')
    ############
    #IF NEED TO TEST PRINT
    print(top_n)
    print(bot_n)
    ############
    #Iterate through least populous and plot on map
    for i in range(n_areas):
        folium.Circle(
            location=[bot_n.iloc[i]['Latitude'], bot_n.iloc[i]['Longitude']],
            popup=bot_n.iloc[i]['Neighbourhood_Name'] + '\n' + str(bot_n.iloc[i]['Total']),
            radius = int(bot_n.iloc[i]['Total']) * 1.1,
            color = 'green',
            fill = True,
            fill_color='blue',
        ).add_to(m)
    #Iterate through most populous and plot on map
    for i in range(n_areas):
        folium.Circle(
            location=[top_n.iloc[i]['Latitude'], top_n.iloc[i]['Longitude']],
            popup=top_n.iloc[i]['Neighbourhood_Name'] + '\n' + str(top_n.iloc[i]['Total']),
            radius = int(top_n.iloc[i]['Total']) * 0.1,
            color = 'crimson',
            fill = True,
            fill_color='red',
        ).add_to(m)
    #Increment counter and save file to disk
    global q2_count
    q2_count += 1
    sav_html_str = 'Q2-{}.html'.format(q2_count)
    m.save(sav_html_str)
    conn.close()
    main_query(database_name)
# ================================================================================
# // Q3
#   Prompt to enter range of years, crime type and an integer N
#   Show the map with Top-N neighbourhoods and crime count w/ respect to given
#   crime type and year range.
# ================================================================================
def q3(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    #Get user input
    strt_year = int(input("Enter start year (YYYY):"))
    end_year = int(input("Enter end_year (YYYY):"))
    crime_type = str(input("Enter crime type:"))
    number_nbhd = int(input("Enter number of neighbourhoods:"))

    #Query to select crime counts of the given crime type in the year range.
    sql_statement = '''SELECT neighbourhood_name, sum(incidents_count) as total_incidents  
    from crime_incidents
    where crime_type = '%s'
    and year between %d and %d
    group by neighbourhood_name
    order by total_incidents desc''' % (crime_type, strt_year, end_year)

    #Extract the top n neighbourhoods with the highest crime counts of the given crime type.
    test1 = pd.read_sql_query(sql_statement, conn)
    rows = test1.nlargest(number_nbhd,'total_incidents',keep='all')
    new = rows.iloc[:, 0]

    #Join table, to get coordinates to top n neighbourhoods
    universe = pd.read_sql_query('''Select * from coordinates''', conn)
    result = pd.merge(rows, universe, on = 'Neighbourhood_Name')

    ############
    #IF NEED TO TEST PRINT
    print(result)
    ############

    #Plot top n neighbourhoods on map
    map =folium.Map(location=[result['Latitude'].mean(),result['Longitude'].mean()], zoom_start=14)
    for row in result.head().itertuples():
        folium.Circle(
            location = [row.Latitude, row.Longitude],
            popup = "{} <br> {} ".format(row.Neighbourhood_Name, row.total_incidents),
            radius = (45*(row.total_incidents//50)),
            color = 'crimson',
            fill = True,
            fill_color = 'crimson'
        ).add_to(map)
        
    #Increment counter and save file to disk
    global q3_count
    q3_count += 1
    sav_html_str = 'Q3-{}.html'.format(q3_count)
    map.save(outfile=sav_html_str)

    conn.close()
    main_query(database_name)
# ================================================================================
# // Q4
#   Prompt to enter range of years and an integer N.
#   Show a map with Top-N neighbourhoods with highest crimes/population ratio
#   as well as most frequent crime type in the neighbourhoods.
# ================================================================================
def q4(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    #Create base map
    m = folium.Map(location=[53.5444,-113.323], zoom_start=11)
    #Gather user input
    strt_year = int(input("Enter start year (YYYY):"))
    end_year = int(input("Enter end_year (YYYY):"))
    number_nbhd = int(input("Enter number of neighbourhoods:"))

    #Query to get population count
    start_statement = '''select neighbourhood_name, (canadian_citizen+ non_canadian_citizen+ no_response) as population_count 
    from population 
    where population_count!=0
    group by neighbourhood_name;'''
    population = pd.read_sql_query(start_statement,conn)
    #Query to get total crime incidents
    sql_statement = '''SELECT neighbourhood_name, sum(incidents_count) as total_incidents  
    from crime_incidents
    where year between %d and %d
    group by neighbourhood_name
    order by total_incidents''' % (strt_year, end_year)

    #Calculate the ratio crimes/population for each neighbourhood
    crimes = pd.read_sql_query(sql_statement, conn)
    crimes = pd.merge(crimes, population, on = 'Neighbourhood_Name')
    crimes['ratio'] = crimes['total_incidents']/crimes['population_count']
    crimes = crimes.sort_values(['ratio'], ascending=[False])
    # print(crimes.to_string(index = False))

    listone = ['Neighbourhood_Name', 'ratio']
    result= crimes[[col for col in listone if col in crimes.columns]]
    result = result.iloc[:number_nbhd, :]

    #Get most frequent crime types in each neighbourhood
    parent = '''SELECT neighbourhood_name,crime_type, sum(incidents_count) as total_incidents  from crime_incidents
    where year between %d and %d
    group by neighbourhood_name, crime_type
    order by neighbourhood_name asc, total_incidents desc''' % (strt_year, end_year)

    #Extract the most frequent crime type from each neighbourhood
    dummy = pd.read_sql_query(parent, conn)
    dummy = dummy.groupby("Neighbourhood_Name").head(1)
    list = ['Neighbourhood_Name', 'Crime_Type', 'ratio']
    dummy = pd.merge(result, dummy, on="Neighbourhood_Name")
    semi_final=dummy[[col for col in list if col in dummy.columns]]

    #Perform a join to get coordinates for selected neighbourhoods.
    coordinate_query = '''select * from coordinates'''
    coord = pd.read_sql_query(coordinate_query, conn)
    coord = pd.merge(semi_final, coord, on='Neighbourhood_Name')
    list = ['Neighbourhood_Name', 'Crime_Type', 'ratio', 'Latitude', 'Longitude']
    final=coord[[col for col in list if col in coord.columns]]
    ############
    #IF NEED TO TEST PRINT
    print(final)
    ############
    #Plot the neighbourhoods on map
    for row in final.head().itertuples():
        folium.Circle(
            location = [row.Latitude, row.Longitude],
            popup = "{} <br> {} <br> {}".format(row.Neighbourhood_Name, row.Crime_Type, row.ratio),
            radius = (1500*(row.ratio)),
            color = 'crimson',
            fill = True,
            fill_color = 'crimson'
        ).add_to(m)
    
    #Increment counter and save file to disk
    global q4_count
    q4_count += 1
    sav_html_str = 'Q4-{}.html'.format(q4_count)
    m.save(sav_html_str)

    conn.close()
    main_query(database_name)
main()