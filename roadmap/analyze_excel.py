import pandas as pd
import numpy as np
from datetime import datetime
import openpyxl

def analyze_excel_file(file_path):
    """
    分析Excel文件的数据结构和内容
    """
    print(f"分析文件: {file_path}")
    print("=" * 60)
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        print(f"数据集基本信息:")
        print(f"- 总行数: {len(df)}")
        print(f"- 总列数: {len(df.columns)}")
        print(f"- 内存使用: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        print("\n")
        
        # 检查列名
        print("列名列表:")
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")
        print("\n")
        
        # 分析每一列
        print("各列详细分析:")
        print("-" * 80)
        
        for col in df.columns:
            print(f"\n列名: {col}")
            print(f"数据类型: {df[col].dtype}")
            print(f"非空值数量: {df[col].count()}")
            print(f"空值数量: {df[col].isnull().sum()}")
            print(f"空值比例: {df[col].isnull().sum() / len(df) * 100:.2f}%")
            
            # 获取唯一值数量
            unique_count = df[col].nunique()
            print(f"唯一值数量: {unique_count}")
            
            # 显示前几个非空值
            non_null_values = df[col].dropna()
            if len(non_null_values) > 0:
                print(f"前5个非空值: {list(non_null_values.head())}")
                
                # 如果是数值类型，显示统计信息
                if pd.api.types.is_numeric_dtype(df[col]):
                    print(f"统计信息:")
                    print(f"  - 最小值: {df[col].min()}")
                    print(f"  - 最大值: {df[col].max()}")
                    print(f"  - 平均值: {df[col].mean():.2f}")
                    print(f"  - 中位数: {df[col].median():.2f}")
                    print(f"  - 标准差: {df[col].std():.2f}")
                
                # 如果是字符串类型，显示最常见的值
                elif df[col].dtype == 'object':
                    if unique_count <= 20:  # 如果唯一值不多，显示所有唯一值
                        unique_vals = df[col].value_counts()
                        print(f"所有唯一值及其出现次数:")
                        for val, count in unique_vals.head(10).items():
                            print(f"  - '{val}': {count}次")
                    else:
                        print(f"最常见的5个值:")
                        top_values = df[col].value_counts().head()
                        for val, count in top_values.items():
                            print(f"  - '{val}': {count}次")
                
                # 检查是否可能是日期类型
                if df[col].dtype == 'object':
                    try:
                        pd.to_datetime(non_null_values.iloc[0])
                        print(f"可能是日期类型")
                    except:
                        pass
            
            print("-" * 40)
        
        # 显示前几行数据
        print("\n前5行数据预览:")
        print(df.head().to_string())
        
        # 检查数据质量问题
        print("\n\n数据质量检查:")
        print("-" * 40)
        
        # 检查完全重复的行
        duplicate_rows = df.duplicated().sum()
        print(f"完全重复的行数: {duplicate_rows}")
        
        # 检查完全空的行
        empty_rows = df.isnull().all(axis=1).sum()
        print(f"完全空的行数: {empty_rows}")
        
        # 检查各列的空值情况
        null_summary = df.isnull().sum()
        print("\n各列空值统计:")
        for col, null_count in null_summary.items():
            if null_count > 0:
                print(f"  {col}: {null_count} ({null_count/len(df)*100:.1f}%)")
        
        return df
        
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

if __name__ == "__main__":
    # 分析Excel文件
    file_path = "黑龙江数据V20250609.xlsx"
    df = analyze_excel_file(file_path) 