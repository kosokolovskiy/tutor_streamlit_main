from pymongo import MongoClient
import os
import mysql.connector



def create_connection(database_name):
    """Creates and returns a MongoDB client for the specified database.
    
    This function establishes a connection to a MongoDB server using credentials from environment variables.

    Args:
        database_name (str): The name of the MongoDB database to connect to.

    Returns:
        MongoClient: A client instance connected to the specified MongoDB database.
    """
    host = "3.79.153.33"
    port = 27017
    username = os.environ["db_username"]
    password = os.environ["db_password"] 

    print('AGAIN')
    mongo_uri = f"mongodb://{username}:{password}@{host}:{port}/{database_name}"

    try:
        client = MongoClient(mongo_uri)
    except:
        print("ERROR")

    return client

def create_connection_sql(db_name):
    """Creates and returns a MySQL database connection and cursor.

    This function connects to a MySQL database using credentials from environment variables.

    Args:
        db_name (str): The name of the MySQL database to connect to.

    Returns:
        tuple: A tuple containing the MySQL connection object and its cursor.
    """
    rds_endpoint = os.environ["rds_endpoint"]
    username = os.environ["sql_username"]
    password = os.environ["sql_password"]

    connection = mysql.connector.connect(
            host=rds_endpoint,
            user=username,
            password=password,
            port=3306, 
            connect_timeout=5,
            database=db_name
        )

    return connection, connection.cursor()


def make_request(req, db_name):
    """Executes a SQL query on the specified database and returns the results.

    This function creates a connection to a MySQL database, executes the provided query, and returns all fetched results.

    Args:
        req (str): The SQL query to execute.
        db_name (str): The name of the database to connect to.

    Returns:
        list: A list of tuples containing the query results.
    """
    connection, cursor = create_connection_sql(db_name)
    cursor.execute(req)
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    return res