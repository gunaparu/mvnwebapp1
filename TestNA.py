import pandas as pd

def find_string_in_column(file_path, sheet_name, column_name, search_string):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    found_rows = df[df[column_name] == search_string]
    
    return found_rows

file_path = 'path_to_your_excel_file.xlsx'
sheet_name = 'Sheet1'
column_name = 'ColumnB'  # Replace with the column name where you want to search
search_string = 'iam:*'

found_rows = find_string_in_column(file_path, sheet_name, column_name, search_string)
print(found_rows)
