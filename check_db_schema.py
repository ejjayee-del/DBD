import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check the structure of the certificaterequest table
cursor.execute("PRAGMA table_info(certificates_certificaterequest);")
columns = cursor.fetchall()

print("CertificateRequest table columns:")
for col in columns:
    print(f"  {col[1]} - {col[2]} {'NULL' if col[3] else 'NOT NULL'} {'PRIMARY KEY' if col[5] else ''}")

conn.close()