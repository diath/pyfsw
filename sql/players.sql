ALTER TABLE `players` ADD `comment` VARCHAR(255) DEFAULT '' AFTER `skill_fishing_tries`;
ALTER TABLE `players` ADD `hidden` TINYINT(1) DEFAULT '0' AFTER `comment`;
ALTER TABLE `players` ADD `postcount` INT(11) NOT NULL DEFAULT '0' AFTER `hidden`;
