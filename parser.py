from bs4 import BeautifulSoup

html = open('table.html', 'r')
soup = BeautifulSoup(html, 'html.parser')
rows = [
        [td.text for td in tr.find_all('td')]
        for tr in soup.find_all('tr')[2:]
        if tr.find('td').text.strip() != '' # get rid of the empty 'second lines'
       ]

import csv

fieldnames = [
    'Select', 'CRN', 'Subj', 'Crse', 'Sec', 'Cmp', 'Bas', 'Cred',
    'Title', 'Days', 'Time', 'Cap', 'Act', 'Rem', 'WLCap', 'WLAct',
    'WLRem', 'Instructor', 'Location', 'Attribute'
]
wr = open('table.csv', 'w')
writer = csv.writer(wr, delimiter=',', quoting=csv.QUOTE_ALL)
writer.writerow(fieldnames)
for row in rows:
    writer.writerow(row)

html.close()
wr.close()

import pandas

allowed_courses = [
    6035, 6210, 6220, 6242, 6250, 6262, 6290, 6300, 6310, 6340,
    6400, 6440, 6460, 6475, 6476, 6505, 6601, 7637, 7641, 7646,
    8803, 8803, 8803
]

df = pandas.read_csv('table.csv')
valid_courses = df[df['Crse'].isin(allowed_courses)][df.apply(lambda x: str(x['Sec']).startswith('O'), axis=1)][df.apply(lambda x: True if x['Crse'] != 8803 else x['Sec'] in ['O01', 'O02', 'O03'], axis=1)][['Select', 'CRN', 'Subj', 'Crse', 'Sec', 'Title', 'Rem', 'WLAct', 'WLRem']].sort(['Rem'], ascending=False)
valid_courses.to_csv('courses.csv', quoting=csv.QUOTE_ALL)
