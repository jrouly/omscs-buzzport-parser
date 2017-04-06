from bs4 import BeautifulSoup
from adjustText import adjust_text
import matplotlib.pyplot as plt
import csv
import pandas
import os
import requests
import sys

###
### Constants
###

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

# Special topics 8803 availability varies per-section.
SPECIAL_TOPICS_SECTIONS = ['O01', 'O02', 'O03', 'O04', 'O07', 'O08']


###
### HTML Parsing
###

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


###
### Sorting and Filtering
###

# Load up the pandas data frame.
df = pandas.read_csv('table.csv')
os.remove('table.csv')

# Filter and select only allowed courses.
c = df[df['Crse'].isin(ALLOWED_COURSES)]

# Filter only the allowed online sections of the offered courses.
filter_online = lambda x: str(x['Sec']).startswith('O')
filter_special_topics = lambda x: True if x['Crse'] != 8803 else x['Sec'] in SPECIAL_TOPICS_SECTIONS
c = c[c.apply(filter_online, axis=1)]
c = c[c.apply(filter_special_topics, axis=1)]

# Project the desired columns.
c = c[['Select', 'CRN', 'Subj', 'Crse', 'Sec', 'Title', 'Rem', 'WLAct', 'WLRem']]

# Strip section prefixes so they become integers.
c['Sec'] = c['Sec'].apply(lambda sec: int(sec[1:]))

# Generate a synthetic crosswalk field to work with the Course Reviews APIs.
format_crosswalk = lambda x: '{}-{:0>3}'.format(x[0], x[1]) if x[0] == 8803 else x[0]
c['Crswlk'] = c[['Crse', 'Sec']].apply(format_crosswalk, axis=1).map(str)

# Sort and deduplicate.
c = c.sort_values(by=['Crse', 'Sec'], ascending=True)
c = c.drop_duplicates()


###
### Associate Course Review Data
###

REVIEWS_API_BASE_URL = 'https://gt-surveyor.firebaseio.com'
COURSE_API_URL = '{}/CRS.json'.format(REVIEWS_API_BASE_URL)
AGGREGATE_API_URL = '{}/AGG.json'.format(REVIEWS_API_BASE_URL)

# Make requests to external reviews API.
course_resp = requests.get(COURSE_API_URL)
aggregate_resp = requests.get(AGGREGATE_API_URL)

# Handle failed requests gracefully.
if course_resp.status_code >= 400 or aggregate_resp.status_code >= 400:
    sys.exit()

# Parse json response bodies.
crs = course_resp.json()
agg = aggregate_resp.json()

# Associate desired fields from API responses.
c['Name'] = c['Crswlk'].apply(lambda x: crs.get(x).get('name'))
c['Foundational_Bool'] = c['Crswlk'].apply(lambda x: crs.get(x).get('foundational'))
c['Foundational'] = c['Crswlk'].apply(lambda x: '' if crs.get(x).get('foundational') else 'Not Foundational')
c['Avg_Rating'] = c['Crswlk'].apply(lambda x: agg.get(x).get('average').get('rating'))
c['Avg_Workload'] = c['Crswlk'].apply(lambda x: agg.get(x).get('average').get('workload'))
c['Review_Count'] = c['Crswlk'].apply(lambda x: agg.get(x).get('count'))


###
### Generate Plots
###

def label_point(xs, ys, labels, ax):
    points_and_labels = pandas.concat({'x': xs, 'y': ys, 'label': labels}, axis=1)
    for i, data in points_and_labels.iterrows():
        ax.text(data['x'], data['y'], str(data['label']))

# Alias X data, Y data, Labels.
xs, ys, labels = c['Avg_Workload'], c['Avg_Rating'], c['Crswlk']

# Construct figure and axes.
fig, ax = plt.subplots()
ax.scatter(xs, ys, marker='o', c=c['Review_Count'], cmap=plt.cm.coolwarm)
label_point(xs, ys, labels, ax)
ax.invert_xaxis()
ax.set_title('Avg_Rating by Avg_Workload')
ax.set_xlabel('Avg_Workload')
ax.set_ylabel('Avg_Rating')

# Adjust labeling.
# adjust_text(labels, xs, ys, arrowprops=dict(arrowstyle='->', color='r', lw=0.5))


###
### Final I/O
###

# Output plot to file.
ax.figure.savefig('plot.png')

# Write data frame out to CSV.
prj = c[[
    'CRN', 'Subj', 'Crse', 'Sec', 'Foundational', 'Name', 'Rem',
    'Avg_Workload', 'Avg_Rating', 'Review_Count'
]]
prj.to_csv('courses.csv', quoting=csv.QUOTE_ALL)
