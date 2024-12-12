import os
import pandas as pd
from faker import Faker
import random

# Initialize Faker to generate fake data
random.seed(1)
fake = Faker()

# Step 1: Create the first fake dataset
print("Generating the first dataset...")
data1 = {
    'Name': [fake.name() for _ in range(10)],
    'Email': [fake.email() for _ in range(10)],
    'Phone Number': [fake.phone_number() for _ in range(10)],
    'Address': [fake.address() for _ in range(10)],
    'Birthdate': [fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d') for _ in range(10)],
    'Company': [fake.company() for _ in range(10)],
    'Credit Card Number': [fake.credit_card_number(card_type=None) for _ in range(10)],
    'Favorite Color': [fake.color_name() for _ in range(10)],
    'Website': [fake.url() for _ in range(10)]
}
df1 = pd.DataFrame(data1)
print("First dataset generated.")
df1.head()

# Step 2: Create the second fake dataset with one column difference
print("Generating the second dataset with one fewer column...")
data2 = {
    'Name': [fake.name() for _ in range(10)],
    'Email': [fake.email() for _ in range(10)],
    'Phone Number': [fake.phone_number() for _ in range(10)],
    'Address': [fake.address() for _ in range(10)],
    'Birthdate': [fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d') for _ in range(10)],
    'Company': [fake.company() for _ in range(10)],
    'Favorite Color': [fake.color_name() for _ in range(10)],
    'Website': [fake.url() for _ in range(10)]
}
df2 = pd.DataFrame(data2)
print("Second dataset generated.")
df2.head()

# Step 3: Save the datasets as CSV files in the current working directory
cwd = os.getcwd()
file1_path = os.path.join(cwd, 'fake_data1.csv')
file2_path = os.path.join(cwd, 'fake_data2.csv')

print(f"Saving the first dataset to: {file1_path}")
df1.to_csv(file1_path, index=False)
print("First dataset saved.")

print(f"Saving the second dataset to: {file2_path}")
df2.to_csv(file2_path, index=False)
print("Second dataset saved.")

# Final confirmation
print("Both datasets have been successfully generated and saved in the current working directory.")
