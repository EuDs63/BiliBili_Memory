# 处理merge后的json文件，将其按年份分别保存到不同的json文件中
import json
import datetime
import os


def split_data_by_year(user_id):
    merge_file_path = os.path.join("output", f"merged_{user_id}.json")
    # 读取json文件
    with open(merge_file_path, encoding='utf-8') as f:
        data = json.load(f)

    files_data = {}

    def process(item):
        # 由时间戳转换为datetime对象
        create_date = datetime.datetime.fromtimestamp(item["time"])
        year = create_date.year
        if year not in files_data.keys():
            files_data[year] = []
        files_data[year].append(item)

    for item in data:
        process(item)

    # 输出到对应的json文件中
    for k, v in files_data.items():
        with open(f"output/year_{user_id}_{k}.json", "w", encoding="utf-8") as f:
            json.dump(v, f, ensure_ascii=False, indent=2)

    # 输出到总的json文件中
    with open(f"output/all_{user_id}.json", "w", encoding="utf-8") as f:
        json.dump(files_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    uid = "7"  # 示例 UID
    split_data_by_year(uid)