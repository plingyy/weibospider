create table `weibo` (
`id` varchar(64) NOT NULL COMMENT '主键',
`user_id` varchar(11) NOT NULL COMMENT '用户ID',
`mblogid` varchar(64) NOT NULL COMMENT '微博ID',
`screen_name` varchar(64) NOT NULL COMMENT '用户昵称',
`text` varchar(1024) NOT NULL COMMENT '微博内容',
`pics` varchar(1024) NOT NULL COMMENT '图片列表',
`video_url` varchar(1024) NOT NULL COMMENT '视频列表',
`location` varchar(128) NOT NULL COMMENT '发布地点',
`created_at` datetime NOT NULL COMMENT '发布时间',
`source` varchar(128) NOT NULL COMMENT '微博来源',
`attitudes_count` int(11) NOT NULL COMMENT '点赞数',
`comments_count` int(11) NOT NULL COMMENT '评论数',
`reposts_count` int(11) NOT NULL COMMENT '转发数',
`retweet_content` varchar(1024) NOT NULL COMMENT '转发原内容',
`comments` varchar(1024) NOT NULL COMMENT '评论',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;