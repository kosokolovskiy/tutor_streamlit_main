from pymongo import MongoClient
import os
import mysql.connector
import streamlit as st
from urllib.parse import quote_plus

def create_connection(database_name: str) -> MongoClient:
    uri = os.getenv("MONGO_URI")
    if not uri:
        user = os.environ["DB_USERNAME"]
        pwd  = quote_plus(os.environ["DB_PASSWORD"])
        host = os.getenv("MONGO_HOST", "ec2-3-67-163-253.eu-central-1.compute.amazonaws.com")
        port = int(os.getenv("MONGO_PORT", "27017"))

        auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")
        replica_set = os.getenv("MONGO_REPLICA_SET", "rs0")

        uri = (
            f"mongodb://{user}:{pwd}@{host}:{port}/"
            f"?authSource={auth_source}&replicaSet={replica_set}"
        )

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client



def create_connection_sql(db_name):

    rds_endpoint = os.environ["RDS_ENDPOINT"]
    username = os.environ["SQL_USERNAME"]
    password = os.environ["SQL_PASSWORD"]


    connection = mysql.connector.connect(
            host=rds_endpoint,
            user=username,
            password=password,
            port=3306,
            connect_timeout=10,
            database=db_name
        )

    return connection, connection.cursor()


def make_request(req, db_name):
    connection, cursor = create_connection_sql(db_name)
    cursor.execute(req)
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    return res