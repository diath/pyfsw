CREATE TABLE IF NOT EXISTS `news` (
  `id` int(4) NOT NULL AUTO_INCREMENT,
  `timestamp` int(11) NOT NULL,
  `header` varchar(64) NOT NULL,
  `content` text NOT NULL,
  `author_id` int(11) NOT NULL,
  `thread_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;
