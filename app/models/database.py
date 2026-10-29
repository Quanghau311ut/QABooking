import os
from contextlib import contextmanager

import pyodbc


def get_connection():
    """Create a SQL Server connection from environment configuration."""
    connection_string = os.getenv("SQL_CONNECTION_STRING")
    if not connection_string:
        driver = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
        server = os.getenv("SQL_SERVER", "localhost")
        database = os.getenv("SQL_DATABASE", "QABooking")
        username = os.getenv("SQL_USER")
        password = os.getenv("SQL_PASSWORD")
        encrypt = os.getenv("SQL_ENCRYPT", "yes")
        trust_certificate = os.getenv("SQL_TRUST_SERVER_CERTIFICATE", "yes")

        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Encrypt={encrypt};"
            f"TrustServerCertificate={trust_certificate};"
        )
        if username:
            connection_string += f"UID={username};PWD={password or ''};"
        else:
            connection_string += "Trusted_Connection=yes;"

    return pyodbc.connect(connection_string, timeout=5)


@contextmanager
def connection_scope():
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
