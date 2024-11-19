import export
import process
import merge
import spilt
import analyze

uid = "7" # 你的UID

# 导出评论
export.main(uid)

# 处理评论
process.main(uid)

# 合并评论文件
merge.main(uid)

# # 拆分评论文件
spilt.split_data_by_year(uid)

# 生成分析报告
# 1. 为每年的数据生成词云图
analyze.generate_word_cloud_every_year(uid)

# 2. 为每年的数据生成饼状图
analyze.generate_pie_chart_every_year(uid)

# 3. 为每年的数据生成记录文件
analyze.generate_post_all_data(uid)


