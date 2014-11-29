ALTER TABLE `accounts` ADD `key` VARCHAR(19) DEFAULT '' AFTER `creation`;
ALTER TABLE `accounts` ADD `points` INT(8) DEFAULT '0' AFTER `key`;
ALTER TABLE `accounts` ADD `lastpost` INT(11) DEFAULT '0' AFTER `points`;
ALTER TABLE `accounts` ADD `web_access` INT(4) DEFAULT '0' AFTER `lastpost`;

CREATE TABLE IF NOT EXISTS `login_history` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `account` varchar(32) NOT NULL,
  `ip` varchar(32) NOT NULL,
  `platform` varchar(32) NOT NULL,
  `browser` varchar(32) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `time` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;
