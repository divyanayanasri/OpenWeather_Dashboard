import mysql.connector
from mysql.connector import Error

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def get_connection(use_database=True):
    """Open and return a new MySQL connection.

    use_database=False connects to the server only (needed once,
    to create the database itself).
    """
    settings = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }
    if use_database:
        settings["database"] = DB_NAME

    return mysql.connector.connect(**settings)


def init_db():
    """Create the database and the favorites table if they don't exist."""
    # Step 1: create the database
    conn = get_connection(use_database=False)
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.close()
    finally:
        conn.close()

    # Step 2: create the table inside it
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id         INT AUTO_INCREMENT PRIMARY KEY,
                city       VARCHAR(100) NOT NULL,
                country    VARCHAR(2)   NOT NULL DEFAULT '',
                latitude   DECIMAL(9,6) NULL,
                longitude  DECIMAL(9,6) NULL,
                note       VARCHAR(255) NULL,
                created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uq_city_country (city, country)
            )
        """)
        conn.commit()
        cursor.close()
    finally:
        conn.close()


if __name__ == "__main__":
    # Run:  python database.py
    try:
        init_db()
        conn = get_connection()
        print("Connected to MySQL database:", DB_NAME)
        conn.close()
    except Error as err:
        print("Database error:", err)