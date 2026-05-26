import pandas as pd

path = r"E:\ai-agent\uploads\产品资料\SL货盘表.xlsx"
sheets = pd.read_excel(path, sheet_name=None, dtype=str)
for name, frame in sheets.items():
    print("SHEET", name, "shape", frame.shape)
    print("COLUMNS", list(frame.columns))
    print(frame.head(3).to_string())
