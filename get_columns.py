import pandas as pd
excel_path = r'c:\Users\dell\Desktop\Projets 2\data\banking_dash_project\data_raw\BASE_SENEGAL2.xlsx'
try:
    df = pd.read_excel(excel_path, nrows=1)
    with open('columns_v3.txt', 'w', encoding='utf-8') as f:
        f.write(';'.join(df.columns.tolist()))
    print("Columns saved to columns_v3.txt")
except Exception as e:
    with open('error_log.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
    print(f"Error: {e}")
