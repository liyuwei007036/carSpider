CREATE DATABASE spider DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

use spider;

CREATE TABLE `car` (
  `che168_id` bigint(20) NOT NULL,
  `vehicle_name` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `province` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `price` double(10,2) DEFAULT NULL,
  `distance` double DEFAULT NULL,
  `volume` varchar(255) DEFAULT NULL,
  `trubo` varchar(255) DEFAULT NULL,
  `last_date` varchar(0) DEFAULT NULL,
  `update_date` datetime DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `owner` varchar(255) DEFAULT NULL,
  `gb` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`che168_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;