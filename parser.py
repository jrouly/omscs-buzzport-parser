from bs4 import BeautifulSoup
import csv
import pandas
import os


# These are the column headers in the <tbody>, in order.
FIELDNAMES = [
    'Select', 'CRN', 'Subj', 'Crse', 'Sec', 'Cmp', 'Bas', 'Cred',
    'Title', 'Days', 'Time', 'Cap', 'Act', 'Rem', 'WLCap', 'WLAct',
    'WLRem', 'Instructor', 'Location', 'Attribute'
]

# These are the allowed course numbers. This includes both CS and CSE.
ALLOWED_COURSES = [
    6035, 6210, 6220, 6242, 6250, 6262, 6290, 6300, 6310, 6340, 6400, 6440,
    6460, 6475, 6476, 6505, 6601, 6750, 7637, 7641, 7646, 8803
]

# Set up parser.
html = open('input/table.html', 'r')
soup = BeautifulSoup(html, 'html.parser')

# Isolate only the data <td> elements.
rows = [
    td.find_parent('tr').find_all('td')
    for td in soup.find_all('td', class_='dddefault')
]

# Isolate only text within the rows.
rows = [
    [td.text.strip() for td in tr]
    for tr in rows
]

# Filter the weird 'secondary' rows. They all have an empty first column.
rows = [r for r in rows if len(r[0]) > 0]

# Write raw data to intermediate CSV file.
wr = open('table.csv', 'w')
writer = csv.writer(wr, delimiter=',', quoting=csv.QUOTE_ALL)
writer.writerow(FIELDNAMES)
for row in rows:
    writer.writerow(row)

# Close file handlers.
html.close()
wr.close()

# Load up the pandas data frame.
df = pandas.read_csv('table.csv')

# Filter and select only relevant courses.
valid_courses = df[df['Crse'].isin(ALLOWED_COURSES)]
valid_courses = valid_courses[df.apply(lambda x: str(x['Sec']).startswith('O'), axis=1)]
valid_courses = valid_courses[df.apply(lambda x: True if x['Crse'] != 8803 else x['Sec'] in ['O01', 'O02', 'O03'], axis=1)]
valid_courses = valid_courses[['Select', 'CRN', 'Subj', 'Crse', 'Sec', 'Title', 'Rem', 'WLAct', 'WLRem']]
valid_courses = valid_courses.sort_values(by=['Rem'], ascending=False)
valid_courses = valid_courses.drop_duplicates()

# Write data frame out to CSV.
valid_courses.to_csv('courses.csv', quoting=csv.QUOTE_ALL)

# Delete intermediate file.
os.remove('table.csv')
