import sqlite3

def main():

	conn = sqlite3.connect("..//data//weedmaps.db")
	c = conn.cursor()


	c.execute("DROP TABLE store;")
	c.execute("DROP TABLE strain;")

	conn.commit()
	conn.close()


if __name__ == '__main__':
    main()