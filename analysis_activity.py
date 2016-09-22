# -*- coding: utf-8 -*-
"""
@author: Carl Rygart
"""
from scipy import *
from pylab import *
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

user_list = {}
cluster_data = {}

user_file_name = 'yelp_academic_dataset_user.csv'
tip_file_name = 'yelp_academic_dataset_tip.csv'
review_file_name = 'yelp_academic_dataset_review.csv'

## starting_date format: 'YYYY-MM'
## ending_date format: 'YYYY-MM-DD'
def calculate_months_between_two_dates(starting_date, ending_date):
    months = 0
    starting_date = starting_date.split('-')
    ending_date = ending_date[:-3].split('-')

    starting_year = int(starting_date[0])
    ending_year = int(ending_date[0])
    starting_month = int(starting_date[1])
    ending_month = int(ending_date[1])

    if ending_month - starting_month < 0:
        months += 12*(ending_year-starting_year-1)
        months += ending_month + (12-starting_month)
    else:
        months += 12*(ending_year-starting_year)
        months += ending_month-starting_month
    return months

## Open file. Iterate through all lines.
def add_activity(file_name):
    with open(file_name, 'r', encoding='utf8') as tip_file:
        tip_columns = tip_file.readline().rstrip('\n').split('\t')
        tip_index_uid = tip_columns.index('user_id')
        tip_index_date = tip_columns.index('date')
        row = 0
        for line_in_tip_file in tip_file:
            tip_line = line_in_tip_file.rstrip('\n').split("\t")
            row += 1
            
            ## Check if there are line breaks in row, in that case: Go to next row
            ## and check if there's 
            while len(tip_line) < len(tip_columns):
                new_row = tip_file.readline().rstrip('\n').split('\t')
                row += 1
                if len(new_row) > 1:
                    new_row.pop(0)
                    tip_line.extend(new_row)
            user_id = tip_line[tip_index_uid]
    
            ## Do the months calculation and insertion in cluster_data dict.
            try:
                user_yelping_since = user_list[user_id]
                tip_date = tip_line[tip_index_date]
                months_since_reg = calculate_months_between_two_dates(user_yelping_since, tip_date)
                cluster_data[user_id][months_since_reg] += 1
            except KeyError:
                print("KeyError row: {}".format(row))
            except IndexError:
                print("IndexError row: {}".format(row))
            except ValueError:
                print("ValueError row: {}".format(row))

## Open userfile. Iterate through all lines (one line per user),
## extract user_id and yelping_since. Store in a dict.
with open(user_file_name, 'r', encoding='utf8') as user_file:
    user_columns = user_file.readline().rstrip('\n').split('|')
    user_index_uid = user_columns.index('user_id')
    user_index_yelping_since = user_columns.index('yelping_since')
    for line_in_user_file in user_file:
        user_row = line_in_user_file.rstrip('\n').split('|')
        user_id =  user_row[user_index_uid] #'bvu13GyOUwhEjPum2xjiqQ'
        user_yelping_since = user_row[user_index_yelping_since] #'2010-08'
        user_list[user_id] = user_yelping_since
        cluster_data[user_id] = [0]*135

# Choose which data you want to include.
add_activity(tip_file_name)
add_activity(review_file_name)

# Convert dict to list and remove keys etc.
data = list(cluster_data.values())
data_cols = len(data[0])
data_rows = len(data)

# Initiate K-means. Choose clusters.
n_clusters = 3
kms = KMeans(n_clusters=n_clusters, n_jobs=1)
kms.fit(data)
labels = kms.labels_

label_count = []
for i in range(n_clusters):
    label_count.append(labels.tolist().count(i))

lines_set = np.zeros((n_clusters, data_cols))
for i in range(data_rows):
        lines_set[labels[i]] += data[i]

for i in range(n_clusters):
        lines_set[i] /= np.sum(lines_set[i])

x = range(data_cols)
for i in range(n_clusters):
        y = lines_set[i]
        plt.plot(x, y, label="Nbr of users: {}".format(label_count[i]))

plt.legend(loc='best')
plt.title("Number of posts per month after signup")
plt.ylabel("Number of posts / All posts")
plt.xlabel("Months after signup")
plt.show()
