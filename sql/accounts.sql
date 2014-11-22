ALTER TABLE `accounts` ADD `key` VARCHAR(19) DEFAULT '' AFTER `creation`;
ALTER TABLE `accounts` ADD `points` INT(8) DEFAULT '0' AFTER `key`;
ALTER TABLE `accounts` ADD `lastpost` INT(11) DEFAULT '0' AFTER `points`;
