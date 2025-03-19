print("开始测试导入...")

try:
    import jieba
    print("成功导入 jieba")
except Exception as e:
    print(f"导入 jieba 失败：{str(e)}")

try:
    import numpy as np
    print("成功导入 numpy")
except Exception as e:
    print(f"导入 numpy 失败：{str(e)}")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    print("成功导入 scikit-learn")
except Exception as e:
    print(f"导入 scikit-learn 失败：{str(e)}")

try:
    import matplotlib.pyplot as plt
    print("成功导入 matplotlib")
except Exception as e:
    print(f"导入 matplotlib 失败：{str(e)}")

try:
    from wordcloud import WordCloud
    print("成功导入 wordcloud")
except Exception as e:
    print(f"导入 wordcloud 失败：{str(e)}")

try:
    import pandas as pd
    print("成功导入 pandas")
except Exception as e:
    print(f"导入 pandas 失败：{str(e)}")

print("\n所有导入测试完成") 