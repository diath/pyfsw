CREATE TABLE IF NOT EXISTS `library` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(32) NOT NULL,
  `name` varchar(32) NOT NULL,
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `content` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`,`uri`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;
