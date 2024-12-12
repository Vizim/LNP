

# **POC for Flyway with Oracle Database in Docker**

### **Step 1: Pull the Oracle Docker Image & Do First Time Config**

First, pull the Oracle-free Docker image from Docker Hub:

```bash
docker pull gvenzl/oracle-free
```

Run the Docker container, mapping the database port to `1521` and setting the Oracle password:

```bash
docker run -d -p 1521:1521 -e ORACLE_PASSWORD=123 gvenzl/oracle-free
```

- **Explanation**:
  - `-d`: Runs the container in detached mode.
  - `-p 1521:1521`: Maps the container's internal port `1521` to the host’s port `1521`.
  - `-e ORACLE_PASSWORD=123`: Sets the Oracle system password.

---

### **Step 2: Optional - Start the Database with an Exported Volume**

If you have a pre-configured volume, you can start the container with it initialized:

```bash
docker run -d -p 1521:1521 -e ORACLE_PASSWORD=<your password> -v oracle-volume:/opt/oracle/oradata gvenzl/oracle-free
```

This mounts the `oracle-volume` to the container's data directory.

---

### **Step 3: Reset the Oracle Password (Optional)**

To reset the Oracle password, run:

```bash
docker exec <container name|id> resetPassword 123
```

Replace `<container name|id>` with your container's name or ID.

---

### **Step 4: Generate Fake Data**

You can generate fake data using a Python script. Assuming you have the script, run:

```bash
python3 ~/Your/DataPath/Generate_Fake_data.py
```

---

### **Step 5: Access the Docker Container Shell**

To access the container's shell:

```bash
docker exec -it <container name|id> /bin/bash
```

Once inside the shell, you can list files and create a directory for your local files:

```bash
mkdir temp
ls
```

---

### **Step 6: Create Fake Data Objects in the Database**

Inside the container, copy the CSV file and run the SQL script to create fake data objects. For example:

```bash
docker cp /path/to/your/data.csv <container_name>:/tmp/
sqlplus SYSTEM/123@database @/home/user/scripts/create_fake_data_1.sql
```

---

### **Step 7: Load Data from CSV into Oracle Database**

Use SQL\*Loader (`sqlldr`) to load data from a CSV file:

```bash
sqlldr userid=SYSTEM/123@localhost:1521/FREEPDB1 control=/opt/oracle/temp/fake_data1.ctl log=data.log
```

- **Explanation**:
  - `userid=SYSTEM/123@localhost:1521/FREEPDB1`: Connects to the Oracle database with the SYSTEM user and password.
  - `control=/opt/oracle/temp/fake_data1.ctl`: Specifies the control file for the data.
  - `log=data.log`: Creates a log file for the loading process.

---

### \*\*Repeat steps

### **Step 8: Install and Configure Flyway**

1. **Download Flyway**:

   - Go to the [Flyway website](https://flywaydb.org/download) and download the appropriate version.
   - Extract the archive to your desired location.

2. **Configure Flyway for Oracle Database**:

   - Open the `flyway.conf` file in the `conf` folder.
   - Modify the connection details:

   ```properties
   flyway.url=jdbc:oracle:thin:@localhost:1521:FREEPDB1
   flyway.user=SYSTEM
   flyway.password=123
   ```

   - You may need to download the Oracle JDBC driver and place it in the `flyway/drivers` directory. The driver can be found [here](https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html).

---

### **Step 9: Create Flyway Migration Scripts**

1. Create migration scripts and place them in the `flyway/sql` directory.

   - Example: `V1__initial_schema.sql`, `V2__add_new_table.sql`

2. Example `V1__initial_schema.sql`:

   ```sql
   CREATE TABLE employees (
       id INT PRIMARY KEY,
       name VARCHAR(100),
       email VARCHAR(100),
       hire_date DATE
   );
   ```

---

### **Step 10: Run Flyway Migrations**

1. Open a terminal and navigate to the Flyway installation directory.
2. Run the migration command:

   ```bash
   ./flyway migrate
   ```

   - Flyway will apply all new migration scripts to the database.

---

### **Step 11: Verify the Setup**

1. Check the Flyway log to ensure migrations were applied successfully.
2. Query the `flyway_schema_history` table in Oracle to view the applied migrations:

   ```sql
   SELECT * FROM flyway_schema_history;
   ```

---

### **Additional Notes**

- If using Docker, ensure that Flyway can connect to the Oracle container, which may require setting up a network bridge.
- Avoid using the `SYSTEM` user for Flyway in production. Instead, create a dedicated schema user:

  ```sql
  CREATE USER flyway_user IDENTIFIED BY flyway_password;
  GRANT CONNECT, RESOURCE TO flyway_user;
  ```

# Docker Compose and Full Database Migration

To integrate Docker Compose for managing the Oracle database and Flyway migrations, you can define a setup that will recreate the database, apply the migrations, and inject new data. Below are the additional steps for configuring a `docker-compose.yml` file to achieve this.

---

### **Step 1: Create a `docker-compose.yml` File**

Create a `docker-compose.yml` file that will set up the Oracle database container, configure Flyway for migrations, and inject new data.

```yaml
version: "3.8"

services:
  oracle:
    image: gvenzl/oracle-free
    container_name: oracle_db
    environment:
      - ORACLE_PASSWORD=123
    ports:
      - "1521:1521"
    volumes:
      - oracle-data:/opt/oracle/oradata
    networks:
      - oracle_network

  flyway:
    image: flyway/flyway
    container_name: flyway_migrations
    environment:
      - FLYWAY_URL=jdbc:oracle:thin:@oracle_db:1521/FREEPDB1
      - FLYWAY_USER=SYSTEM
      - FLYWAY_PASSWORD=123
    command: "migrate"
    depends_on:
      - oracle
    volumes:
      - ./sql:/flyway/sql
    networks:
      - oracle_network

  data_injection:
    image: python:3.8
    container_name: data_injection
    environment:
      - DATABASE_URL=jdbc:oracle:thin:@oracle_db:1521/FREEPDB1
      - DATABASE_USER=SYSTEM
      - DATABASE_PASSWORD=123
    volumes:
      - ./data:/data
      - ./scripts:/scripts
    command: "python3 /scripts/inject_data.py"
    depends_on:
      - oracle
    networks:
      - oracle_network

networks:
  oracle_network:
    driver: bridge

volumes:
  oracle-data:
```

---

### **Step 2: Explanation of the `docker-compose.yml`**

1. **Oracle Service (`oracle`)**:

   - Uses the `gvenzl/oracle-free` image to run Oracle in a container.
   - Maps the internal port `1521` to the host machine for database access.
   - Uses a named volume (`oracle-data`) to persist Oracle data.
   - Sets the `ORACLE_PASSWORD` environment variable to initialize the database with a password.

2. **Flyway Service (`flyway`)**:

   - Uses the official Flyway image (`flyway/flyway`) for database migrations.
   - Runs the `migrate` command to apply all available migrations.
   - Depends on the Oracle service, so it will wait for Oracle to be ready before running migrations.
   - Mounts the `./sql` directory (where your Flyway SQL scripts are stored) to the `/flyway/sql` directory in the Flyway container.

3. **Data Injection Service (`data_injection`)**:

   - Uses the `python:3.8` image to run a Python script that injects data into the Oracle database.
   - The script (`inject_data.py`) should handle data injection, and the environment variables `DATABASE_URL`, `DATABASE_USER`, and `DATABASE_PASSWORD` can be used in your script for database access.
   - Mounts the `./data` directory (containing any CSV or other data files you want to inject) and the `./scripts` directory (where the Python script is located).

4. **Networks**:

   - Creates a custom network (`oracle_network`) to allow the services to communicate with each other (Oracle, Flyway, and Data Injection).

5. **Volumes**:
   - A named volume (`oracle-data`) is used to persist the Oracle database's data so that it isn't lost when the container is restarted or recreated.

---

### **Step 3: Organize Your Project Files**

Ensure your project directory contains the following structure:

```
project/
│
├── data/                     # Contains CSV or other data files to inject
│   └── data.csv
│
├── scripts/                  # Contains Python scripts for data injection
│   └── inject_data.py        # Python script to inject data into Oracle DB
│
├── sql/                      # Contains Flyway migration scripts
│   └── V1__initial_schema.sql
│   └── V2__add_fake_data.sql
│
└── docker-compose.yml        # Docker Compose configuration file
```

- **`data.csv`**: This is your data file that will be injected into the Oracle database.
- **`inject_data.py`**: A Python script that reads `data.csv` and inserts data into the Oracle database using `cx_Oracle` or other libraries. The script can use environment variables for database connection.

---

### **Step 4: Example Python Script to Inject Data (`inject_data.py`)**

```python
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
```

---

### **Step 5: Bringing Up the Services with Docker Compose**

Run the following command in the directory where your `docker-compose.yml` file is located:

```bash
docker-compose up --build
```

- This command will:
  1. Create and start the Oracle container.
  2. Wait for Oracle to be ready, then apply the Flyway migrations.
  3. Once the migrations are applied, the data injection script will run, inserting the new data into the database.

---

### **Step 6: Verify the Setup**

1. **Check the Logs**: Monitor the logs of the running services to ensure that everything is working correctly.
   - For Flyway migrations: `docker logs flyway_migrations`
   - For data injection: `docker logs data_injection`
2. **Query the Database**: After the setup is complete, you can log into Oracle to verify the migrations and data:

   ```sql
   SELECT * FROM employees;
   ```

---

### **Step 7: Cleanup (Optional)**

To tear down the services and remove the containers:

```bash
docker-compose down -v
```

This will stop the containers and remove any volumes (including the Oracle database data).

---

### **Additional Notes**

- You may need to install the `cx_Oracle` library in the Python container for the data injection script to work:

  ```bash
  pip install cx_Oracle
  ```

- If you're using a custom database user for Flyway migrations or data injection, ensure that the appropriate permissions are granted.

---
