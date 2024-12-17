

---

## Step-by-Step Guide for Oracle Database with Flyway & Terraform

### Step 1: Pull Oracle Docker Image and Run It

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

### Step 2: Generate and Load Fake Data

To generate fake data, you can use a Python script:

```bash
python3 ~/Your/DataPath/Generate_Fake_data.py
```

Then, access the container’s shell:

```bash
docker exec -it <container_name_or_id> /bin/bash
```

Once inside, create a directory to store your local files:

```bash
mkdir temp
ls
```

Now, copy your local data files into the container:

```bash
docker cp /path/to/your/data.csv <container_name_or_id>:/tmp/
```

Execute your SQL script to create the necessary database objects:

```bash
sqlplus SYSTEM/123@database @/home/user/scripts/create_fake_data_1.sql
```

Finally, load data from a CSV file using SQL*Loader:

```bash
sqlldr userid=SYSTEM/123@localhost:1521/FREEPDB1 control=/opt/oracle/temp/fake_data1.ctl log=data.log
```

---

### Step 3: Install Flyway for Schema Management

#### Step 3.1: Download Flyway

1. Download Flyway from the [official Flyway website](https://flywaydb.org/download).
2. Extract it to a desired directory.

#### Step 3.2: Configure Flyway

1. Navigate to the `conf` directory in your Flyway installation.
2. Edit `flyway.conf` and configure it for your Oracle database:

   ```properties
   flyway.url=jdbc:oracle:thin:@localhost:1521:FREEPDB1
   flyway.user=SYSTEM
   flyway.password=123
   ```

   Ensure you have the Oracle JDBC driver in the `flyway/drivers` directory if needed.

#### Step 3.3: Create Migration Scripts

Create migration scripts in the `sql` directory of the Flyway installation:

- Example `V1__initial_schema.sql`:

   ```sql
   CREATE TABLE employees (
       id INT PRIMARY KEY,
       name VARCHAR(100),
       email VARCHAR(100),
       hire_date DATE
   );
   ```

#### Step 3.4: Run Flyway Migrations

In the terminal, navigate to the Flyway installation directory and run the migrations:

```bash
./flyway migrate
```

Check the Flyway log to verify successful migrations.

---

### Step 4: Use Terraform to Create Oracle Docker Container in Kind (Kubernetes)

1. **Create Terraform Configuration**: Write a Terraform configuration file to define the Oracle container in Kind.

   Example `main.tf`:

   ```hcl
   provider "kubernetes" {
     host                   = "https://localhost:6443"
     cluster_ca_certificate = base64decode("<cluster-ca-certificate>")
     token                  = "<service-account-token>"
   }

   resource "kubernetes_pod" "oracle" {
     metadata {
       name = "oracle-db"
     }
     spec {
       container {
         name  = "oracle"
         image = "gvenzl/oracle-free"
         ports {
           container_port = 1521
         }
         env {
           name  = "ORACLE_PASSWORD"
           value = "123"
         }
       }
     }
   }
   ```

2. **Set up Kubernetes Cluster with Kind**:
   Create a Kubernetes cluster with Kind:

   ```bash
   kind create cluster
   ```

3. **Apply Terraform**:

   ```bash
   terraform init
   terraform apply
   ```

This will create the Oracle container inside the Kind Kubernetes cluster using Terraform.

---

### Final Steps: Verify the Setup

- Check the logs for the Flyway migrations.
- Verify that your Oracle container is running in Kind.
- You can query the `flyway_schema_history` table in Oracle to check the migrations:

   ```sql
   SELECT * FROM flyway_schema_history;
   ```

---

Let me know if you need further clarification or assistance with any step!