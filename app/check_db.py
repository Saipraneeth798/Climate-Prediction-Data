import mysql.connector

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='localhost:3306',        # Replace with your MySQL server host
    user='root',    # Replace with your MySQL username
    password='0505', # Replace with your MySQL password
    database='info'  # Replace with your MySQL database name
)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Query to select all records from the members table
cursor.execute("SELECT * FROM members")

# Fetch all rows from the executed query
rows = cursor.fetchall()

# Print the records in the members table
print("members table:")
for row in rows:
    print(row)

# Close the cursor and connection
cursor.close()
conn.close()
