import pandas as pd
from requests import get
import psycopg2

def bd_to_csv():
    sql_query = "SELECT * FROM feedback"

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database='vk', user='aleksandralekseev', host='localhost', password='')
    #conn = psycopg2.connect(database='vk', user='postgres', host='localhost', password='1712')

    # Create a cursor object
    cursor = conn.cursor()

    # Execute the SQL query
    cursor.execute(sql_query)

    # Fetch all rows from the result set
    rows = cursor.fetchall()

    # Get column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Create a Pandas DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=column_names)

    # Print or use the DataFrame as needed
    df.to_csv('df.csv')

    df.to_excel('df.xlsx')




