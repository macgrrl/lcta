#!/usr/bin/env python
"""
lcta_proc.py

Purpose: Process the Sorted Data tab saved as a CSV file from the LCTA Trail Count Worksheet

Preconditions
* Sorted by Location and then by Date / Time in Ascending Order

What it does
* Eliminates duplicate rows
* Takes the later timestamp
* Flags an error if the reading is less than the previous (in comment)
* Prepend date to the Comment field
* Append 'Counter not working' text to comment

Output

<site name>
date/time \t count \t comment

"""

import csv
from datetime import datetime

previous_location = None
previous_date_time = datetime.fromtimestamp(0) # zero date time
previous_count = 0
previous_comment = ''
new_location = True # first item is a new location

# functions

def print_previous():
  global previous_date_time, previous_count, previous_comment
  print previous_date_time.strftime('%x %X') + '\t' + str(previous_count) + '\t\t\t\t\t' + previous_comment
  # comment has to line up in the Excel spreadsheet


def set_previous(location, date_time, count, comment):
  global previous_location, previous_date_time, previous_count, previous_comment
  previous_location = location
  previous_date_time = date_time
  previous_count = count
  previous_comment = comment


# main code

filename = 'LCTA Trail Count Worksheet - Sorted data.csv'

csvfile = open(filename, 'rb')

lcta_records = csv.reader(csvfile)

# skip header
lcta_records.next()

for (rec_location, rec_date_time, rec_count, rec_comment, rec_inop) in lcta_records:
  date_time = datetime.strptime(rec_date_time, '%m/%d/%Y %H:%M:%S')
  count = int(rec_count)
  comment = ''
  new_location = previous_location != rec_location
  #print '# Loc={} data_time={} count={} comment={} inop={}'.format(rec_location, date_time, rec_count, rec_comment, rec_inop)
  # process comment first (since we're caching it)
  if not new_location:
    if count < previous_count:
      # count is less than previous count
      rec_comment = 'COUNT ERROR. ' + rec_comment
    elif count == previous_count:
      # count is same - flag possible INOP
      rec_comment = 'COUNTER DEAD. ' + rec_comment
  if (rec_comment != '') or (rec_inop != ''):
    # process comment
    comment = date_time.strftime('%m/%d ') + rec_comment + ' ' + rec_inop
  if new_location:
    # location has changed
    if previous_location != None:
      print_previous() # flush last entry
      print
    print rec_location
    set_previous(rec_location, date_time, count, comment)
  else:
    if date_time.date() == previous_date_time.date():
      # same date
      current_time = date_time.time()
      previous_time = previous_date_time.time()
      if current_time != previous_time:
        # different time (otherwise we ignore the same or previous time - always keep the latest time)
        if current_time > previous_time:
          # time is after the previous -> replace previous entry
          #print '# >> Replacing previous entry for ' + str(previous_date_time) + ' with ' + str(date_time)
          set_previous(rec_location, date_time, count, comment)
      else:
        # same time - ignore
        #print '# >> Ignoring - same date and time for ' + str(date_time)
        pass
    else:
      # different day
      print_previous()
      set_previous(rec_location, date_time, count, comment)

print_previous() # flush last entry

