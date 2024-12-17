# POC FOR FlyWay

### Step 1: Pull the Oracle Docker Image & Do First Time Config

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

### Step 3: Optional - Start the Database with an Exported Volume

If you have a pre-configured volume, you can start the container with it initialized. For example:

```bash
docker run -d -p 1521:1521 -e ORACLE_PASSWORD=<your password> -v oracle-volume:/opt/oracle/oradata gvenzl/oracle-free
```

This mounts the `oracle-volume` to the container's data directory.

---

```bash
docker exec <container name|id> resetPassword 123
```

Replace `<container name|id>` with your container's name or ID.

---

### Step 5: Generate Fake Data

Generate fake data using a Python script. Assuming you have a Python script to generate the data:

```bash
python3 ~/Your/DataPath/Generate_Fake_data.py
```

---

### Step 6: Access the Docker Container Shell

To access the container's shell, use the following command:

```bash
docker exec -it <container name|id> /bin/bash
```

Once inside the shell, you can list files to ensure you are in the correct directory go ahead and create a directory for your source files you generated locally:

```bash
mkdir temp
```

```bash
ls
```

You should see output similar to:

```bash
admin cfgtoollogs createAppUser diag oraInventory product temp
audit container-entrypoint.sh createDatabase healthcheck.sh oradata resetPassword
```

Going back to the local shell go ahead import
the following file

---

### Step 7: Create Fake Data Objects in the Database

Inside the container, run the SQL script to create fake data objects. Use `sqlplus` with the Oracle SYSTEM user:

docker cp /path/to/your/data.csv stupefied_swan:/tmp/

```bash
sqlplus SYSTEM/123@database @/home/user/scripts/create_fake_data_1.sql
```

---

### Step 8: Load Data from CSV into Oracle Database

Use `sqlldr` (SQL\*Loader) to load data from a CSV file into the Oracle database. This requires a control file and a log file for tracking:

```bash
sqlldr userid=SYSTEM/123@localhost:1521/FREEPDB1 control=/opt/oracle/temp/fake_data1.ctl log=data.log
```

- **Explanation**:
  - `userid=SYSTEM/123@localhost:1521/FREEPDB1`: Connects to the Oracle database with the SYSTEM user and password.
  - `control=/opt/oracle/temp/fake_data1.ctl`: Specifies the control file that defines the structure of the data to be loaded.
  - `log=data.log`: Generates a log file for the loading process.

---

172.17.0.2
To install and set up **Flyway** for use with an Oracle Database, follow these steps:

---

### Step 1: Download Flyway

1. Go to the [official Flyway website](https://flywaydb.org/download) and download the Flyway Community or Enterprise Edition (depending on your needs).
2. Extract the downloaded archive to a desired location on your system.

---

### Step 2: Configure Flyway for Oracle Database

1. Navigate to the Flyway installation directory.
2. Open the `conf/flyway.conf` file for editing.
3. Add or modify the following configuration details for connecting to your Oracle database:

   ```properties
   flyway.url=jdbc:oracle:thin:@localhost:1521:FREEPDB1
   flyway.user=SYSTEM
   flyway.password=123
   ```

   - **`flyway.url`**: Specifies the JDBC connection string for Oracle. Adjust `localhost`, `1521`, and `FREEPDB1` if your Oracle DB is running elsewhere or under a different service name.
   - **`flyway.user`** and **`flyway.password`**: Replace these with the credentials for the database user (preferably not `SYSTEM` in production).

   > **Note**: You may need to download the Oracle JDBC driver and place it in the `flyway/drivers` directory. You can find it in the [Oracle JDBC Downloads](https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html). Make sure to match the driver version to your database.

---

### Step 3: Create Flyway Migration Scripts

1. Flyway requires migration scripts to be placed in the `sql` folder under the `flyway` directory (`flyway/sql` by default).
2. Each migration script must follow Flyway's naming conventions:

   - Example: `V1__initial_schema.sql`, `V2__add_new_table.sql`
   - Scripts should include SQL commands for schema changes, data inserts, etc.

   Example `V1__initial_schema.sql`:

   ```sql
   CREATE TABLE employees (
       id INT PRIMARY KEY,
       name VARCHAR(100),
       email VARCHAR(100),
       hire_date DATE
   );
   ```

---

### Step 4: Run Flyway Migrations

1. Open a terminal and navigate to the Flyway installation directory.
2. Run the following command to apply the migrations:
   ```bash
   ./flyway migrate
   ```
   - Flyway will connect to the Oracle database, check the `flyway_schema_history` table (created automatically), and apply any new migration scripts.

---

### Step 5: Verify the Setup

1. Check the Flyway log output to ensure migrations were applied successfully.
2. You can also log into your Oracle database and query the `flyway_schema_history` table to see the applied migrations:
   ```sql
   SELECT * FROM flyway_schema_history;
   ```

---

### Additional Notes

- If you're working in a Dockerized environment, ensure Flyway can connect to the Oracle container. This might involve setting up a network bridge between Flyway's container (if you run Flyway in a container) and the Oracle container.
- For testing purposes, avoid running Flyway with the `SYSTEM` user. Create a dedicated schema user for Flyway migrations.
  ```sql
  CREATE USER flyway_user IDENTIFIED BY flyway_password;
  GRANT CONNECT, RESOURCE TO flyway_user;
  ```

Let me know if you need help with any specific part!


================================================================


My goal is todo the following: 

1. I need to pull down docker image genzvel/oracle-free, load in two csv files that are locally stored on my computer. I have a create_fake_data1.sql file and fake_data1.csv file
2. I then need to edit the docker cotainer so that the oracle database has  flyway installed on it with the correct schema.  
3. I then need to use kind to create and load that oracle img that I just created into kind but I need to do this will terraform. 