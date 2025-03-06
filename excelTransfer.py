import pandas as pd

# 读取原始 csv 文件
df = pd.read_csv('6.csv')

# 提取指定的列（基于索引）
# 假设 D, E, F, N, O, P, X, Y, Z 对应的索引是 3, 4, 5, 13, 14, 15, 23, 24, 25
columns_to_extract = df.iloc[:, [3, 4, 5, 13, 14, 15, 23, 24, 25]]

# 写入新的 Excel 文件
columns_to_extract.to_excel('extractedData6.xlsx', index=False,engine='openpyxl')
#findpeak ,