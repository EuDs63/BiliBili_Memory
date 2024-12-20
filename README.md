# BiliBili_Memory

## 说明
B站令人诟病的一点在于它不提供历史评论查询功能，你无法方便地翻到自己过去在哪，回复了什么内容，除非有人对你的回复内容进行回应。

作为一位B站多年的用户，以及抱着对自己过去几年来兴趣，言论等变化，我希望能获取到自己的历史评论，并进行一定的分析，几番寻找，我发现了[AICU - 我会一直看着你](https://www.aicu.cc/ )。

本项目获取b站评论部分是通过调用[AICU - 我会一直看着你](https://www.aicu.cc/ )实现，在此表示感谢。

本项目获取视频详细信息是基于[获取视频详细信息(web端)](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/info.md )这一文档，在此表示感谢。

本项目意在对自己的评论数据进行备份和分析。

## 使用方法
1. 安装依赖
  ```shell
  pip install -r requirements.txt
  ```
2. 修改`main.py`中的`uid`
3. 运行
  ```shell
  python main.py
  ```

## 程序逻辑 
1. 通过[AICU - 我会一直看着你](https://www.aicu.cc/ )获取uid所对应的所有评论
2. 对获取到的评论进行数据处理
   1. 格式转换
   2. 由`oid`,`rpid`,`type`转换评论的源链接
   3. 由`oid`,`type`获取评论的源地址信息(分区，up主信息)
3. 对得到的数据进行一定分析

## 学到的知识
### aicu是如何获取到用户评论?
[aicu是如何运作的](https://www.aicu.cc/help?id=11 )是这样介绍的:

>先通过uid获取到该uid的所有动态 将其存入数据库中
>再通过uid type进行去重 排除评论数为0的动态
> 随后开始获取这些动态的所有评论

着实是一个大工程，我十分佩服。

### B站评论数据量有多大，怎么存储?
[aicu是如何运作的](https://www.aicu.cc/help?id=11 )是这样介绍的:

>前文已经说到数据量都是以十亿做单位的
>评论数据大概有70亿条数据
>采用clickhouse储存 占用了约500g的存储空间

- 我有点惊讶，居然才500g，也就是每个人都能存储一份b站的评论数据
- ClickHouse是一个用于联机分析(OLAP)的列式数据库管理系统(DBMS)。

### 为什么是列式存储
参见[什么是ClickHouse？ | ClickHouse Docs](https://clickhouse.com/docs/zh )

### aicu如何根据oid和rpid获取到评论的源链接
```javascript
    let url0;
    switch (item.dyn.type) {
        case 17:
            url0 = `https://t.bilibili.com/${item.dyn.oid}#reply${item.rpid}`;
                break;
        case 1:
            url0 = `https://www.bilibili.com/video/av${item.dyn.oid}#reply${item.rpid}`;
            break;
        case 12:
            url0 = `https://www.bilibili.com/read/cv${item.dyn.oid}#reply${item.rpid}`;
            break;
        default:
            // 目前仍不知道这里的zhtype是什么
            url0 = `https://t.bilibili.com/${item.dyn.oid}?type=${zhtype(item.dyn.type)}#reply${item.rpid}`;
            break;
    }
```

### 如何由`oid`,`type`获取评论的源地址信息(分区，up主信息)
1. 首先由`type`判断是视频，专栏还是动态
2. `type`为1时，是视频，`oid`为av号 调用[获取视频详细信息(web端)](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/info.md )获取视频分区，up主信息
3. `type`为12时，是专栏，`oid`为cv号 调用`"https://www.bilibili.com/read/cv{oid}#reply{rpid}"`
4. `type`为17时，是动态，`oid`为动态号 调用[获取动态详情](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/dynamic/detail.md )
5. 其他情况，暂时不知道怎么处理,先不管

## Todo
- [ ] 集成为NoneBot插件
- [ ] 写个web ui (aicu已经有个能用的web ui了,没啥必要。但我可以借此练手数据展示)

## 参考
- [aicu是如何运作的](https://www.aicu.cc/help?id=11 )
- [什么是ClickHouse？ | ClickHouse Docs](https://clickhouse.com/docs/zh )