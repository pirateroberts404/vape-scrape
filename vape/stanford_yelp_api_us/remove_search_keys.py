import sqlite3
import urllib.parse


db_name = 'test_us.db'
conn = sqlite3.connect(db_name)
c = conn.cursor()

c.execute('SELECT * FROM search_names;')

names = c.fetchall()

set_names = set()
for name in names:
    set_names.add(urllib.parse.urlparse(name[0]).path)

print(len(names))
print(len(set_names))

c.execute('DELETE FROM search_names;')

for name in set_names:
    c.execute('INSERT INTO search_names VALUES (?)', (name,))

conn.commit()
