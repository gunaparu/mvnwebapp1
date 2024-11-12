import csv

def read_column_from_csv(file_path, column_name):
    with open(file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        # Loop through each row and print the value in the specified column
        for row in csv_reader:
            print(row[column_name])

# Example usage
file_path = 'your_file.csv'  # Replace with the path to your CSV file
column_name = 'YourColumnName'  # Replace with the name of the column you want to print

read_column_from_csv(file_path, column_name)