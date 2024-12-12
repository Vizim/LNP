import cx_Oracle
import os

# Fetch database connection details from environment variables
db_url = os.getenv('DATABASE_URL', 'jdbc:oracle:thin:@localhost:1521/FREEPDB1')
db_user = os.getenv('DATABASE_USER', 'SYSTEM')
db_password = os.getenv('DATABASE_PASSWORD', '123')

# Connect to the Oracle database
connection = cx_Oracle.connect(user=db_user, password=db_password, dsn=db_url)
cursor = connection.cursor()

# Example: Insert fake data from a CSV file
with open('/data/data.csv', 'r') as file:
    for line in file:
        name, email, hire_date = line.strip().split(',')
        cursor.execute("""
            INSERT INTO employees (name, email, hire_date)
            VALUES (:name, :email, TO_DATE(:hire_date, 'YYYY-MM-DD'))
        """, {'name': name, 'email': email, 'hire_date': hire_date})

# Commit the transaction
connection.commit()

# Close the connection
cursor.close()
connection.close()