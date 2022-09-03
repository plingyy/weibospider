# weibospider

Introduction:
To get all the weibo data included text and comments of a certain user.

Prerequiste:
1. Python3 environment
2. Run weibo_create.sql in your own mysql database (no need if you only want the csv version)
3. Change the database information, userID and cookie in config.

注意事项
1. 在config中添加想要爬取的账户ID，并加入cookie。账户ID不是用户名而是一串数字，可以在主页的url里看到。
2. 如果想要爬自己的微博，需要在登录后获取自己的cookie。建议先登录，否则会有一些微博自动被和谐而爬不下来。
3. 数据存入了本地数据库，需要在mysql里先跑一下 weibo_create.sql 这个文件生成表，config里改成数据库连接的名称和密码。
4. 数据同时还以csv格式保存在了代码同一地址下。
5. 如果有遇到“敏感信息”这样的输出，建议重新登录一次更改cookie就行。按理来说不会出现滴～


#### 超级超级超级无敌小白，第一次改别人的爬虫代码（甚至是第一次弄好本地数据库）。源码是根据微博客户端写的，最近微博网页改版了看着还挺好爬的，比客户端还规整一些，于是就把源代码改简单了一点更适合我这样的菜鸟理解，微博原文和评论合在一张表里。但这就不太适合爬有非常多评论的账号。建议有需求的小伙伴改回两个表的版本。
#### 第一次写爬虫，代码在不同的账户估计会遇到很多的问题，只能说在我只发了200多条的小号上是可以正常跑的🥲

源码地址：https://gitee.com/chengrongkai/OpenSpiders/tree/master/weiboSpider
