import requests
import logging
import json
import os

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 获取视频基本信息
# [bilibili-API-collect/docs/video/info.md at master · SocialSisterYi/bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/info.md )
def get_video_info(oid):
    """ 根据 oid 和 type 获取视频详细信息（分区和up主信息） """
    video_url = f"https://api.bilibili.com/x/web-interface/wbi/view?aid={oid}"

    try:
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        }
        response = requests.get(video_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data['code'] != 0:
            logging.error(f"获取视频信息失败，错误代码：{data['code']}")
            return None

        video_info = data['data']
        return {
            'author_name': video_info['owner']['name'],
            'author_uid': video_info['owner']['mid'],
            'category': video_info['tname'],  # 视频分类
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"请求视频信息失败: {e}")
        return None


# 获取动态基本信息
# [bilibili-API-collect/docs/dynamic/detail.md at master · SocialSisterYi/bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/dynamic/detail.md )
def get_dynamic_info(dynamic_id):
    """ 根据动态ID获取动态详细信息 """
    dynamic_url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?id={dynamic_id}"

    try:
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        }
        response = requests.get(dynamic_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data['code'] != 0:
            logging.error(f"获取动态信息失败，错误代码：{data['code']},动态ID：{dynamic_id}")
            return None

        dynamic_info = data['data']['item']
        author_info = dynamic_info["modules"]["module_author"]
        return {
            "author_name": author_info["name"],
            "author_uid": author_info["mid"],
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"请求动态信息失败: {e}")
        return None


# 获取专栏详细信息
# [bilibili-API-collect/docs/article/info.md at master · SocialSisterYi/bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/article/info.md )
def get_article_info(oid):
    """ 根据专栏ID获取专栏详细信息 """
    article_url = f"https://api.bilibili.com/x/article/viewinfo?id={oid}"

    try:
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        }
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['code'] != 0:
            logging.error(f"获取专栏信息失败，错误代码：{data['code']}")
            return None
        article_info = data['data']
        author_name = article_info['author_name']
        author_uid = article_info['mid']
        return {
            'author_name': author_name,
            'author_uid': author_uid,
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"请求专栏信息失败: {e}")
        return None


# 生成评论源链接
def generate_source_url(oid, rpid, comment_type):
    """ 根据 oid, rpid, type 生成评论源链接 """

    if oid and rpid and comment_type is not None:
        if comment_type == 1:
            return f"https://www.bilibili.com/video/av{oid}#reply{rpid}"
        elif comment_type == 12:
            return f"https://www.bilibili.com/read/cv{oid}#reply{rpid}"
        elif comment_type == 17:
            return f"https://t.bilibili.com/{oid}reply{rpid}"
    return None


def fetch_extra_info(oid, comment_type):
    logging.info(f"尝试获取额外信息：oid={oid}, type={comment_type}")

    """ 获取评论的额外信息（视频、动态、专栏） """
    if comment_type == 1:
        return get_video_info(oid)
    elif comment_type == 12:
        return get_article_info(oid)
    elif comment_type == 17:
        return get_dynamic_info(oid)
    return None


# 处理单条评论数据
def process_comment(comment):
    """ 格式转换：调整评论数据格式，保留所需信息 """
    rpid = comment.get('rpid')
    oid = comment.get('dyn', {}).get('oid')
    comment_type = comment.get('dyn', {}).get('type')

    source_url = generate_source_url(oid, rpid, comment_type)
    extra_info = fetch_extra_info(oid, comment_type)

    return {
        'rpid': rpid,
        'message': comment.get('message'),
        'time': comment.get('time'),
        'rank': comment.get('rank'),
        'oid': oid,
        'type': comment_type,
        'source_url': source_url,
        'extra_info': extra_info,
    }


# 处理评论数据
def process_comments(comments):
    """ 处理获取到的所有评论，进行格式转换，并添加视频信息 """
    processed_comments = []
    comments_count = len(comments)

    for comment in comments:
        logging.info(f"处理评论数据：{comments.index(comment) + 1}/{comments_count}")
        processed_comment = process_comment(comment)

        processed_comments.append(processed_comment)

    return processed_comments


# 保存处理后的评论
def save_processed_comments(comments, filename):
    """ 将处理后的评论保存到JSON文件 """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"replies": comments}, f, ensure_ascii=False, indent=4)
        logging.info(f"处理后的评论已成功保存到 {filename}")
    except Exception as e:
        logging.error(f"保存处理后的评论时出错: {e}")


# 主程序：对获取的评论数据进行处理并保存
def process_file(user_id, input_filename):
    """ 主程序：读取评论，进行数据处理并保存 """
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            comments = raw_data.get("replies", [])

        if not comments:
            logging.warning("没有评论数据需要处理")
            return

        logging.info(f"读取{input_filename}文件中{len(comments)}条评论")

        # 处理评论数据
        processed_comments = process_comments(comments)

        # 生成输出文件名,输入文件名前面加上processed_
        output_filename = input_filename.replace(user_id, f"processed_{user_id}")

        # 保存处理后的评论
        save_processed_comments(processed_comments, output_filename)

    except Exception as e:
        logging.error(f"读取或处理评论时出错: {e}")


def main(user_id):
    # 获取output文件夹下的所有以uid开头的json文件
    files = [f for f in os.listdir("output") if f.startswith(user_id) and f.endswith(".json")]
    if not files:
        logging.warning("没有找到需要处理的文件")
        return
    else:
        logging.info(f"找到了{len(files)}个文件")
        for file in files:
            logging.info(f"正在处理文件：{file}")
            file_path = os.path.join("output", file)
            process_file(user_id, file_path)


# 示例用法
if __name__ == "__main__":
    #  获取output文件夹下的所有以json文件
    uid = "7"  # 示例 UID
    main(uid)
