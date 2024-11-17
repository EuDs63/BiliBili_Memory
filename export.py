import requests
import json
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_comments(uid, page=1, page_size=100):
    """ 获取评论数据 """
    url = "https://api.aicu.cc/api/v3/search/getreply"
    params = {
        "uid": uid,
        "pn": page,
        "ps": page_size,
        "mode": "0",  # 0-全部 1-仅一级评论 2-仅2级评论
        "keyword": "",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.aicu.cc",
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # 如果响应状态码不是 200，将抛出异常
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败: {e}")
        return None


def save_comments_to_file(comments, filename):
    """ 将评论保存到指定的JSON文件 """
    try:
        # 创建保存目录
        if not os.path.exists("output"):
            os.makedirs("output")
        file_path = os.path.join("output", filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=4)
        logging.info(f"评论已成功保存到 {filename}")
    except Exception as e:
        logging.error(f"保存评论到文件时出错: {e}")


def get_all_comments(uid, page_size=100):
    """ 获取该用户所有评论并分页保存 """
    page = 1
    all_comments = []
    while True:
        logging.info(f"正在获取第 {page} 页的评论数据...")
        comments = fetch_comments(uid, page, page_size)

        if comments is None or comments["code"] != 0:
            logging.error(f"获取评论失败或没有更多数据。错误信息：{comments['message'] if comments else '无响应'}")
            break

        all_comments.extend(comments["data"]["replies"])

        # 判断是否已获取完所有评论
        if comments["data"]["cursor"]["is_end"]:
            logging.info("所有评论已获取完毕")
            break

        page += 1

    return all_comments


def main(user_id):
    """ 主程序，控制数据获取并按100条数据存储为不同文件 """
    all_comments = get_all_comments(user_id)

    if not all_comments:
        logging.warning("没有获取到任何评论数据")
        return

    total_comments = len(all_comments)
    for i in range(0, total_comments, 100):
        # 获取当前100条评论
        comments_chunk = all_comments[i:i + 100]
        filename = f"{user_id}_{i + 1}-{min(i + 100, total_comments)}.json"
        save_comments_to_file({"replies": comments_chunk}, filename)

    logging.info(f"所有评论数据已保存，共保存了 {total_comments} 条评论。")


# Example usage
if __name__ == "__main__":
    uid = 502474657  # 示例 UID
    main(uid)
