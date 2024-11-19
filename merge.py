# 读取uid所对应的所有已处理后的json文件，合并为一个json文件
import logging
import json
import os

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def merge_files(files, output_file):
    """ 合并多个json文件 """
    data = []
    for file in files:
        file_path = os.path.join("output", file)
        with open(file_path, encoding="utf-8") as f:
            processed_data = json.load(f)
            cur_comments = processed_data.get("replies", [])

        data.extend(cur_comments)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"合并完成，共有{len(data)}条数据")


def main(user_id):
    # 获取output文件夹下的所有以uid开头的json文件
    files = [f for f in os.listdir("output") if f.startswith(f"processed_{user_id}") and f.endswith(".json")]
    if not files:
        logging.warning("没有找到需要合并的文件")
        return
    else:
        logging.info(f"找到了{len(files)}个文件")
        merge_files(files, f"output/merged_{user_id}.json")


# 示例用法
if __name__ == "__main__":
    #  获取output文件夹下的所有以json文件
    uid = "7"  # 示例 UID
    main(uid)
