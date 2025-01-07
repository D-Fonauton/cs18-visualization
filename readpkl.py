import pickle
import numpy as np
import pandas as pd


# filename = ["Levenshtein_distance_diff", "Needleman_Wunsch_diff", "Scanmatch_diff"]
filename = ["levenshtein","needleman","scanmatch"]

for index in range(3):
    # 从 .pkl 文件读取数据
    with open(f"{filename[index]}.pkl", "rb") as f:
        matrix = pickle.load(f)

    # 检查是否是 NumPy 矩阵（或转换为矩阵）
    if not isinstance(matrix, np.ndarray):
        matrix = np.array(matrix)

    # 将矩阵保存为 .csv 文件
    df = pd.DataFrame(matrix)  # 转换为 Pandas DataFrame
    df.to_csv(f"{filename[index]}.csv", index=False, header=False)  # 保存为 CSV

    print(f"数据已成功保存为 {filename[index]}.csv 文件！")
