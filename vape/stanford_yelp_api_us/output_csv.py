import sqlite3
import csv

def main():
    us_states_and_territories = set(('AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO',
                                     'CT', 'DK', 'DE', 'DC', 'FL', 'GA', 'GU',
                                     'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY',
                                     'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
                                     'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM',
                                     'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR',
                                     'OL', 'PA', 'PI', 'PR', 'RI', 'SC', 'SD',
                                     'TN', 'TX', 'UT', 'VT', 'VI', 'VA', 'WA',
                                     'WV', 'WI', 'WY'))

    state_codes = us_states_and_territories

    state_code_sql = ','.join(["'"+state+"'" for state in state_codes])

    seen_ids = set()
    conn = sqlite3.connect('test_us.db')

    c = conn.cursor()
    with open('us.csv', 'w') as csvfile:
        fieldnames = ('yelp_id','name','phone','address_line1', 'address_line2','address_line3','city','postal_code','state_code','is_closed','review_count','rating','store_types','url')

        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        i=0
        for row in c.execute('SELECT * FROM entries WHERE state_code IN ('+state_code_sql+') ORDER BY postal_code'):
            row = list(row)

            row[0] = row[0].split('?')[0]
            if row[0] in seen_ids:
                continue
            #remove yelp url
            row.pop(-2)

            #convert numbers to strings
            row[-7] = str(row[-7])
            row[-6] = str(row[-6])
            row[-5] = str(row[-5])

            row = [x if x is not None else '' for x in row]
            print(row)
            writer.writerow(row)
            i+=1
            seen_ids.add(row[0])
        print(i)
        i=0
        for row in c.execute('SELECT * FROM search_entries WHERE state_code IN ('+state_code_sql+') ORDER BY postal_code'):
            row = list(row)

            row[0] = row[0].split('?')[0]
            if row[0] in seen_ids:
                continue
            #convert numbers to strings
            row[-7] = str(row[-7])
            row[-6] = str(row[-6])
            row[-5] = str(row[-5])

            if 'Vape Shops' not in row[-4:-1]:
                continue

            print(row)
            #remove yelp url
            writer.writerow([s.encode("utf-8") for s in row])
            i+=1
            seen_ids.add(row[0])
        print(i)


if __name__ == '__main__':
    main()
