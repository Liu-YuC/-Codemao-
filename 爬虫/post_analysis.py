import json
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import sys
import traceback
import os

def main():
    try:
        # 检查文件是否存在
        if not os.path.exists('codemao_posts_detail.json'):
            print("错误：找不到文件 codemao_posts_detail.json")
            return

        # 获取文件大小
        file_size = os.path.getsize('codemao_posts_detail.json')
        print(f"文件大小：{file_size / 1024:.2f} KB")

        # 读取帖子数据
        print("正在读取数据...")
        try:
            with open('codemao_posts_detail.json', 'r', encoding='utf-8') as f:
                posts = json.load(f)
            print(f"成功读取 {len(posts)} 个帖子")
        except json.JSONDecodeError as e:
            print(f"JSON解析错误：{str(e)}")
            return
        except Exception as e:
            print(f"读取文件时出错：{str(e)}")
            return

        # 提取标题和内容
        print("正在提取标题和内容...")
        titles = []
        contents = []
        for i, post in enumerate(posts):
            try:
                title = post.get('title', '')
                content = post.get('content', '')
                if not isinstance(title, str):
                    print(f"警告：帖子 {i} 的标题不是字符串类型：{type(title)}")
                    title = str(title)
                if not isinstance(content, str):
                    print(f"警告：帖子 {i} 的内容不是字符串类型：{type(content)}")
                    content = str(content)
                titles.append(title)
                contents.append(content)
            except Exception as e:
                print(f"处理帖子 {i} 时出错：{str(e)}")
                continue
        print(f"成功提取 {len(titles)} 个标题和内容")

        # 分词处理
        print("正在进行分词...")
        def process_text(text):
            try:
                if not isinstance(text, str):
                    return ''
                # 使用结巴分词
                words = jieba.cut(text)
                # 过滤停用词（这里可以根据需要添加更多停用词）
                stop_words = {'的', '了', '和', '是', '就', '都', '而', '及', '与', '着',
                            '或', '一个', '没有', '我们', '你们', '他们', '它们', '这个',
                            '那个', '这些', '那些', '自己', '什么', '这样', '那样', '怎样',
                            '如何', '为什么', '啊', '呢', '吗', '嘛', '吧', '么'}
                return ' '.join(w for w in words if w not in stop_words and len(w) > 1)
            except Exception as e:
                print(f"分词处理出错：{str(e)}")
                return ''

        processed_titles = []
        for i, title in enumerate(titles):
            try:
                processed = process_text(title)
                processed_titles.append(processed)
            except Exception as e:
                print(f"处理标题 {i} 时出错：{str(e)}")
                processed_titles.append('')
        print("分词处理完成")

        # 使用TF-IDF向量化
        print("正在进行文本向量化...")
        try:
            vectorizer = TfidfVectorizer(max_features=1000)
            X = vectorizer.fit_transform(processed_titles)
            print(f"向量化完成，特征维度：{X.shape}")
        except Exception as e:
            print(f"向量化过程出错：{str(e)}")
            return

        # 使用K-means聚类
        print("正在进行聚类分析...")
        try:
            n_clusters = 8  # 可以调整聚类数量
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X)
            print(f"聚类完成，共 {n_clusters} 个类别")
        except Exception as e:
            print(f"聚类过程出错：{str(e)}")
            return

        # 分析每个聚类的关键词
        print("\n发现的帖子类别：")
        feature_names = vectorizer.get_feature_names_out()
        cluster_info = []
        
        for i in range(n_clusters):
            try:
                # 获取该聚类的所有文档索引
                cluster_docs = np.where(clusters == i)[0]
                
                # 计算该聚类中心的特征权重
                centroid = kmeans.cluster_centers_[i]
                
                # 获取权重最高的10个词
                top_keywords = [feature_names[j] for j in centroid.argsort()[-10:][::-1]]
                
                # 获取该聚类的示例标题
                example_titles = [titles[idx] for idx in cluster_docs[:3]]
                
                print(f"\n类别 {i+1}:")
                print(f"关键词: {', '.join(top_keywords)}")
                print(f"该类别帖子数量: {len(cluster_docs)}")
                print("示例标题:")
                for title in example_titles:
                    print(f"- {title}")
                    
                cluster_info.append({
                    'category': f'类别{i+1}',
                    'keywords': top_keywords,
                    'post_count': len(cluster_docs),
                    'percentage': len(cluster_docs) / len(posts) * 100,
                    'example_titles': example_titles
                })
            except Exception as e:
                print(f"处理类别 {i} 时出错：{str(e)}")
                continue

        # 生成词云
        print("\n正在生成词云...")
        try:
            all_text = ' '.join(processed_titles)
            wordcloud = WordCloud(width=800, height=400,
                                background_color='white',
                                font_path='C:\\Windows\\Fonts\\simhei.ttf')
            wordcloud.generate(all_text)

            # 保存词云图
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.savefig('post_wordcloud.png')
            plt.close()
            print("词云图生成完成")
        except Exception as e:
            print(f"生成词云图时出错：{str(e)}")

        # 统计分析
        print("\n正在生成统计报告...")
        try:
            df = pd.DataFrame({
                '标题': titles,
                '内容': contents,
                '类别': [f'类别{i+1}' for i in clusters]
            })

            # 保存分析结果
            report = {
                'cluster_info': cluster_info,
                'statistics': {
                    'total_posts': len(posts),
                    'avg_title_length': sum(len(title) for title in titles) / len(titles),
                    'category_distribution': df['类别'].value_counts().to_dict()
                }
            }

            # 保存分析报告
            with open('post_analysis_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print("JSON报告生成完成")

            # 生成Markdown格式的分析报告
            with open('post_analysis_report.md', 'w', encoding='utf-8') as f:
                f.write("# 编程猫社区帖子分析报告\n\n")
                f.write(f"## 基本统计\n\n")
                f.write(f"- 总帖子数：{report['statistics']['total_posts']}\n")
                f.write(f"- 平均标题长度：{report['statistics']['avg_title_length']:.2f}字\n\n")
                
                f.write("## 帖子类别分布\n\n")
                for info in cluster_info:
                    f.write(f"### {info['category']}\n\n")
                    f.write(f"- 帖子数量：{info['post_count']} ({info['percentage']:.2f}%)\n")
                    f.write(f"- 关键词：{', '.join(info['keywords'])}\n")
                    f.write("- 示例标题：\n")
                    for title in info['example_titles']:
                        f.write(f"  - {title}\n")
                    f.write("\n")
                
                f.write("\n## 词云图\n\n")
                f.write("![帖子词云图](post_wordcloud.png)\n")
            print("Markdown报告生成完成")

            print("\n分析完成！生成了以下文件：")
            print("1. post_wordcloud.png - 帖子关键词词云图")
            print("2. post_analysis_report.json - 详细的分析数据")
            print("3. post_analysis_report.md - 可读性好的分析报告")
        except Exception as e:
            print(f"生成报告时出错：{str(e)}")

    except Exception as e:
        print(f"\n错误：{str(e)}")
        print("\n详细错误信息：")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 