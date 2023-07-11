CREATE TABLE `userinfo` (
  `id` varchar(40) NOT NULL,
  `sname` varchar(11) DEFAULT NULL,
  `sex` varchar(1) DEFAULT NULL COMMENT '1是男性 0是女性',
  `saddress` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `uuid` FOREIGN KEY (`id`) REFERENCES `login` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `login` (
  `id` varchar(40) NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` text NOT NULL COMMENT '加密后',
  `token` text,
  `status` char(1) DEFAULT NULL COMMENT '0代表从未登录，1代表登录，2代表登出，-1代表封禁',
  `registertime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;