import os
import json
import psycopg2
from sqlalchemy import create_engine
from src.src_context import root_dir
from dotenv import load_dotenv
import numpy as np
import vertica_python


# psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)
""" decrypt the database details"""
load_dotenv(os.path.join(root_dir, ".env"))


def db_connection():
    connection = psycopg2.connect(
        host=os.getenv("db_host"),
        user=os.getenv("db_user"),
        port=5432,
        password=os.getenv("db_passwd"),
        database=os.getenv("dbname"),
    )
    return connection


def engine():
    conn = create_engine(
        "postgresql://{username}:{password}@{host}:5432/{database}".format(
            username=os.getenv("db_user"),
            password=os.getenv("db_passwd"),
            host=os.getenv("db_host"),
            database=os.getenv("dbname"),
        )
    )
    return conn


