import pandas as pd
import csv
import os

file_name = 'book1.csv'
keep_headers = True

row_limit = 0
delimiter = ','


def Check(extraction_type):
    # Opening the CSV file
    f = open(file_name, 'r')

    # Reading the CSV File
    reader = csv.reader(f, delimiter=delimiter)

    # Reading file using pandas
    df = pd.read_csv(file_name)
    print("Is CSV File empty ?", df.empty)

    # print(df.isnull())

    # If file is empty, exiting the process
    if(df.empty):
        print("Given CSV File is Empty")
        return
    else:
        # Appending Row names
        names = next(reader)
        print(names)

        print("Given Extraction type:", extraction_type)
        if(extraction_type == "empi" and ("EMPI" not in names)):
            print("Error, incomplete CSV File or provided wrong extraction type")
            return

        if(extraction_type == "accession" and ("Accession" not in names)):
            print("Error, incomplete CSV File or provided wrong extraction type")
            return

        if(extraction_type == "empi_accession" and (("Accession" not in names) or ("EMPI" not in names))):
            print("Error, incomplete CSV File or provided wrong extraction type")
            return

        # Iterating through each column and finding number of null values
        flag = 0
        for n in names:
            c = df[n].isnull().sum()
            print(n, c, sep=" ")
            if(c != 0):
                flag = -1

        # If one value is also missing returning it as missing
        if(flag == -1):
            print("Error, Given CSV File contains missing fields")
            print("Now Removing those values . . . . . . . . .")
            df.dropna(inplace=True)
            print(
                "CSV file is now cleaned . . . . . .\nGoing forward with the extraction")
            print(df.to_string())
        else:
            print("All good !!\nGoing forward with the extraction")


extraction_type = input(
    "Types of Extractions\nempi_date\nempi\naccession\nempi_accession\n\nEnter the Extraction type: ")
Check(extraction_type)
