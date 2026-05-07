import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check if there are any records in the certificaterequest table
cursor.execute("SELECT COUNT(*) FROM certificates_certificaterequest;")
count = cursor.fetchone()[0]
print(f"Number of records in CertificateRequest table: {count}")

if count > 0:
    print("Sample records:")
    cursor.execute("SELECT id, requested_by_id, template_id, status, created_date FROM certificates_certificaterequest LIMIT 5;")
    records = cursor.fetchall()
    for record in records:
        print(f"  ID: {record[0]}, Requester: {record[1]}, Template: {record[2]}, Status: {record[3]}, Created: {record[4]}")

conn.close()