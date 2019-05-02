from flask import Flask, request, render_template
import sqlite3
import matplotlib, os
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import folium

def startup():

    try:
        name = input("Name of the database you will use")
        check_connection = 'file:{}.db?mode=rw'.format(name)
        conn = sqlite3.connect(check_connection, uri=True)
        database_name = "./{}.db".format(name)
        print("Edmonton Public Crime Database")
        global dbname
        dbname = database_name
        if __name__ == '__main__':
            app.run(debug=False)

    except sqlite3.OperationalError:
        #If database DNE print out error
        print("database doesn't exist")
        exit(0)



app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query1')
def query1():
    return render_template('query1.html')

@app.route('/query2')
def query2():
    return render_template('query2.html')

@app.route('/query3')
def query3():
    return render_template('query3.html')

@app.route('/query4')
def query4():
    return render_template('query4.html')



@app.route('/query1', methods=['GET', 'POST'])
def q1():

    if request.method == 'POST':
        conn = sqlite3.connect(dbname)
        c = conn.cursor()
        strt_year = int(request.form["start_year"])
        end_year = int(request.form["end_year"])
        crime_type = str(request.form["type_crime"])

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
        plot = df.plot.bar(x="Month")
        plt.plot()
        i = 1

        while os.path.exists("static/q1-{}.png".format(i)):
            i += 1

        plt.savefig('static/q1-{}.png'.format(i))
        filename = 'static/q1-{}.png'.format(i)
        conn.close()
        return render_template('plot.html', val=filename)



@app.route('/query2', methods = ['GET', 'POST'])
def q2():
    if request.method == 'POST':
        conn = sqlite3.connect(dbname)
        c = conn.cursor()
        n_areas = int(request.form["number"])
        m = folium.Map(location=[53.5444, -113.323], zoom_start=11)
        sql_top_bot = '''
                    SELECT p.Neighbourhood_Name, c.Latitude, c.Longitude, (CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE) as Total
                    FROM population p, coordinates c
                    WHERE p.Neighbourhood_name = c.Neighbourhood_name and total > 0 and c.Latitude != 0 and c.Longitude != 0
                    ORDER BY Total
                '''
        data = pd.read_sql_query(sql_top_bot, conn)
        top_n = data.nlargest(n_areas, 'Total', keep='all')
        bot_n = data.nsmallest(n_areas, 'Total', keep='all')
        # print(top_n)
        # print(bot_n)
        for i in range(n_areas):
            folium.Circle(
                location=[bot_n.iloc[i]['Latitude'], bot_n.iloc[i]['Longitude']],
                popup=bot_n.iloc[i]['Neighbourhood_Name'] + '\n' + str(bot_n.iloc[i]['Total']),
                radius=int(bot_n.iloc[i]['Total']) * 1.1,
                color='green',
                fill=True,
                fill_color='blue',
            ).add_to(m)
        for i in range(n_areas):
            folium.Circle(
                location=[top_n.iloc[i]['Latitude'], top_n.iloc[i]['Longitude']],
                popup=top_n.iloc[i]['Neighbourhood_Name'] + '\n' + str(top_n.iloc[i]['Total']),
                radius=int(top_n.iloc[i]['Total']) * 0.1,
                color='crimson',
                fill=True,
                fill_color='red',
            ).add_to(m)
        i = 1
        while os.path.exists("templates/q2-{}.html".format(i)):
            i += 1

        m.save('templates/q2-{}.html'.format(i))
        conn.close()
        return render_template('q2-{}.html'.format(i))






@app.route('/query3', methods = ['GET', 'POST'])
def q3():
    if request.method == 'POST':
        strt_year = int(request.form["start_year"])
        end_year = int(request.form["end_year"])
        number_nbhd = int(request.form["number"])
        crime_type = request.form["type"]

        conn = sqlite3.connect(dbname)
        c = conn.cursor()

        sql_statement = '''SELECT neighbourhood_name, sum(incidents_count) as total_incidents  
        from crime_incidents
        where crime_type = '%s'
        and year between %d and %d
        group by neighbourhood_name
        order by total_incidents desc''' % (crime_type, strt_year, end_year)

        test1 = pd.read_sql_query(sql_statement, conn)
        rows = test1.nlargest(number_nbhd, 'total_incidents', keep='all')

        universe = pd.read_sql_query('''Select * from coordinates''', conn)
        result = pd.merge(rows, universe, on='Neighbourhood_Name')
        print(result)
        map = folium.Map(location=[result['Latitude'].mean(), result['Longitude'].mean()], zoom_start=14)

        for row in result.head().itertuples():
            folium.Circle(
                location=[row.Latitude, row.Longitude],
                popup="{} <br> {} ".format(row.Neighbourhood_Name, row.total_incidents),
                radius=(45 * (row.total_incidents // 50)),
                color='crimson',
                fill=True,
                fill_color='crimson'
            ).add_to(map)
        i = 1
        while os.path.exists("templates/q3-{}.html".format(i)):
            i += 1

        map.save('templates/q3-{}.html'.format(i))
        conn.close()
        return render_template('q3-{}.html'.format(i))


@app.route('/query4', methods = ['GET', 'POST'])
def q4():
    if request.method == 'POST':
        strt_year = int(request.form["start_year"])
        end_year = int(request.form["end_year"])
        number_nbhd = int(request.form["number"])

        conn = sqlite3.connect(dbname)
        m = folium.Map(location=[53.5444,-113.323], zoom_start=11)
        c = conn.cursor()

        start_statement = '''select neighbourhood_name, (canadian_citizen+ non_canadian_citizen+ no_response) as population_count 
        from population 
        where population_count!=0
        group by neighbourhood_name;'''
        population = pd.read_sql_query(start_statement, conn)

        sql_statement = '''SELECT neighbourhood_name, sum(incidents_count) as total_incidents  
        from crime_incidents
        where year between %d and %d
        group by neighbourhood_name
        order by total_incidents''' % (strt_year, end_year)

        crimes = pd.read_sql_query(sql_statement, conn)

        crimes = pd.merge(crimes, population, on='Neighbourhood_Name')
        crimes['ratio'] = crimes['total_incidents'] / crimes['population_count']
        crimes = crimes.sort_values(['ratio'], ascending=[False])
        # print(crimes.to_string(index = False))

        listone = ['Neighbourhood_Name', 'ratio']
        result = crimes[[col for col in listone if col in crimes.columns]]
        result = result.iloc[:number_nbhd, :]

        parent = '''SELECT neighbourhood_name,crime_type, sum(incidents_count) as total_incidents  from crime_incidents
        where year between %d and %d
        group by neighbourhood_name, crime_type
        order by neighbourhood_name asc, total_incidents desc''' % (strt_year, end_year)

        dummy = pd.read_sql_query(parent, conn)
        dummy = dummy.groupby("Neighbourhood_Name").head(1)
        list = ['Neighbourhood_Name', 'Crime_Type', 'ratio']
        dummy = pd.merge(result, dummy, on="Neighbourhood_Name")
        semi_final = dummy[[col for col in list if col in dummy.columns]]

        coordinate_query = '''select * from coordinates'''
        coord = pd.read_sql_query(coordinate_query, conn)
        coord = pd.merge(semi_final, coord, on='Neighbourhood_Name')
        list = ['Neighbourhood_Name', 'Crime_Type', 'ratio', 'Latitude', 'Longitude']
        final = coord[[col for col in list if col in coord.columns]]
        print(final)
        for row in final.head().itertuples():
            folium.Circle(
                location=[row.Latitude, row.Longitude],
                popup="{} <br> {} <br> {}".format(row.Neighbourhood_Name, row.Crime_Type, row.ratio),
                radius=(1500 * (row.ratio)),
                color='crimson',
                fill=True,
                fill_color='crimson'
            ).add_to(m)
        i = 1
        while os.path.exists("templates/q4-{}.html".format(i)):
            i += 1

        m.save('templates/q4-{}.html'.format(i))
        conn.close()
        return render_template('q4-{}.html'.format(i))

startup()
