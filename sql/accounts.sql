ALTER TABLE `accounts` ADD `key` VARCHAR(19) AFTER `creation`;
ALTER TABLE `accounts` ADD `points` INT(8) AFTER `key`;
