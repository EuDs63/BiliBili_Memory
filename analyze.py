# 对posts.josn文件进行分析
import asyncio
import json
import jieba
import numpy as np
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image  # 处理图片
import datetime
from concurrent.futures import ProcessPoolExecutor


# 根据data生成词云
def generate_word_cloud_by_data(data):
    # 将文本数据拼接成一个长字符串
    text_data = " ".join(post["message"] for post in data)

    # 使用jieba分词
    text_data = " ".join(jieba.cut(text_data))

    # 读取停用词
    # 停用词基于[stopwords/cn_stopwords.txt at master · goto456/stopwords](https://github.com/goto456/stopwords/blob/master/cn_stopwords.txt)
    # 添加了贴吧常用的表情符号
    stopwords = set()
    content = [line.strip() for line in open('resources/cn_stopwords.txt', 'r', encoding="utf8").readlines()]
    stopwords.update(content)

    # 创建 WordCloud 对象
    wordcloud = WordCloud(width=480,
                          height=480,
                          # mask=mask,
                          background_color="white",
                          # mode="RGB",
                          font_path=r'C:\Windows\Fonts\STZHONGS.ttf',
                          stopwords=stopwords,
                          max_words=100,
                          relative_scaling=0.8,
                          # contour_width=1,
                          ).generate(text_data)

    # 显示词云图
    plt.figure(figsize=(10, 5))
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    return plt


# 从post文件生成词云
def generate_word_cloud_from_file(file_path):
    # 读取json文件
    data = json.load(open(file_path, encoding="utf-8"))
    result_plt = generate_word_cloud_by_data(data)
    # 标题
    result_plt.title(f"{file_path}词云图")
    result_plt.show()
    # wordcloud.to_file(f"output/wordcloud_{file_path}.png")


# 为每年的数据生成词云
def generate_word_cloud_every_year(user_id):
    # 读取json文件
    with open(f"output/all_{user_id}.json", encoding='utf-8') as f:
        data = json.load(f)
    for k, v in data.items():
        result_plt = generate_word_cloud_by_data(v)
        # 设置标题
        result_plt.title(f"{k}年词云图")
        # 保存图片
        result_plt.savefig(f"output/wordcloud_{k}.png")
        result_plt.show()


# 统计在每个用户的回复数
def count_post_per_user(data):
    stats = {}

    for item in data:
        extra_info = item.get("extra_info", {})
        if extra_info:
            name = item.get("extra_info", {}).get("author_name")
            if name not in stats:
                stats[name] = 0
            stats[name] += 1

    return stats


# 根据data生成饼状图
def generate_pie_chart_by_data(data):
    # 统计在每个贴吧的回复数
    stats = count_post_per_user(data)

    # 出于显示美观考虑，将占比小的贴吧合并为其他
    num_labels = 7  # 需要显示的标签数
    # 当贴吧数大于num_labels时
    if len(stats) > num_labels:
        sorted_counts = sorted(stats.values())
        min_count = sorted_counts[-num_labels]
        other_count = 0

        new_stats = {
            k: v for k, v in stats.items() if v >= min_count
        }
        for v in stats.values():
            if v < min_count:
                other_count += v
        new_stats['其他'] = other_count
        stats = new_stats

    # 绘制饼状图
    labels = list(stats.keys())
    sizes = list(stats.values())
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes,
            labels=labels,
            # autopct='%1.1f%%',
            pctdistance=0.1,
            labeldistance=1.1,
            shadow=False,
            startangle=90)
    ax1.axis('equal')
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    # 创建图例
    # plt.legend(labels, loc="best", bbox_to_anchor=(0.5, 0, 0.5, 1))
    return plt


# 由文件生成饼状图
def generate_pie_chart_from_file(file_path):
    # 读取json文件
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)
    result_plt = generate_pie_chart_by_data(data)
    result_plt.show()


# 为每年的数据生成饼状图
def generate_pie_chart_every_year(user_id):
    # 读取json文件
    with open(f"output/all_{user_id}.json", encoding='utf-8') as f:
        data = json.load(f)
    for k, v in data.items():
        result_plt = generate_pie_chart_by_data(v)
        # 设置标题
        result_plt.title(f"{k}年回复用户分布")
        # 保存图片
        result_plt.savefig(f"output/pie_{k}.png")
        result_plt.show()


# 为每年的数据生成记录文件
def generate_post_all_data(user_id):
    with open(f"output/all_{user_id}.json", encoding='utf-8') as f:
        data = json.load(f)
    result = {}
    for k, v in data.items():
        year_data = count_post_per_user(v)
        # 添加总数
        year_data["总计回复"] = len(v)
        result[k] = year_data
    with open(f"output/post_all_data_{user_id}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    user_id = "502474657"
    # 为每年的数据生成词云图
    generate_word_cloud_every_year(user_id)
    # 为每年的数据生成饼状图
    #generate_pie_chart_every_year(user_id)
    # generate_post_all_data(user_id)
