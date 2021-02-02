import os
import csv

file_name = 'origin.csv'
output_name_template='output_%s.csv'
output_path='.'
keep_headers=True

row_limit = 0
delimiter = ','


def split():
    filehandler = open(file_name, 'r')
    reader = csv.reader(filehandler, delimiter=delimiter)

    current_piece = 1
    current_out_path = os.path.join(output_path, output_name_template % current_piece)
    current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
    current_limit = row_limit
    if keep_headers:
        headers = next(reader)
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(output_path, output_name_template % current_piece)
            current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)


with open(file_name,'r') as f:
    reader = csv.reader(f)
    data = list(reader)
    row_limit = int(len(data) / 2)

split()
