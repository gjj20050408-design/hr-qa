-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: hr_policy_qa
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `hr_policy_qa`
--

/*!40000 DROP DATABASE IF EXISTS `hr_policy_qa`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `hr_policy_qa` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `hr_policy_qa`;

--
-- Table structure for table `announcement_reads`
--

DROP TABLE IF EXISTS `announcement_reads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcement_reads` (
  `read_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `announcement_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `read_at` datetime DEFAULT NULL,
  `remind_count` int DEFAULT NULL,
  PRIMARY KEY (`read_id`),
  KEY `announcement_id` (`announcement_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `announcement_reads_ibfk_1` FOREIGN KEY (`announcement_id`) REFERENCES `announcements` (`announcement_id`) ON DELETE CASCADE,
  CONSTRAINT `announcement_reads_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcement_reads`
--

LOCK TABLES `announcement_reads` WRITE;
/*!40000 ALTER TABLE `announcement_reads` DISABLE KEYS */;
INSERT INTO `announcement_reads` VALUES ('0fb89bad8bdf424c89a1038680c7204b','70a2df8a2fad4df3be52c63b0c733209','user123',1,'2026-06-30 14:48:51',0),('2a3b6984d2674142984d9fc8b9c93b78','895d1d0412264528a360867a9290d821','user123',1,'2026-06-30 15:03:13',0),('3ba25ea85dd74a409ab09779994510ab','d7fe14f1b668460c8d5241a2e7de5753','user123',1,'2026-06-30 13:07:55',0),('615c1bfe694d48c4a390bae51ccd2bae','d7fe14f1b668460c8d5241a2e7de5753','2c2e97aac553494f91f1a0f742bbe387',1,'2026-07-01 01:07:39',0),('6542f6e26ed34f81a3826f1d21ed7468','d7fe14f1b668460c8d5241a2e7de5753','user-admin-001',0,NULL,0),('7ce4125034a744cc8c54b050f8c62a96','70a2df8a2fad4df3be52c63b0c733209','hr001',1,'2026-06-30 14:55:28',0),('90b68863d080495c8418a88b59c39fd0','d7fe14f1b668460c8d5241a2e7de5753','hr001',1,'2026-06-30 12:43:48',0);
/*!40000 ALTER TABLE `announcement_reads` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `announcements`
--

DROP TABLE IF EXISTS `announcements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcements` (
  `announcement_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `priority` enum('NORMAL','IMPORTANT','URGENT') COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_type` enum('ALL','DEPARTMENT','ROLE') COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_ids` json DEFAULT NULL,
  `attachment` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `published_by` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `published_at` datetime DEFAULT NULL,
  PRIMARY KEY (`announcement_id`),
  KEY `published_by` (`published_by`),
  CONSTRAINT `announcements_ibfk_1` FOREIGN KEY (`published_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcements`
--

LOCK TABLES `announcements` WRITE;
/*!40000 ALTER TABLE `announcements` DISABLE KEYS */;
INSERT INTO `announcements` VALUES ('70a2df8a2fad4df3be52c63b0c733209','您的纠错反馈已被驳回','您针对制度文档《绩效制度》「绩效制度」提交的纠错反馈未被采纳。\n审核意见：滚','IMPORTANT','ROLE','[\"user123\"]',NULL,'user123','2026-06-30 14:48:46'),('895d1d0412264528a360867a9290d821','您的纠错反馈已被驳回','您针对制度文档《薪酬制度》「薪酬制度」提交的纠错反馈未被采纳。\n审核意见：123','IMPORTANT','ROLE','[\"user123\"]',NULL,'user123','2026-06-30 15:03:09'),('d7fe14f1b668460c8d5241a2e7de5753','不是哥们','123123','NORMAL','ALL','null',NULL,'hr001','2026-06-30 12:43:37');
/*!40000 ALTER TABLE `announcements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `log_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `resource_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `resource_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `detail` json DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES ('040971f3eced4f06a2819ac977746327','user123','user_disable','user','2c2e97aac553494f91f1a0f742bbe387','{\"name\": \"哈哈哈\", \"employee_id\": \"1234\"}',NULL,NULL,'2026-07-01 00:35:45'),('04ea77647f484176b89ab4b62970e2c8','user-admin-001','login_success','user','user-admin-001',NULL,'127.0.0.1','python-requests/2.34.2','2026-06-29 01:59:23'),('0879f251f3f144feb65896a9a1df132d','hr001','document_archive','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 02:53:38'),('0cd529b11f864868919675ff7eb184d9','2c2e97aac553494f91f1a0f742bbe387','personal_data_denied','personal_data','','{\"denied\": [], \"reason\": \"extraction_failed\", \"extraction\": {\"confidence\": 0.0, \"query_type\": \"personal_data\", \"is_self_query\": false, \"target_persons\": [], \"requested_fields\": []}}','',NULL,'2026-06-29 00:30:50'),('10134dfd6216486c8c8fdcb5ea711e84','user-admin-001','login_success','user','user-admin-001',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-26 01:02:06'),('10a6f0d54e10413188995f409e631f65','hr001','document_archive','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 02:50:12'),('111087cefcdf4f439527150515ff009b','2c2e97aac553494f91f1a0f742bbe387','login_success','user','2c2e97aac553494f91f1a0f742bbe387',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-29 01:26:17'),('12357bbdc1244f87b30b7aac2eeff6f7','user123','document_archive','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027',NULL,NULL,NULL,'2026-06-30 13:48:53'),('13e92a5a19e549079c3f3ce60a6df363','hr001','login_success','user','hr001',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-07-01 01:01:53'),('16d6bffbaa3c486aa0638b403ac47eed','user123','document_update','document','73b945e6ca349f8d','{\"title\": \"绩效制度\"}',NULL,NULL,'2026-06-30 14:05:11'),('18107424782e4e86aae5e9504b247e91','user123','document_update','document','2a046aad5cfb4948a9cf99c31b2c4511','{\"title\": \"薪酬制度\"}',NULL,NULL,'2026-06-30 13:43:09'),('1b953b200448481cacec0dcf6e987613','user123','document_update','document','2a046aad5cfb4948a9cf99c31b2c4511','{\"title\": \"薪酬制度\"}',NULL,NULL,'2026-06-30 14:32:22'),('2330b2f5165b4d81aab36cf7213284e3','2c2e97aac553494f91f1a0f742bbe387','login_success','user','2c2e97aac553494f91f1a0f742bbe387',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-07-01 01:07:34'),('2357589a0c1d4ae4b25e72003e93453d','user123','document_archive','document','2a046aad5cfb4948a9cf99c31b2c4511',NULL,NULL,NULL,'2026-06-30 13:24:01'),('26805d2fa39d488cb4ee0d5a34881886','user123','document_archive','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 13:39:55'),('26856cbc92eb43cdb00725e19fd9b1df','hr001','document_create','document','2a046aad5cfb4948a9cf99c31b2c4511','{\"title\": \"薪酬制度\", \"format\": \"word\"}',NULL,NULL,'2026-06-30 03:29:23'),('2ac375eb62054288a6e58ca0f9888318','user123','document_update','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027','{\"title\": \"考勤制度\"}',NULL,NULL,'2026-06-30 13:42:36'),('2f24f32659784a16944c993affd5de17','user123','document_restore','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027',NULL,NULL,NULL,'2026-06-30 13:50:39'),('334743c4ba49460d97dfd35de888c2d2','2c2e97aac553494f91f1a0f742bbe387','user_register','user','2c2e97aac553494f91f1a0f742bbe387','{\"name\": \"哈哈哈\", \"employee_id\": \"1234\"}',NULL,NULL,'2026-06-29 00:08:27'),('34a48883a67d4227bc64ac0709f2a4a6','hr001','login_success','user','hr001',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 15:03:49'),('3772087963934ad59b745e088be2be3f','user123','document_delete','document','d5fa6f616fda49bab22fc338d36f502a',NULL,NULL,NULL,'2026-06-30 14:31:58'),('3a0c2214fb884cba9b63dbde23a47998','user123','document_archive','document','2a046aad5cfb4948a9cf99c31b2c4511',NULL,NULL,NULL,'2026-06-30 13:23:07'),('3b1a9e67df1848669b24518743836f77','user123','document_archive','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027',NULL,NULL,NULL,'2026-06-30 13:50:38'),('3e4e52bdbb2d43078661fde6245b5a84','user-admin-001','login_success','user','user-admin-001',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-26 00:36:16'),('3e9a4b8779714236ab5097a032db9ec1','2c2e97aac553494f91f1a0f742bbe387','personal_data_denied','personal_data','','{\"denied\": [], \"reason\": \"extraction_failed\", \"extraction\": {\"confidence\": 0.1, \"query_type\": \"personal_data\", \"is_self_query\": false, \"target_persons\": [], \"requested_fields\": []}}','',NULL,'2026-06-29 00:40:00'),('4830e37a9f774752823b1c019a2a15ac','user123','login_success','user','user123',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 12:54:57'),('493f6f7294884883a62ed33926c2351a','user123','document_update','document','87d0b8363a47c8ca','{\"title\": \"福利制度\"}',NULL,NULL,'2026-06-30 14:05:15'),('4afa37d2984d4653b65cdd6446ba524a','user123','document_archive','document','2a046aad5cfb4948a9cf99c31b2c4511',NULL,NULL,NULL,'2026-06-30 13:23:06'),('5850a3b991bd4e9992492d3bf98e1821','user123','login_success','user','user123',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 15:02:52'),('58740e4586aa457980d62027044eaccb','user123','document_update','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027','{\"title\": \"考勤制度\"}',NULL,NULL,'2026-06-30 14:39:40'),('5898d1e62b294072a1e5d6c37749c453','hr001','document_archive','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 03:27:11'),('5e0d21eb43624bfd9f4713c6adec9c32','2c2e97aac553494f91f1a0f742bbe387','login_success','user','2c2e97aac553494f91f1a0f742bbe387',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-29 00:25:22'),('6ba758839f2843f998c92ac1b032003c','2c2e97aac553494f91f1a0f742bbe387','login_success','user','2c2e97aac553494f91f1a0f742bbe387',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-29 03:31:55'),('724b729c75ab42869b2ebe720587d779','hr001','login_success','user','hr001',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 02:33:03'),('741f1d1342fe476cafd6c612be96919a','user123','document_archive','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027',NULL,NULL,NULL,'2026-06-30 13:40:13'),('7c1d5bb7058e4b46954f33fdec57a15e','hr001','login_success','user','hr001',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 12:28:16'),('854ea2a826d845f892d8383ccb100a52','user123','document_update','document','f56c26f55490432e98cb3696399c3f8c','{\"title\": \"绩效制度\"}',NULL,NULL,'2026-06-30 13:42:55'),('8b533a148dca4bf8aeca827361aa248f','user123','login_success','user','user123',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 12:26:53'),('8bc19be5f62941e2bf9708ae8251ae23','user123','document_restore','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027',NULL,NULL,NULL,'2026-06-30 13:49:58'),('921609e85ea0417f96abf1cf1603076c','user123','document_delete','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 14:32:00'),('923b76a34c704cec8a2811343c2122c0','hr001','document_create','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027','{\"title\": \"考勤制度\", \"format\": \"word\"}',NULL,NULL,'2026-06-30 02:57:13'),('940c1e158cdf485182483a7e994f7282','hr001','login_success','user','hr001',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 14:55:22'),('964667ea83fb466baee449fe35550357','user-admin-001','login_success','user','user-admin-001',NULL,'127.0.0.1','curl/8.12.1','2026-06-30 13:41:19'),('96ad50d98555410498105525396af273','user123','document_archive','document','2a046aad5cfb4948a9cf99c31b2c4511',NULL,NULL,NULL,'2026-06-30 13:30:07'),('9cb1edbe25694d749a41b9d4895dc154','user123','user_update','user','2c2e97aac553494f91f1a0f742bbe387','{\"changed\": {\"status\": \"active\"}}',NULL,NULL,'2026-07-01 00:40:43'),('a74cecbcc0a94343a59f829c8bc0ce64','user123','document_archive','document','2a046aad5cfb4948a9cf99c31b2c4511',NULL,NULL,NULL,'2026-06-30 13:40:00'),('b1ffce1024b442c1a48baf3cfbe42620','hr001','document_archive','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 02:49:54'),('b74eb0501e3549f0964a6e159882c854','2c2e97aac553494f91f1a0f742bbe387','login_success','user','2c2e97aac553494f91f1a0f742bbe387',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 12:10:36'),('bb1ef536db4643feae3e2320c8fafbf3','user123','document_archive','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027',NULL,NULL,NULL,'2026-06-30 13:50:45'),('c04772328af746f6bda4a9a532217ec1','user123','document_archive','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 13:30:12'),('c04f1b9159a54991ae7a064e7a223612','hr001','document_update','document','f56c26f55490432e98cb3696399c3f8c','{\"title\": \"绩效制度\"}',NULL,NULL,'2026-06-30 03:27:24'),('c3e5e49326ce4e1a81dc09a4e803a1b8','2c2e97aac553494f91f1a0f742bbe387','personal_data_denied','personal_data','','{\"denied\": [], \"reason\": \"extraction_failed\", \"extraction\": {\"confidence\": 0.0, \"query_type\": \"personal_data\", \"is_self_query\": false, \"target_persons\": [], \"requested_fields\": []}}','',NULL,'2026-06-29 00:36:22'),('c5169e3257744e90adf6c25a075f96ea','user123','document_archive','document','2a046aad5cfb4948a9cf99c31b2c4511',NULL,NULL,NULL,'2026-06-30 13:40:56'),('c59b88e112b14c16aa93e796dcc3501e','hr001','document_archive','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 02:49:52'),('cb52d185bbe8442082d7e40fd23c5018','user123','document_archive','document','2a046aad5cfb4948a9cf99c31b2c4511',NULL,NULL,NULL,'2026-06-30 13:30:13'),('cc2c88ddce6d4d5c958b28f68db9b445','user-admin-001','login_success','user','user-admin-001',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-26 00:31:02'),('d02f49b19fd845d699e3776b75414338','hr001','document_update','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027','{\"title\": \"考勤制度\"}',NULL,NULL,'2026-06-30 03:16:26'),('d347a3022d4b47f5a0082387ea64513c','user123','login_success','user','user123',NULL,'127.0.0.1','curl/8.12.1','2026-06-30 12:56:11'),('d4e997b37367431bb77e032e991e6e6f','hr001','document_archive','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 02:49:50'),('d52bb94fbfaf4a55876dc3f2530c5629','user123','login_success','user','user123',NULL,'127.0.0.1','curl/8.12.1','2026-06-30 12:55:56'),('d671a35be8b8410883862c01ec7df30d','user123','document_archive','document','2a046aad5cfb4948a9cf99c31b2c4511',NULL,NULL,NULL,'2026-06-30 13:29:14'),('d9ac77262f6a481b86b6e892e5c63574','2c2e97aac553494f91f1a0f742bbe387','login_success','user','2c2e97aac553494f91f1a0f742bbe387',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 12:15:45'),('dd232a1e821c409f875a27e0fbcff30c','user123','login_success','user','user123',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-07-01 01:02:15'),('e3c7b512e49b4fab90f727068265229a','2c2e97aac553494f91f1a0f742bbe387','login_success','user','2c2e97aac553494f91f1a0f742bbe387',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 02:31:31'),('e4cfdc4cbe2e4ecf94b539929e533901','user123','document_archive','document','2a046aad5cfb4948a9cf99c31b2c4511',NULL,NULL,NULL,'2026-06-30 13:40:14'),('e61242b83c5b41bab068684da6e4f925','2c2e97aac553494f91f1a0f742bbe387','login_success','user','2c2e97aac553494f91f1a0f742bbe387',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-29 00:08:59'),('e8d10c0b7ea44fe3b3f86c15bab74791','hr001','login_success','user','hr001',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-07-01 00:46:02'),('ee2a2b55e362474f9a778540e2e32c7f','user123','document_archive','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027',NULL,NULL,NULL,'2026-06-30 13:48:50'),('ee80ae05a1154944afa3230fd15d8bfc','user123','login_success','user','user123',NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','2026-06-30 23:56:32'),('f53448a57020471eab89a78c5eb45bc5','hr001','document_archive','document','f56c26f55490432e98cb3696399c3f8c',NULL,NULL,NULL,'2026-06-30 02:49:48'),('fd7d81f23875461689fa895530e9186a','user123','document_restore','document','7ab9fe6efcb24b4e9d9c77a9c5a1f027',NULL,NULL,NULL,'2026-06-30 13:50:46');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `benefit_reports`
--

DROP TABLE IF EXISTS `benefit_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `benefit_reports` (
  `report_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year` int NOT NULL,
  `tenure_years` int DEFAULT NULL,
  `items` json DEFAULT NULL,
  `summary` text COLLATE utf8mb4_unicode_ci,
  `model` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`report_id`),
  UNIQUE KEY `uq_benefit_user_year` (`user_id`,`year`),
  CONSTRAINT `benefit_reports_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `benefit_reports`
--

LOCK TABLES `benefit_reports` WRITE;
/*!40000 ALTER TABLE `benefit_reports` DISABLE KEYS */;
INSERT INTO `benefit_reports` VALUES ('02468c63468e468a8783c94d64d33370','hr001',2025,2,'[{\"title\": \"带薪年假\", \"value\": \"5 天/年\", \"category\": \"休假\", \"description\": \"您当前工龄 2 年，按《休假制度》可享受 5 天带薪年假。\", \"source_rule\": \"rule-annual-leave\"}, {\"title\": \"病假薪酬\", \"value\": \"最高全额\", \"category\": \"薪酬\", \"description\": \"病假≤2天全额工资；3-30天按基本工资80%；超30天按当地最低工资标准。\", \"source_rule\": \"rule-sick-leave-pay\"}, {\"title\": \"加班补偿\", \"value\": \"1.5–3 倍\", \"category\": \"薪酬\", \"description\": \"工作日加班1.5倍、休息日2倍（或调休）、法定节假日3倍工资。需提前审批。\", \"source_rule\": \"rule-overtime-pay\"}, {\"title\": \"婚假\", \"value\": \"3 天起\", \"category\": \"休假\", \"description\": \"法定婚假3天，晚婚（男≥25/女≥23）可增加7天，需在领证后一年内休完。（您已婚，如尚未休可向HR申请。）\", \"source_rule\": \"rule-marriage-leave\"}]','亲爱的张HR，感谢你过去两年的全心付出。这一年，我们特别为你梳理了 2025 年度专属权益。无论是一次放松身心的带薪年假，还是生病时让人安心的薪酬保障，或是每一份辛苦都有回应的加班补偿，以及如果尚未休满可以随时申请的婚假——这些，都是公司对你不言自明的感谢与守护。愿你在拼搏的同时，也记得为自己留一份从容。有任何需要，我们就在你身边。','deepseek-v4-pro','2026-07-01 00:48:11'),('02be2dc902cd464281c79891d9d5c575','2c2e97aac553494f91f1a0f742bbe387',2025,0,'[{\"title\": \"带薪年假\", \"value\": \"5 天/年\", \"category\": \"休假\", \"description\": \"您当前工龄 0 年，按《休假制度》可享受 5 天带薪年假。\", \"source_rule\": \"rule-annual-leave\"}, {\"title\": \"病假薪酬\", \"value\": \"最高全额\", \"category\": \"薪酬\", \"description\": \"病假≤2天全额工资；3-30天按基本工资80%；超30天按当地最低工资标准。\", \"source_rule\": \"rule-sick-leave-pay\"}, {\"title\": \"加班补偿\", \"value\": \"1.5–3 倍\", \"category\": \"薪酬\", \"description\": \"工作日加班1.5倍、休息日2倍（或调休）、法定节假日3倍工资。需提前审批。\", \"source_rule\": \"rule-overtime-pay\"}, {\"title\": \"婚假\", \"value\": \"3 天起\", \"category\": \"休假\", \"description\": \"法定婚假3天，晚婚（男≥25/女≥23）可增加7天，需在领证后一年内休完。（祝您未来喜结良缘时及时申请。）\", \"source_rule\": \"rule-marriage-leave\"}]','亲爱的哈哈哈，感谢你在2025年成为我们团队的一员。虽然你才刚刚开启职业生涯，但我们已为你准备了一份贴心保障：带薪年假帮你放松充电，弹性病假让你安心休养，公正的加班补偿体现每一份付出都有回报，而婚假更是为未来的幸福时刻备好祝福。愿这些关怀伴你稳步前行，工作顺意，生活温暖。','deepseek-v4-pro','2026-07-01 01:08:40'),('62784586949742048c6816590299f0d4','user123',2025,2,'[{\"title\": \"带薪年假\", \"value\": \"5 天/年\", \"category\": \"休假\", \"description\": \"您当前工龄 2 年，按《休假制度》可享受 5 天带薪年假。\", \"source_rule\": \"rule-annual-leave\"}, {\"title\": \"病假薪酬\", \"value\": \"最高全额\", \"category\": \"薪酬\", \"description\": \"病假≤2天全额工资；3-30天按基本工资80%；超30天按当地最低工资标准。\", \"source_rule\": \"rule-sick-leave-pay\"}, {\"title\": \"加班补偿\", \"value\": \"1.5–3 倍\", \"category\": \"薪酬\", \"description\": \"工作日加班1.5倍、休息日2倍（或调休）、法定节假日3倍工资。需提前审批。\", \"source_rule\": \"rule-overtime-pay\"}, {\"title\": \"婚假\", \"value\": \"3 天起\", \"category\": \"休假\", \"description\": \"法定婚假3天，晚婚（男≥25/女≥23）可增加7天，需在领证后一年内休完。（祝您未来喜结良缘时及时申请。）\", \"source_rule\": \"rule-marriage-leave\"}]','亲爱的测试用户，感谢您在过去两年里的辛勤付出。我们为您整理了2025年度专属权益，希望能帮助您更好地平衡工作与生活。无论是5天带薪年假，还是灵活的加班补偿方案，以及贴心设计的病假薪酬与婚假支持，都承载着公司对您身心健康的关爱。祝愿您在需要休息时安心休养，在重要人生时刻尽享喜悦。如有任何疑问，欢迎随时联系我们。祝您新的一年工作顺心，生活幸福！','deepseek-v4-pro','2026-07-01 00:16:53'),('8a302d6f649f4743a9ddfe79223b9ed5','2c2e97aac553494f91f1a0f742bbe387',2026,0,'[{\"title\": \"带薪年假\", \"value\": \"5 天/年\", \"category\": \"休假\", \"description\": \"您当前工龄 0 年，按《休假制度》可享受 5 天带薪年假。\", \"source_rule\": \"rule-annual-leave\"}, {\"title\": \"病假薪酬\", \"value\": \"最高全额\", \"category\": \"薪酬\", \"description\": \"病假≤2天全额工资；3-30天按基本工资80%；超30天按当地最低工资标准。\", \"source_rule\": \"rule-sick-leave-pay\"}, {\"title\": \"加班补偿\", \"value\": \"1.5–3 倍\", \"category\": \"薪酬\", \"description\": \"工作日加班1.5倍、休息日2倍（或调休）、法定节假日3倍工资。需提前审批。\", \"source_rule\": \"rule-overtime-pay\"}, {\"title\": \"婚假\", \"value\": \"3 天起\", \"category\": \"休假\", \"description\": \"法定婚假3天，晚婚（男≥25/女≥23）可增加7天，需在领证后一年内休完。（祝您未来喜结良缘时及时申请。）\", \"source_rule\": \"rule-marriage-leave\"}]','亲爱的哈哈哈，欢迎加入我们的大家庭！2026年是您在这里的崭新起点，我们为您准备了一份贴心的权益保障，希望这些安排能陪伴您安心工作、从容生活。无论是放松调整的带薪休假，还是遇到身体不适时的关怀支持，或是辛苦加班后的合理回报，以及未来人生喜事中的温暖祝福，都体现了公司对每一位伙伴的珍视。愿这些小小的心意，能为您的新旅程增添一份踏实与美好。祝您在这里收获成长，也拥抱生活的每一份喜悦！','deepseek-v4-pro','2026-07-01 01:08:07'),('f12259fa9ad045098836f2b00d8f2df2','hr001',2026,2,'[{\"title\": \"带薪年假\", \"value\": \"5 天/年\", \"category\": \"休假\", \"description\": \"您当前工龄 2 年，按《休假制度》可享受 5 天带薪年假。\", \"source_rule\": \"rule-annual-leave\"}, {\"title\": \"病假薪酬\", \"value\": \"最高全额\", \"category\": \"薪酬\", \"description\": \"病假≤2天全额工资；3-30天按基本工资80%；超30天按当地最低工资标准。\", \"source_rule\": \"rule-sick-leave-pay\"}, {\"title\": \"加班补偿\", \"value\": \"1.5–3 倍\", \"category\": \"薪酬\", \"description\": \"工作日加班1.5倍、休息日2倍（或调休）、法定节假日3倍工资。需提前审批。\", \"source_rule\": \"rule-overtime-pay\"}, {\"title\": \"婚假\", \"value\": \"3 天起\", \"category\": \"休假\", \"description\": \"法定婚假3天，晚婚（男≥25/女≥23）可增加7天，需在领证后一年内休完。（您已婚，如尚未休可向HR申请。）\", \"source_rule\": \"rule-marriage-leave\"}]','张HR，您好！这是您 2026 年度的专属权益清单。您当前工龄 2 年，共梳理出 4 项核心权益。如对任何一项有疑问，欢迎随时咨询 HR 部门。','','2026-06-30 16:57:51'),('f2f53f0f957f426ba0a53fad61a9afa7','user123',2026,2,'[{\"title\": \"带薪年假\", \"value\": \"5 天/年\", \"category\": \"休假\", \"description\": \"您当前工龄 2 年，按《休假制度》可享受 5 天带薪年假。\", \"source_rule\": \"rule-annual-leave\"}, {\"title\": \"病假薪酬\", \"value\": \"最高全额\", \"category\": \"薪酬\", \"description\": \"病假≤2天全额工资；3-30天按基本工资80%；超30天按当地最低工资标准。\", \"source_rule\": \"rule-sick-leave-pay\"}, {\"title\": \"加班补偿\", \"value\": \"1.5–3 倍\", \"category\": \"薪酬\", \"description\": \"工作日加班1.5倍、休息日2倍（或调休）、法定节假日3倍工资。需提前审批。\", \"source_rule\": \"rule-overtime-pay\"}, {\"title\": \"婚假\", \"value\": \"3 天起\", \"category\": \"休假\", \"description\": \"法定婚假3天，晚婚（男≥25/女≥23）可增加7天，需在领证后一年内休完。（祝您未来喜结良缘时及时申请。）\", \"source_rule\": \"rule-marriage-leave\"}]','测试用户，您好！这是您 2026 年度的专属权益清单。您当前工龄 2 年，共梳理出 4 项核心权益。如对任何一项有疑问，欢迎随时咨询 HR 部门。','','2026-06-30 23:57:22');
/*!40000 ALTER TABLE `benefit_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `category_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` enum('DOCUMENT','FAQ') COLLATE utf8mb4_unicode_ci NOT NULL,
  `access_level` enum('ALL_ROLES','HR_ADMIN_ONLY','ADMIN_ONLY') COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_order` int DEFAULT NULL,
  PRIMARY KEY (`category_id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`category_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES ('cat_doc_attend','考勤制度','cat_doc_root','DOCUMENT','ALL_ROLES',7),('cat_doc_benefit','福利制度','cat_doc_root','DOCUMENT','ALL_ROLES',4),('cat_doc_contract','劳动合同','cat_doc_root','DOCUMENT','HR_ADMIN_ONLY',8),('cat_doc_handbook','员工手册','cat_doc_root','DOCUMENT','ALL_ROLES',10),('cat_doc_insurance','社保公积金','cat_doc_root','DOCUMENT','ALL_ROLES',9),('cat_doc_leave','休假制度','cat_doc_root','DOCUMENT','ALL_ROLES',2),('cat_doc_offboard','离职制度','cat_doc_root','DOCUMENT','HR_ADMIN_ONLY',13),('cat_doc_perf','绩效制度','cat_doc_root','DOCUMENT','ALL_ROLES',3),('cat_doc_promote','晋升制度','cat_doc_root','DOCUMENT','ALL_ROLES',12),('cat_doc_recruit','招聘制度','cat_doc_root','DOCUMENT','ALL_ROLES',5),('cat_doc_reward','奖惩制度','cat_doc_root','DOCUMENT','ALL_ROLES',11),('cat_doc_root','制度文档',NULL,'DOCUMENT','ALL_ROLES',0),('cat_doc_safe','安全生产','cat_doc_root','DOCUMENT','ALL_ROLES',14),('cat_doc_salary','薪酬制度','cat_doc_root','DOCUMENT','HR_ADMIN_ONLY',1),('cat_doc_train','培训制度','cat_doc_root','DOCUMENT','ALL_ROLES',6),('cat_faq_benefit','福利FAQ','cat_faq_root','FAQ','ALL_ROLES',54),('cat_faq_leave','休假FAQ','cat_faq_root','FAQ','ALL_ROLES',52),('cat_faq_perf','绩效FAQ','cat_faq_root','FAQ','ALL_ROLES',53),('cat_faq_recruit','招聘FAQ','cat_faq_root','FAQ','ALL_ROLES',55),('cat_faq_root','常见问题',NULL,'FAQ','ALL_ROLES',50),('cat_faq_salary','薪酬FAQ','cat_faq_root','FAQ','HR_ADMIN_ONLY',51),('cat_faq_train','培训FAQ','cat_faq_root','FAQ','ALL_ROLES',56);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_sessions`
--

DROP TABLE IF EXISTS `chat_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_sessions` (
  `session_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_pinned` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `chat_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_sessions`
--

LOCK TABLES `chat_sessions` WRITE;
/*!40000 ALTER TABLE `chat_sessions` DISABLE KEYS */;
INSERT INTO `chat_sessions` VALUES ('05f856ba8db545ac9a6d575a1fa8bcd2','hr001','迟到会有什么处罚？',0,'2026-06-30 12:39:57','2026-06-30 12:39:57'),('398772e3768b42bc9b9de92cb9529447','hr001','每日工作时间',0,'2026-06-30 03:24:19','2026-06-30 03:24:19'),('3da44d83b2ac4ba09bc9d28ec631b919','hr001','绩效制度是什么',0,'2026-06-30 03:27:51','2026-06-30 03:27:51'),('501e7c158c7b4037977f5bb43ba4b814','2c2e97aac553494f91f1a0f742bbe387','我的薪资',0,'2026-06-30 12:11:28','2026-06-30 12:11:28'),('55e65d0443b944c099669c5bf3b0745f','user123','如何申请加班？',0,'2026-06-30 13:56:15','2026-06-30 13:56:15'),('793d6b28028842ea88e0ecf544feb372','user123','上下班时间',0,'2026-06-30 13:57:45','2026-06-30 13:57:45'),('7b4f8776b92d43289881f552b88378b3','hr001','几点上班',0,'2026-06-30 02:58:08','2026-06-30 02:58:08'),('9a58fee97b304bc782e54e52137e11d8','2c2e97aac553494f91f1a0f742bbe387','年假有多少天',0,'2026-06-29 01:39:45','2026-06-29 01:44:36'),('9b121a8a530f4125bff39f8f8f3b82fe','2c2e97aac553494f91f1a0f742bbe387','你是什么模型',0,'2026-06-29 01:40:08','2026-06-29 01:44:39'),('c4a51bc685f54e318406c1c94284fa64','hr001','你可以回答我关于考勤的问题吗',0,'2026-06-30 16:33:53','2026-06-30 16:33:53'),('db62566162974004a8acceca7aa03e6f','user123','你是谁',0,'2026-06-30 13:57:15','2026-06-30 13:57:15'),('e5d0aaf71644412fa9a10e9c7128ec9c','user123','薪资多少',0,'2026-06-30 13:23:41','2026-06-30 13:23:41'),('f7d8ea9729f04dee9b2cf5eb448fe4d6','hr001','每天的上下班时间',0,'2026-06-30 03:33:29','2026-06-30 03:33:29');
/*!40000 ALTER TABLE `chat_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `correction_requests`
--

DROP TABLE IF EXISTS `correction_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `correction_requests` (
  `request_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `section` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `submitted_by` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reviewed_by` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('PENDING','APPROVED','REJECTED') COLLATE utf8mb4_unicode_ci NOT NULL,
  `review_comment` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  KEY `document_id` (`document_id`),
  KEY `submitted_by` (`submitted_by`),
  KEY `reviewed_by` (`reviewed_by`),
  CONSTRAINT `correction_requests_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`document_id`) ON DELETE CASCADE,
  CONSTRAINT `correction_requests_ibfk_2` FOREIGN KEY (`submitted_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `correction_requests_ibfk_3` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `correction_requests`
--

LOCK TABLES `correction_requests` WRITE;
/*!40000 ALTER TABLE `correction_requests` DISABLE KEYS */;
INSERT INTO `correction_requests` VALUES ('784d083fba1849ddabc44f035cd3609e','73b945e6ca349f8d','绩效制度','不好','user123','user123','REJECTED','滚','2026-06-30 14:48:36','2026-06-30 14:48:46'),('b4a7d5c1d0134e15a47a4c7750bcc0be','2a046aad5cfb4948a9cf99c31b2c4511','薪酬制度','123','user123','user123','REJECTED','123','2026-06-30 15:03:02','2026-06-30 15:03:09');
/*!40000 ALTER TABLE `correction_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departments` (
  `department_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` int DEFAULT NULL,
  PRIMARY KEY (`department_id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `departments_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `departments` (`department_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments`
--

LOCK TABLES `departments` WRITE;
/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
INSERT INTO `departments` VALUES ('dept-001','总公司',NULL,0),('dept-002','技术部','dept-001',1),('dept-003','产品部','dept-001',2),('dept-004','人力资源部','dept-001',3),('dept-005','财务部','dept-001',4),('root','总公司',NULL,0);
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `document_chunks`
--

DROP TABLE IF EXISTS `document_chunks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_chunks` (
  `chunk_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `chunk_index` int NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `token_count` int DEFAULT NULL,
  `embedding_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`chunk_id`),
  KEY `document_id` (`document_id`),
  CONSTRAINT `document_chunks_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`document_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `document_chunks`
--

LOCK TABLES `document_chunks` WRITE;
/*!40000 ALTER TABLE `document_chunks` DISABLE KEYS */;
/*!40000 ALTER TABLE `document_chunks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `document_versions`
--

DROP TABLE IF EXISTS `document_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_versions` (
  `version_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_snapshot` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `change_summary` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `changed_by` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`version_id`),
  KEY `document_id` (`document_id`),
  KEY `changed_by` (`changed_by`),
  CONSTRAINT `document_versions_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`document_id`) ON DELETE CASCADE,
  CONSTRAINT `document_versions_ibfk_2` FOREIGN KEY (`changed_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `document_versions`
--

LOCK TABLES `document_versions` WRITE;
/*!40000 ALTER TABLE `document_versions` DISABLE KEYS */;
INSERT INTO `document_versions` VALUES ('2d0e5e0c84934365a1f3443a6665bd09','2a046aad5cfb4948a9cf99c31b2c4511','1.2','薪酬管理制度\n（2026年修订版）\n\n第一章 总则\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\n第二条 适用范围：本制度适用于公司全体正式员工。实习生、临时工等特殊用工形式的薪酬管理另行规定。\n第三条 基本原则：\n（1）战略性原则：薪酬设计以公司战略为导向，与公司发展阶段和经营目标相匹配。\n（2）公平性原则：以岗位价值为基础，体现内部公平性和外部竞争力。\n（3）激励性原则：通过绩效奖金等激励性工资单元激发员工工作积极性。\n（4）合规性原则：严格遵守国家劳动法律法规，保障员工合法权益。\n（5）经济性原则：薪酬水平与公司经济效益和支付能力相适应。\n第二章 薪酬结构\n第四条 薪酬总构成：员工薪酬由基本工资、岗位工资、绩效工资、津贴补贴、奖金五部分组成。\n第五条 基本工资：根据员工的学历、工龄、技能等级等因素确定的基础性薪酬。\n（1）学历工资：大专300元/月，本科500元/月，硕士800元/月，博士1200元/月。\n（2）工龄工资：每年增加50元/月，上限500元/月。\n第六条 岗位工资：根据员工所在岗位的职责大小、技能要求、工作强度等因素确定的薪酬。岗位工资按职级分为P1—P10共十个级别。\n第七条 绩效工资：根据员工月度/年度绩效考核结果核发的浮动薪酬。一般员工绩效工资占比为总薪酬的20%—30%，管理层占比为30%—50%。\n第八条 津贴补贴：\n（1）通讯补贴：普通员工100元/月，主管级200元/月，经理级300元/月。\n（2）交通补贴：300元/月（统一标准）。\n（3）餐补：20元/工作日出勤日。\n（4）高温补贴：每年6—9月，按国家规定标准发放。\n（5）项目现场津贴：外派项目现场人员，按项目地标准给予补贴。\n第九条 奖金：\n（1）年终奖金：根据公司年度经营效益和个人年度绩效考核结果发放，一般为1-3个月工资。\n（2）项目奖金：项目完成并产生效益后，按税后利润的3%—5%提取，根据参与人员的贡献度发放。\n（3）专项奖金：对在技术创新、降本增效、市场开拓等方面有突出贡献的员工设立的特别奖励。\n第三章 薪酬定级与调整\n第十条 新员工定薪：新员工入职时，根据其学历、工作经验、岗位要求和市场薪酬水平，由用人部门与人力资源部共同确定初始薪酬等级。\n第十一条 薪酬调整类型：\n（1）年度普调：公司每年根据市场薪酬水平、CPI变动和公司经营状况进行薪酬整体调整。\n（2）绩效调薪：根据年度绩效考核结果进行个人薪酬调整。考核为\"优秀\"者可晋升一档，连续两年\"优秀\"者可晋升一级。\n（3）岗位变动调薪：员工岗位发生变动（晋升、降级、平调）时，薪酬相应调整。晋升的从批准次月起执行新薪酬，降级的从批准当月起执行。\n（4）特殊调薪：对紧缺人才、特殊贡献者可进行特殊调薪，须经总经理审批。\n第四章 薪资核算与发放\n第十二条 薪资计算周期：每月1日至月末最后一天为一个薪酬计算周期。\n第十三条 薪资发放日期：每月10日发放上月薪资。若遇休息日或法定假日，提前至最近工作日发放。\n第十四条 日工资计算：日工资=月基本工资÷21.75天（国家规定的月平均计薪天数）。\n第十五条 新入职/离职员工薪资计算：\n（1）新入职员工：当月薪酬=月基本工资÷21.75×当月实际出勤天数。\n（2）离职员工：薪酬结算至最后工作日，于最近薪资发放日统一支付。\n第十六条 薪资扣除项：根据国家法规，公司依法代扣代缴个人所得税、社会保险及住房公积金个人缴纳部分。\n第十七条 薪资保密：公司实行薪酬保密制度。员工不得泄露本人薪资，不得打听他人薪资，违者将视情节给予纪律处分。\n第五章 特殊情况薪酬管理\n第十八条 试用期薪酬：试用期员工薪酬为转正后薪酬的80%，试用期不超过6个月。\n第十九条 病假薪酬：因病请假，按以下标准计发：\n（1）病假1天以内：不扣工资。\n（2）病假2天以上、1个月以内：按本人工资的80%计发。\n（3）病假超过1个月：按当地最低工资标准的80%计发。\n第二十条 事假薪酬：事假按实际出勤天数计发工资，事假期间不享受绩效工资。\n第二十一条 待岗薪酬：公司因经营需要安排员工待岗的，第一个月按正常工资发放，第二个月起按当地最低工资标准发放生活费。\n第六章 附则\n第二十二条 本制度由人力资源部负责解释和修订。\n第二十三条 本制度自发布之日起施行，原有薪酬相关规定同时废止。','文件替换: 薪酬制度.docx','user123','2026-06-30 14:32:22'),('557cb10e641e46a787cbc0f46661170a','2a046aad5cfb4948a9cf99c31b2c4511','1.1','薪酬管理制度\n（2026年修订版）\n\n第一章 总则\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\n第二条 适用范围：本制度适用于公司全体正式员工。实习生、临时工等特殊用工形式的薪酬管理另行规定。\n第三条 基本原则：\n（1）战略性原则：薪酬设计以公司战略为导向，与公司发展阶段和经营目标相匹配。\n（2）公平性原则：以岗位价值为基础，体现内部公平性和外部竞争力。\n（3）激励性原则：通过绩效奖金等激励性工资单元激发员工工作积极性。\n（4）合规性原则：严格遵守国家劳动法律法规，保障员工合法权益。\n（5）经济性原则：薪酬水平与公司经济效益和支付能力相适应。\n第二章 薪酬结构\n第四条 薪酬总构成：员工薪酬由基本工资、岗位工资、绩效工资、津贴补贴、奖金五部分组成。\n第五条 基本工资：根据员工的学历、工龄、技能等级等因素确定的基础性薪酬。\n（1）学历工资：大专300元/月，本科500元/月，硕士800元/月，博士1200元/月。\n（2）工龄工资：每年增加50元/月，上限500元/月。\n第六条 岗位工资：根据员工所在岗位的职责大小、技能要求、工作强度等因素确定的薪酬。岗位工资按职级分为P1—P10共十个级别。\n第七条 绩效工资：根据员工月度/年度绩效考核结果核发的浮动薪酬。一般员工绩效工资占比为总薪酬的20%—30%，管理层占比为30%—50%。\n第八条 津贴补贴：\n（1）通讯补贴：普通员工100元/月，主管级200元/月，经理级300元/月。\n（2）交通补贴：300元/月（统一标准）。\n（3）餐补：20元/工作日出勤日。\n（4）高温补贴：每年6—9月，按国家规定标准发放。\n（5）项目现场津贴：外派项目现场人员，按项目地标准给予补贴。\n第九条 奖金：\n（1）年终奖金：根据公司年度经营效益和个人年度绩效考核结果发放，一般为1-3个月工资。\n（2）项目奖金：项目完成并产生效益后，按税后利润的3%—5%提取，根据参与人员的贡献度发放。\n（3）专项奖金：对在技术创新、降本增效、市场开拓等方面有突出贡献的员工设立的特别奖励。\n第三章 薪酬定级与调整\n第十条 新员工定薪：新员工入职时，根据其学历、工作经验、岗位要求和市场薪酬水平，由用人部门与人力资源部共同确定初始薪酬等级。\n第十一条 薪酬调整类型：\n（1）年度普调：公司每年根据市场薪酬水平、CPI变动和公司经营状况进行薪酬整体调整。\n（2）绩效调薪：根据年度绩效考核结果进行个人薪酬调整。考核为\"优秀\"者可晋升一档，连续两年\"优秀\"者可晋升一级。\n（3）岗位变动调薪：员工岗位发生变动（晋升、降级、平调）时，薪酬相应调整。晋升的从批准次月起执行新薪酬，降级的从批准当月起执行。\n（4）特殊调薪：对紧缺人才、特殊贡献者可进行特殊调薪，须经总经理审批。\n第四章 薪资核算与发放\n第十二条 薪资计算周期：每月1日至月末最后一天为一个薪酬计算周期。\n第十三条 薪资发放日期：每月10日发放上月薪资。若遇休息日或法定假日，提前至最近工作日发放。\n第十四条 日工资计算：日工资=月基本工资÷21.75天（国家规定的月平均计薪天数）。\n第十五条 新入职/离职员工薪资计算：\n（1）新入职员工：当月薪酬=月基本工资÷21.75×当月实际出勤天数。\n（2）离职员工：薪酬结算至最后工作日，于最近薪资发放日统一支付。\n第十六条 薪资扣除项：根据国家法规，公司依法代扣代缴个人所得税、社会保险及住房公积金个人缴纳部分。\n第十七条 薪资保密：公司实行薪酬保密制度。员工不得泄露本人薪资，不得打听他人薪资，违者将视情节给予纪律处分。\n第五章 特殊情况薪酬管理\n第十八条 试用期薪酬：试用期员工薪酬为转正后薪酬的80%，试用期不超过6个月。\n第十九条 病假薪酬：因病请假，按以下标准计发：\n（1）病假1天以内：不扣工资。\n（2）病假2天以上、1个月以内：按本人工资的80%计发。\n（3）病假超过1个月：按当地最低工资标准的80%计发。\n第二十条 事假薪酬：事假按实际出勤天数计发工资，事假期间不享受绩效工资。\n第二十一条 待岗薪酬：公司因经营需要安排员工待岗的，第一个月按正常工资发放，第二个月起按当地最低工资标准发放生活费。\n第六章 附则\n第二十二条 本制度由人力资源部负责解释和修订。\n第二十三条 本制度自发布之日起施行，原有薪酬相关规定同时废止。','文件替换: 薪酬制度.docx','user123','2026-06-30 13:43:09'),('6e750ed2cc51498d9dc38a93e3c79555','7ab9fe6efcb24b4e9d9c77a9c5a1f027','1.3','**考勤管理制度**\n\n（2026年修订版）\n\n# 第一章 总则\n\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情况，特制定本制度。\n\n第二条 适用范围：本制度适用于公司全体正式聘用员工。实习生、兼职人员及劳务派遣人员参照本制度执行或另行约定。\n\n第三条 基本原则：坚持公平、公正、公开原则，实行标准化、数字化的考勤管理机制。\n\n# 第二章 工作时间\n\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\n\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。\n\n第六条 弹性工作制：经部门负责人批准，部分岗位可实行弹性工作制，核心工作时间为10:00—16:00，其余时间可在规定范围内自主安排。\n\n第七条 特殊工时制：因业务需要实行综合计算工时制或不定时工作制的岗位，须经人力资源部审核并报劳动行政部门批准后执行。\n\n# 第三章 考勤方式\n\n第八条 考勤工具：公司采用电子考勤系统（人脸识别/指纹/打卡），员工须在规定时间内完成签到、签退。\n\n第九条 签到签退：每个工作日须签到一次、签退一次。上午9:00前完成签到，下午18:00后完成签退。未按时签到签退的，视为迟到或早退。\n\n第十条 外出登记：工作时间内因公外出，须提前在OA系统或纸质《外出登记表》中登记，经直属上级审批后方可外出。\n\n第十一条 出差管理：员工出差须提前填写《出差申请单》，经部门负责人审批后报人力资源部备案。出差期间考勤以出差单为准。\n\n第十二条 外勤/现场人员：因工作性质无法正常考勤的，由部门负责人每月出具考勤确认单，报人力资源部审核备案。\n\n# 第四章 迟到、早退与旷工\n\n第十三条 迟到：超过规定上班时间30分钟以内到岗的，视为迟到。\n\n（1）月累计迟到1-2次：口头提醒。\n\n（2）月累计迟到3-5次：每次扣款30元，并予以书面警告。\n\n（3）月累计迟到6次及以上：视为严重违纪，扣发当月全勤奖，纳入绩效考核负面记录。\n\n第十四条 早退：未经批准在下班时间前擅自离岗的，视为早退。早退处理标准与迟到相同。\n\n第十五条 旷工：以下情形视为旷工：\n\n（1）未履行请假手续或请假未获批准而擅自缺勤的。\n\n（2）迟到或早退超过30分钟以上且未说明合理理由的，按旷工半天处理。\n\n（3）假期届满未经续假或续假未获批准而未到岗的。\n\n第十六条 旷工处理：\n\n（1）旷工半天：扣除当日工资及当月全勤奖。\n\n（2）旷工1天：扣除当日工资、当月全勤奖，并予以书面警告。\n\n（3）连续旷工3天（含）以上或月累计旷工5天（含）以上：属于严重违反公司规章制度，公司有权单方解除劳动合同，不予经济补偿。\n\n# 第五章 加班管理\n\n第十七条 加班定义：因工作需要，经审批后在正常工作时间以外延长工作时间的，视为加班。\n\n第十八条 加班申请：加班须提前填写《加班申请单》，经部门负责人审批后报人力资源部备案。未经审批的不视为加班。\n\n第十九条 加班时限：依据《劳动法》规定，每月加班不得超过36小时。确需超时须经总经理审批。\n\n第二十条 加班补偿：\n\n（1）工作日延长工作时间：按不低于本人小时工资的150%支付加班工资。\n\n（2）休息日安排工作且不能补休的：按不低于本人日工资的200%支付加班工资。\n\n（3）法定节假日安排工作的：按不低于本人日工资的300%支付加班工资。\n\n（4）经理级及以上管理人员实行不定时工作制，不计算加班工资，可申请调休。\n\n第二十一条 调休：休息日加班的，应优先安排调休。调休须在加班发生后1个月内完成，逾期作废。\n\n# 第六章 全勤奖\n\n第二十二条 全勤奖标准：当月无迟到、早退、旷工、请假（年假除外）记录的员工，享受全勤奖200元/月。\n\n第二十三条 取消条件：当月有迟到/早退记录、病假/事假记录、旷工记录的，取消当月全勤奖。法定假期（年假、婚假、产假、丧假等）不影响全勤奖。\n\n# 第七章 考勤数据管理\n\n第二十四条 考勤统计：每月5日前，人力资源部完成上月考勤数据统计汇总，经公示无异议后作为薪资核算依据。\n\n第二十五条 考勤异议：员工对考勤结果有异议的，须在公示后3个工作日内向人力资源部提出书面申诉，逾期不予受理。\n\n第二十六条 考勤档案：考勤原始记录至少保存2年备查，考勤汇总表长期保存。\n\n# 第八章 附则\n\n第二十七条 本制度由人力资源部负责解释和修订。\n\n第二十八条 本制度与国家法律法规不一致的，以国家法律法规为准。\n\n第二十九条 本制度自发布之日起施行，原有考勤相关规定同时废止。','文件替换: 考勤制度.docx','user123','2026-06-30 14:39:40'),('7051d7ab20514967973f572794ad4663','7ab9fe6efcb24b4e9d9c77a9c5a1f027','1.2','考勤管理制度\n（2026年修订版）\n\n第一章 总则\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情况，特制定本制度。\n第二条 适用范围：本制度适用于公司全体正式聘用员工。实习生、兼职人员及劳务派遣人员参照本制度执行或另行约定。\n第三条 基本原则：坚持公平、公正、公开原则，实行标准化、数字化的考勤管理机制。\n第二章 工作时间\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。\n第六条 弹性工作制：经部门负责人批准，部分岗位可实行弹性工作制，核心工作时间为10:00—16:00，其余时间可在规定范围内自主安排。\n第七条 特殊工时制：因业务需要实行综合计算工时制或不定时工作制的岗位，须经人力资源部审核并报劳动行政部门批准后执行。\n第三章 考勤方式\n第八条 考勤工具：公司采用电子考勤系统（人脸识别/指纹/打卡），员工须在规定时间内完成签到、签退。\n第九条 签到签退：每个工作日须签到一次、签退一次。上午9:00前完成签到，下午18:00后完成签退。未按时签到签退的，视为迟到或早退。\n第十条 外出登记：工作时间内因公外出，须提前在OA系统或纸质《外出登记表》中登记，经直属上级审批后方可外出。\n第十一条 出差管理：员工出差须提前填写《出差申请单》，经部门负责人审批后报人力资源部备案。出差期间考勤以出差单为准。\n第十二条 外勤/现场人员：因工作性质无法正常考勤的，由部门负责人每月出具考勤确认单，报人力资源部审核备案。\n第四章 迟到、早退与旷工\n第十三条 迟到：超过规定上班时间30分钟以内到岗的，视为迟到。\n（1）月累计迟到1-2次：口头提醒。\n（2）月累计迟到3-5次：每次扣款30元，并予以书面警告。\n（3）月累计迟到6次及以上：视为严重违纪，扣发当月全勤奖，纳入绩效考核负面记录。\n第十四条 早退：未经批准在下班时间前擅自离岗的，视为早退。早退处理标准与迟到相同。\n第十五条 旷工：以下情形视为旷工：\n（1）未履行请假手续或请假未获批准而擅自缺勤的。\n（2）迟到或早退超过30分钟以上且未说明合理理由的，按旷工半天处理。\n（3）假期届满未经续假或续假未获批准而未到岗的。\n第十六条 旷工处理：\n（1）旷工半天：扣除当日工资及当月全勤奖。\n（2）旷工1天：扣除当日工资、当月全勤奖，并予以书面警告。\n（3）连续旷工3天（含）以上或月累计旷工5天（含）以上：属于严重违反公司规章制度，公司有权单方解除劳动合同，不予经济补偿。\n第五章 加班管理\n第十七条 加班定义：因工作需要，经审批后在正常工作时间以外延长工作时间的，视为加班。\n第十八条 加班申请：加班须提前填写《加班申请单》，经部门负责人审批后报人力资源部备案。未经审批的不视为加班。\n第十九条 加班时限：依据《劳动法》规定，每月加班不得超过36小时。确需超时须经总经理审批。\n第二十条 加班补偿：\n（1）工作日延长工作时间：按不低于本人小时工资的150%支付加班工资。\n（2）休息日安排工作且不能补休的：按不低于本人日工资的200%支付加班工资。\n（3）法定节假日安排工作的：按不低于本人日工资的300%支付加班工资。\n（4）经理级及以上管理人员实行不定时工作制，不计算加班工资，可申请调休。\n第二十一条 调休：休息日加班的，应优先安排调休。调休须在加班发生后1个月内完成，逾期作废。\n第六章 全勤奖\n第二十二条 全勤奖标准：当月无迟到、早退、旷工、请假（年假除外）记录的员工，享受全勤奖200元/月。\n第二十三条 取消条件：当月有迟到/早退记录、病假/事假记录、旷工记录的，取消当月全勤奖。法定假期（年假、婚假、产假、丧假等）不影响全勤奖。\n第七章 考勤数据管理\n第二十四条 考勤统计：每月5日前，人力资源部完成上月考勤数据统计汇总，经公示无异议后作为薪资核算依据。\n第二十五条 考勤异议：员工对考勤结果有异议的，须在公示后3个工作日内向人力资源部提出书面申诉，逾期不予受理。\n第二十六条 考勤档案：考勤原始记录至少保存2年备查，考勤汇总表长期保存。\n第八章 附则\n第二十七条 本制度由人力资源部负责解释和修订。\n第二十八条 本制度与国家法律法规不一致的，以国家法律法规为准。\n第二十九条 本制度自发布之日起施行，原有考勤相关规定同时废止。','文件替换: 考勤制度.docx','user123','2026-06-30 13:42:36'),('78310bd511cb4ee9b97fd91314b790a9','7ab9fe6efcb24b4e9d9c77a9c5a1f027','1.1','考勤管理制度\n（2026年修订版）\n\n第一章 总则\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情况，特制定本制度。\n第二条 适用范围：本制度适用于公司全体正式聘用员工。实习生、兼职人员及劳务派遣人员参照本制度执行或另行约定。\n第三条 基本原则：坚持公平、公正、公开原则，实行标准化、数字化的考勤管理机制。\n第二章 工作时间\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。\n第六条 弹性工作制：经部门负责人批准，部分岗位可实行弹性工作制，核心工作时间为10:00—16:00，其余时间可在规定范围内自主安排。\n第七条 特殊工时制：因业务需要实行综合计算工时制或不定时工作制的岗位，须经人力资源部审核并报劳动行政部门批准后执行。\n第三章 考勤方式\n第八条 考勤工具：公司采用电子考勤系统（人脸识别/指纹/打卡），员工须在规定时间内完成签到、签退。\n第九条 签到签退：每个工作日须签到一次、签退一次。上午9:00前完成签到，下午18:00后完成签退。未按时签到签退的，视为迟到或早退。\n第十条 外出登记：工作时间内因公外出，须提前在OA系统或纸质《外出登记表》中登记，经直属上级审批后方可外出。\n第十一条 出差管理：员工出差须提前填写《出差申请单》，经部门负责人审批后报人力资源部备案。出差期间考勤以出差单为准。\n第十二条 外勤/现场人员：因工作性质无法正常考勤的，由部门负责人每月出具考勤确认单，报人力资源部审核备案。\n第四章 迟到、早退与旷工\n第十三条 迟到：超过规定上班时间30分钟以内到岗的，视为迟到。\n（1）月累计迟到1-2次：口头提醒。\n（2）月累计迟到3-5次：每次扣款30元，并予以书面警告。\n（3）月累计迟到6次及以上：视为严重违纪，扣发当月全勤奖，纳入绩效考核负面记录。\n第十四条 早退：未经批准在下班时间前擅自离岗的，视为早退。早退处理标准与迟到相同。\n第十五条 旷工：以下情形视为旷工：\n（1）未履行请假手续或请假未获批准而擅自缺勤的。\n（2）迟到或早退超过30分钟以上且未说明合理理由的，按旷工半天处理。\n（3）假期届满未经续假或续假未获批准而未到岗的。\n第十六条 旷工处理：\n（1）旷工半天：扣除当日工资及当月全勤奖。\n（2）旷工1天：扣除当日工资、当月全勤奖，并予以书面警告。\n（3）连续旷工3天（含）以上或月累计旷工5天（含）以上：属于严重违反公司规章制度，公司有权单方解除劳动合同，不予经济补偿。\n第五章 加班管理\n第十七条 加班定义：因工作需要，经审批后在正常工作时间以外延长工作时间的，视为加班。\n第十八条 加班申请：加班须提前填写《加班申请单》，经部门负责人审批后报人力资源部备案。未经审批的不视为加班。\n第十九条 加班时限：依据《劳动法》规定，每月加班不得超过36小时。确需超时须经总经理审批。\n第二十条 加班补偿：\n（1）工作日延长工作时间：按不低于本人小时工资的150%支付加班工资。\n（2）休息日安排工作且不能补休的：按不低于本人日工资的200%支付加班工资。\n（3）法定节假日安排工作的：按不低于本人日工资的300%支付加班工资。\n（4）经理级及以上管理人员实行不定时工作制，不计算加班工资，可申请调休。\n第二十一条 调休：休息日加班的，应优先安排调休。调休须在加班发生后1个月内完成，逾期作废。\n第六章 全勤奖\n第二十二条 全勤奖标准：当月无迟到、早退、旷工、请假（年假除外）记录的员工，享受全勤奖200元/月。\n第二十三条 取消条件：当月有迟到/早退记录、病假/事假记录、旷工记录的，取消当月全勤奖。法定假期（年假、婚假、产假、丧假等）不影响全勤奖。\n第七章 考勤数据管理\n第二十四条 考勤统计：每月5日前，人力资源部完成上月考勤数据统计汇总，经公示无异议后作为薪资核算依据。\n第二十五条 考勤异议：员工对考勤结果有异议的，须在公示后3个工作日内向人力资源部提出书面申诉，逾期不予受理。\n第二十六条 考勤档案：考勤原始记录至少保存2年备查，考勤汇总表长期保存。\n第八章 附则\n第二十七条 本制度由人力资源部负责解释和修订。\n第二十八条 本制度与国家法律法规不一致的，以国家法律法规为准。\n第二十九条 本制度自发布之日起施行，原有考勤相关规定同时废止。','文件替换: 考勤制度.docx','hr001','2026-06-30 03:16:26'),('cfd5a2d886494048bf10823dbe2864fa','7ab9fe6efcb24b4e9d9c77a9c5a1f027','1.0','考勤管理制度\n（2026年修订版）\n\n第一章 总则\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情况，特制定本制度。\n第二条 适用范围：本制度适用于公司全体正式聘用员工。实习生、兼职人员及劳务派遣人员参照本制度执行或另行约定。\n第三条 基本原则：坚持公平、公正、公开原则，实行标准化、数字化的考勤管理机制。\n第二章 工作时间\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。\n第六条 弹性工作制：经部门负责人批准，部分岗位可实行弹性工作制，核心工作时间为10:00—16:00，其余时间可在规定范围内自主安排。\n第七条 特殊工时制：因业务需要实行综合计算工时制或不定时工作制的岗位，须经人力资源部审核并报劳动行政部门批准后执行。\n第三章 考勤方式\n第八条 考勤工具：公司采用电子考勤系统（人脸识别/指纹/打卡），员工须在规定时间内完成签到、签退。\n第九条 签到签退：每个工作日须签到一次、签退一次。上午9:00前完成签到，下午18:00后完成签退。未按时签到签退的，视为迟到或早退。\n第十条 外出登记：工作时间内因公外出，须提前在OA系统或纸质《外出登记表》中登记，经直属上级审批后方可外出。\n第十一条 出差管理：员工出差须提前填写《出差申请单》，经部门负责人审批后报人力资源部备案。出差期间考勤以出差单为准。\n第十二条 外勤/现场人员：因工作性质无法正常考勤的，由部门负责人每月出具考勤确认单，报人力资源部审核备案。\n第四章 迟到、早退与旷工\n第十三条 迟到：超过规定上班时间30分钟以内到岗的，视为迟到。\n（1）月累计迟到1-2次：口头提醒。\n（2）月累计迟到3-5次：每次扣款30元，并予以书面警告。\n（3）月累计迟到6次及以上：视为严重违纪，扣发当月全勤奖，纳入绩效考核负面记录。\n第十四条 早退：未经批准在下班时间前擅自离岗的，视为早退。早退处理标准与迟到相同。\n第十五条 旷工：以下情形视为旷工：\n（1）未履行请假手续或请假未获批准而擅自缺勤的。\n（2）迟到或早退超过30分钟以上且未说明合理理由的，按旷工半天处理。\n（3）假期届满未经续假或续假未获批准而未到岗的。\n第十六条 旷工处理：\n（1）旷工半天：扣除当日工资及当月全勤奖。\n（2）旷工1天：扣除当日工资、当月全勤奖，并予以书面警告。\n（3）连续旷工3天（含）以上或月累计旷工5天（含）以上：属于严重违反公司规章制度，公司有权单方解除劳动合同，不予经济补偿。\n第五章 加班管理\n第十七条 加班定义：因工作需要，经审批后在正常工作时间以外延长工作时间的，视为加班。\n第十八条 加班申请：加班须提前填写《加班申请单》，经部门负责人审批后报人力资源部备案。未经审批的不视为加班。\n第十九条 加班时限：依据《劳动法》规定，每月加班不得超过36小时。确需超时须经总经理审批。\n第二十条 加班补偿：\n（1）工作日延长工作时间：按不低于本人小时工资的150%支付加班工资。\n（2）休息日安排工作且不能补休的：按不低于本人日工资的200%支付加班工资。\n（3）法定节假日安排工作的：按不低于本人日工资的300%支付加班工资。\n（4）经理级及以上管理人员实行不定时工作制，不计算加班工资，可申请调休。\n第二十一条 调休：休息日加班的，应优先安排调休。调休须在加班发生后1个月内完成，逾期作废。\n第六章 全勤奖\n第二十二条 全勤奖标准：当月无迟到、早退、旷工、请假（年假除外）记录的员工，享受全勤奖200元/月。\n第二十三条 取消条件：当月有迟到/早退记录、病假/事假记录、旷工记录的，取消当月全勤奖。法定假期（年假、婚假、产假、丧假等）不影响全勤奖。\n第七章 考勤数据管理\n第二十四条 考勤统计：每月5日前，人力资源部完成上月考勤数据统计汇总，经公示无异议后作为薪资核算依据。\n第二十五条 考勤异议：员工对考勤结果有异议的，须在公示后3个工作日内向人力资源部提出书面申诉，逾期不予受理。\n第二十六条 考勤档案：考勤原始记录至少保存2年备查，考勤汇总表长期保存。\n第八章 附则\n第二十七条 本制度由人力资源部负责解释和修订。\n第二十八条 本制度与国家法律法规不一致的，以国家法律法规为准。\n第二十九条 本制度自发布之日起施行，原有考勤相关规定同时废止。','V1.0','hr001','2026-06-30 02:57:13'),('d56cd454627a4f9d9ff7fc77f1d8966f','2a046aad5cfb4948a9cf99c31b2c4511','1.0','薪酬管理制度\n（2026年修订版）\n\n第一章 总则\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\n第二条 适用范围：本制度适用于公司全体正式员工。实习生、临时工等特殊用工形式的薪酬管理另行规定。\n第三条 基本原则：\n（1）战略性原则：薪酬设计以公司战略为导向，与公司发展阶段和经营目标相匹配。\n（2）公平性原则：以岗位价值为基础，体现内部公平性和外部竞争力。\n（3）激励性原则：通过绩效奖金等激励性工资单元激发员工工作积极性。\n（4）合规性原则：严格遵守国家劳动法律法规，保障员工合法权益。\n（5）经济性原则：薪酬水平与公司经济效益和支付能力相适应。\n第二章 薪酬结构\n第四条 薪酬总构成：员工薪酬由基本工资、岗位工资、绩效工资、津贴补贴、奖金五部分组成。\n第五条 基本工资：根据员工的学历、工龄、技能等级等因素确定的基础性薪酬。\n（1）学历工资：大专300元/月，本科500元/月，硕士800元/月，博士1200元/月。\n（2）工龄工资：每年增加50元/月，上限500元/月。\n第六条 岗位工资：根据员工所在岗位的职责大小、技能要求、工作强度等因素确定的薪酬。岗位工资按职级分为P1—P10共十个级别。\n第七条 绩效工资：根据员工月度/年度绩效考核结果核发的浮动薪酬。一般员工绩效工资占比为总薪酬的20%—30%，管理层占比为30%—50%。\n第八条 津贴补贴：\n（1）通讯补贴：普通员工100元/月，主管级200元/月，经理级300元/月。\n（2）交通补贴：300元/月（统一标准）。\n（3）餐补：20元/工作日出勤日。\n（4）高温补贴：每年6—9月，按国家规定标准发放。\n（5）项目现场津贴：外派项目现场人员，按项目地标准给予补贴。\n第九条 奖金：\n（1）年终奖金：根据公司年度经营效益和个人年度绩效考核结果发放，一般为1-3个月工资。\n（2）项目奖金：项目完成并产生效益后，按税后利润的3%—5%提取，根据参与人员的贡献度发放。\n（3）专项奖金：对在技术创新、降本增效、市场开拓等方面有突出贡献的员工设立的特别奖励。\n第三章 薪酬定级与调整\n第十条 新员工定薪：新员工入职时，根据其学历、工作经验、岗位要求和市场薪酬水平，由用人部门与人力资源部共同确定初始薪酬等级。\n第十一条 薪酬调整类型：\n（1）年度普调：公司每年根据市场薪酬水平、CPI变动和公司经营状况进行薪酬整体调整。\n（2）绩效调薪：根据年度绩效考核结果进行个人薪酬调整。考核为\"优秀\"者可晋升一档，连续两年\"优秀\"者可晋升一级。\n（3）岗位变动调薪：员工岗位发生变动（晋升、降级、平调）时，薪酬相应调整。晋升的从批准次月起执行新薪酬，降级的从批准当月起执行。\n（4）特殊调薪：对紧缺人才、特殊贡献者可进行特殊调薪，须经总经理审批。\n第四章 薪资核算与发放\n第十二条 薪资计算周期：每月1日至月末最后一天为一个薪酬计算周期。\n第十三条 薪资发放日期：每月10日发放上月薪资。若遇休息日或法定假日，提前至最近工作日发放。\n第十四条 日工资计算：日工资=月基本工资÷21.75天（国家规定的月平均计薪天数）。\n第十五条 新入职/离职员工薪资计算：\n（1）新入职员工：当月薪酬=月基本工资÷21.75×当月实际出勤天数。\n（2）离职员工：薪酬结算至最后工作日，于最近薪资发放日统一支付。\n第十六条 薪资扣除项：根据国家法规，公司依法代扣代缴个人所得税、社会保险及住房公积金个人缴纳部分。\n第十七条 薪资保密：公司实行薪酬保密制度。员工不得泄露本人薪资，不得打听他人薪资，违者将视情节给予纪律处分。\n第五章 特殊情况薪酬管理\n第十八条 试用期薪酬：试用期员工薪酬为转正后薪酬的80%，试用期不超过6个月。\n第十九条 病假薪酬：因病请假，按以下标准计发：\n（1）病假1天以内：不扣工资。\n（2）病假2天以上、1个月以内：按本人工资的80%计发。\n（3）病假超过1个月：按当地最低工资标准的80%计发。\n第二十条 事假薪酬：事假按实际出勤天数计发工资，事假期间不享受绩效工资。\n第二十一条 待岗薪酬：公司因经营需要安排员工待岗的，第一个月按正常工资发放，第二个月起按当地最低工资标准发放生活费。\n第六章 附则\n第二十二条 本制度由人力资源部负责解释和修订。\n第二十三条 本制度自发布之日起施行，原有薪酬相关规定同时废止。','V1.0','hr001','2026-06-30 03:29:23'),('e555211bdca64c3eb911b6d4e6704f17','87d0b8363a47c8ca','1.0','**员工福利管理制度**\n\n（2026年修订版）\n\n# 第一章 总则\n\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\n\n第二条 适用范围：本制度适用于公司全体正式员工。试用期员工和特殊劳动关系人员适用相应条款。\n\n第三条 福利原则：\n\n（1）合法性原则：各项福利须符合国家及地方相关法律法规。\n\n（2）普惠性原则：保障全体员工享有基本福利权益。\n\n（3）激励性原则：部分福利与员工贡献、绩效相挂钩。\n\n（4）可持续原则：福利支出控制在公司人力成本预算范围内。\n\n# 第二章 法定社会保险与公积金\n\n第四条 五险一金：公司依法为转正员工缴纳养老保险、医疗保险、工伤保险、失业保险、生育保险（现已并入医疗保险）及住房公积金。\n\n第五条 缴费基数与比例：社保缴费基数根据员工上年度月平均工资（在社平工资60%—300%之间）确定，缴费比例按国家及地方政府最新规定执行。\n\n第六条 公积金缴纳：住房公积金公司及个人缴存比例均为当地规定标准的最高档（一般为5%—12%）。\n\n# 第三章 补充商业保险\n\n第七条 补充医疗保险：公司为全体员工购买补充医疗保险，用于报销基本医保目录外的合理医疗费用，年度报销上限为2万元/人。\n\n第八条 意外伤害保险：公司为全体员工购买意外伤害保险，保额为20万元/人。对长期外派、项目现场员工，保额提升至50万元/人。\n\n第九条 重大疾病保险：工作满2年的员工，公司为其购买重大疾病保险，保额10万元。\n\n# 第四章 带薪假期福利\n\n第十条 法定节假日：员工享有国家规定的全部法定节假日（元旦、春节、清明节、劳动节、端午节、中秋节、国庆节等），共计11天/年。\n\n第十一条 年休假：员工累计工作满1年不满10年的，年休假5天；满10年不满20年的，年休假10天；满20年的，年休假15天。\n\n第十二条 婚假：员工依法办理结婚登记的，享受婚假3天。符合晚婚条件的，额外增加晚婚假，按当地规定执行。\n\n第十三条 产假/陪产假：女职工生育享受不少于98天产假，难产或多胞胎生育的，按国家规定增加。男职工享受陪产假15天。\n\n第十四条 丧假：员工直系亲属（父母、配偶、子女）去世的，给予丧假3天。\n\n第十五条 病假：员工因病需治疗休养的，凭医院证明申请病假，公司给予每年5天全薪病假，超出部分按薪酬制度执行。\n\n# 第五章 健康关怀\n\n第十六条 年度健康体检：公司每年组织一次员工健康体检，体检项目包括常规项目及专项筛查。体检费用由公司承担，标准为：普通员工800元/人，40岁以上员工1200元/人。\n\n第十七条 心理健康关怀：公司提供员工心理援助计划（EAP），包括心理咨询热线、心理健康讲座等，费用由公司承担。\n\n第十八条 员工健身房/运动补贴：公司在办公区域设立健身房，或为员工提供运动健身补贴300元/月。\n\n# 第六章 生活福利\n\n第十九条 节日福利：春节、端午节、中秋节等传统节日，公司发放节日礼金或礼品，标准为300—500元/人。\n\n第二十条 生日福利：员工生日当月发放生日礼金200元或等值礼物。\n\n第二十一条 结婚礼金：员工结婚，公司赠送礼金1000元。\n\n第二十二条 生育礼金：员工生育子女，公司赠送礼金800元。\n\n第二十三条 抚恤金：员工直系亲属去世，公司发放慰问金500元。\n\n# 第七章 住房与交通福利\n\n第二十四条 住房补贴：公司为未享受公司宿舍的员工提供住房补贴，标准根据职级确定：普通员工500元/月，主管级800元/月，经理级1500元/月。\n\n第二十五条 员工宿舍：公司为外地员工提供员工宿舍，标准间配置，个人承担水电费。\n\n第二十六条 通勤班车：公司在主要居住区提供通勤班车服务。未覆盖区域提供交通补贴。\n\n# 第八章 培训与发展福利\n\n第二十七条 培训经费：公司每年按员工工资总额的2%提取培训经费。\n\n第二十八条 学历提升资助：员工在职攻读与工作岗位相关的学历、学位，取得证书后，公司给予1000—5000元一次性奖励。\n\n第二十九条 职业资格补贴：员工考取与岗位相关的国家职业资格证书，公司给予一次性奖励500—2000元，并按月发放资格补贴100—500元。\n\n# 第九章 附则\n\n第三十条 本制度由人力资源部负责解释和修订。\n\n第三十一条 本制度自发布之日起施行，原有福利相关规定同时废止。','自动导入','user-admin-001',NULL),('ff8b59d9b8fd4eaca1f6ec7d1490a122','73b945e6ca349f8d','1.0','**绩效考核管理制度**\n\n（2026年修订版）\n\n# 第一章 总则\n\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，特制定本制度。\n\n第二条 适用范围：本制度适用于公司全体正式员工。试用期员工、实习生的考核办法另行规定。\n\n第三条 考核原则：\n\n（1）结果导向原则：以工作成果和业绩为考核核心。\n\n（2）客观公正原则：以事实和数据为依据，避免主观偏见。\n\n（3）公开透明原则：考核标准、程序和结果及时公开，接受监督。\n\n（4）持续改进原则：通过考核发现问题、促进改进，而非单纯惩罚。\n\n（5）分层分类原则：不同层级、不同岗位类别采用差异化的考核方式。\n\n# 第二章 考核周期与内容\n\n第四条 考核周期：\n\n（1）月度考核：每月进行一次，针对当月工作目标完成情况进行评价。\n\n（2）季度考核：每季度进行一次综合评估，关注阶段性目标达成情况。\n\n（3）年度考核：每年12月进行全年综合考核，作为年终奖、晋升、调薪的主要依据。\n\n第五条 考核维度：绩效考核主要从以下三个维度进行评价：\n\n（1）工作业绩（权重70%）：主要考核KPI指标完成情况、工作质量、工作效率、目标达成度等。\n\n（2）工作能力（权重20%）：主要考核专业技能、问题解决能力、学习创新能力、沟通协作能力等。\n\n（3）工作态度（权重10%）：主要考核责任心、积极性、团队合作精神、纪律性等。\n\n# 第三章 考核指标体系\n\n第六条 KPI设定：各级管理者与下属在考核周期初共同制定关键绩效指标（KPI），KPI须符合SMART原则（具体、可量化、可实现、相关性、时限性）。\n\n第七条 普通员工KPI指标：\n\n（1）工作任务完成率：考核周期内计划任务的完成比例。\n\n（2）工作质量：差错率、返工率、客户满意度等。\n\n（3）工作效率：任务按时完成率、平均处理时长等。\n\n（4）考勤纪律：出勤率、迟到早退次数等。\n\n第八条 管理者KPI指标：在员工指标基础上增加：\n\n（1）团队管理：下属员工流失率、团队绩效提升率。\n\n（2）人才发展：下属培训完成率、人才梯队建设情况。\n\n（3）预算控制：部门费用预算执行率。\n\n（4）跨部门协作：关联部门满意度评价。\n\n# 第四章 考核流程\n\n第九条 考核流程：考核按以下五个步骤进行：\n\n（1）目标设定：考核周期初，考核者与被考核者沟通确认考核目标与标准。\n\n（2）过程跟踪：考核周期中，考核者持续关注被考核者工作进展，及时指导反馈。\n\n（3）自我评价：考核周期结束时，被考核者对照目标进行自评，撰写工作总结。\n\n（4）上级评价：直属上级根据客观数据和工作表现进行评价打分。\n\n（5）结果确认：考核结果经双方沟通确认后，报上一级领导审核。\n\n第十条 申诉机制：员工对考核结果有异议的，可在考核结果公示后5个工作日内向人力资源部提出书面申诉，人力资源部在10个工作日内组织复核并反馈。\n\n# 第五章 考核等级与比例\n\n第十一条 考核等级划分：\n\nA级（优秀）：考核分数≥90分，占比≤10%。\n\nB级（良好）：考核分数80—89分，占比≤20%。\n\nC级（称职）：考核分数70—79分。\n\nD级（待改进）：考核分数60—69分，占比≥5%。\n\nE级（不称职）：考核分数＜60分。\n\n第十二条 强制分布：各部门考核结果须符合等级比例要求，确保区分度。A级和B级不超过部门总人数的30%。\n\n# 第六章 考核结果应用\n\n第十三条 薪酬调整：\n\n（1）年度考核为A级：薪酬晋升2档，年终奖系数1.5倍。\n\n（2）年度考核为B级：薪酬晋升1档，年终奖系数1.2倍。\n\n（3）年度考核为C级：薪酬不变，年终奖系数1.0倍。\n\n（4）年度考核为D级：薪酬冻结，年终奖系数0.5倍，制定改进计划。\n\n（5）年度考核为E级：降薪一档或调岗，不享受年终奖。\n\n第十四条 晋升与淘汰：\n\n（1）连续两年年度考核为A级的，优先纳入晋升候选人。\n\n（2）年度考核为E级或连续两年为D级的，进行岗位调整或进入绩效改进计划。\n\n（3）绩效改进计划（PIP）期为3个月，期满考核仍不合格的，依法解除劳动合同。\n\n第十五条 培训发展：考核结果作为培训需求分析和培训资源分配的重要依据。优秀员工优先获得外派培训、轮岗锻炼等发展机会。\n\n# 第七章 特殊情形\n\n第十六条 试用期员工：试用期员工参加月度考核，考核结果作为是否转正的重要依据。试用期考核不合格的，依法解除劳动合同。\n\n第十七条 调岗员工：考核周期内调动岗位的，调入部门与调出部门各按实际工作时间占比出具考核意见。\n\n第十八条 长期休假员工：考核周期内累计休假（含病假、事假、产假等）超过考核周期50%的，当期考核结果按\"待定\"处理，不参与当期绩效薪酬核算。\n\n# 第八章 考核组织与管理\n\n第十九条 考核组织：人力资源部是绩效考核的归口管理部门，负责制度制定、流程监督、数据汇总和结果应用。\n\n第二十条 考核纪律：考核者须遵守公平公正原则，严禁徇私舞弊、打击报复。违反者按公司纪律处分制度处理。\n\n第二十一条 考核档案：绩效考核结果纳入员工档案，保存期限不少于2年。\n\n# 第九章 附则\n\n第二十二条 本制度由人力资源部负责解释和修订。\n\n第二十三条 各部门可在本制度框架下制定实施细则，报人力资源部备案。\n\n第二十四条 本制度自发布之日起施行，原有绩效相关规定同时废止。','自动导入','user-admin-001',NULL);
/*!40000 ALTER TABLE `document_versions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documents`
--

DROP TABLE IF EXISTS `documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents` (
  `document_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `format` enum('PDF','WORD','MARKDOWN','HTML') COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `version_note` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('DRAFT','PUBLISHED','ARCHIVED') COLLATE utf8mb4_unicode_ci NOT NULL,
  `access_level` enum('INHERIT','ALL_ROLES','HR_ADMIN_ONLY','ADMIN_ONLY') COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploaded_by` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_path` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `word_count` int DEFAULT NULL,
  `chunk_count` int DEFAULT NULL,
  `embedding_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `published_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`document_id`),
  KEY `category_id` (`category_id`),
  KEY `uploaded_by` (`uploaded_by`),
  FULLTEXT KEY `ft_docs_content` (`title`,`content`) /*!50100 WITH PARSER `ngram` */ ,
  CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`),
  CONSTRAINT `documents_ibfk_2` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documents`
--

LOCK TABLES `documents` WRITE;
/*!40000 ALTER TABLE `documents` DISABLE KEYS */;
INSERT INTO `documents` VALUES ('2a046aad5cfb4948a9cf99c31b2c4511','薪酬制度','薪酬管理制度\n（2026年修订版）\n\n第一章 总则\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\n第二条 适用范围：本制度适用于公司全体正式员工。实习生、临时工等特殊用工形式的薪酬管理另行规定。\n第三条 基本原则：\n（1）战略性原则：薪酬设计以公司战略为导向，与公司发展阶段和经营目标相匹配。\n（2）公平性原则：以岗位价值为基础，体现内部公平性和外部竞争力。\n（3）激励性原则：通过绩效奖金等激励性工资单元激发员工工作积极性。\n（4）合规性原则：严格遵守国家劳动法律法规，保障员工合法权益。\n（5）经济性原则：薪酬水平与公司经济效益和支付能力相适应。\n第二章 薪酬结构\n第四条 薪酬总构成：员工薪酬由基本工资、岗位工资、绩效工资、津贴补贴、奖金五部分组成。\n第五条 基本工资：根据员工的学历、工龄、技能等级等因素确定的基础性薪酬。\n（1）学历工资：大专300元/月，本科500元/月，硕士800元/月，博士1200元/月。\n（2）工龄工资：每年增加50元/月，上限500元/月。\n第六条 岗位工资：根据员工所在岗位的职责大小、技能要求、工作强度等因素确定的薪酬。岗位工资按职级分为P1—P10共十个级别。\n第七条 绩效工资：根据员工月度/年度绩效考核结果核发的浮动薪酬。一般员工绩效工资占比为总薪酬的20%—30%，管理层占比为30%—50%。\n第八条 津贴补贴：\n（1）通讯补贴：普通员工100元/月，主管级200元/月，经理级300元/月。\n（2）交通补贴：300元/月（统一标准）。\n（3）餐补：20元/工作日出勤日。\n（4）高温补贴：每年6—9月，按国家规定标准发放。\n（5）项目现场津贴：外派项目现场人员，按项目地标准给予补贴。\n第九条 奖金：\n（1）年终奖金：根据公司年度经营效益和个人年度绩效考核结果发放，一般为1-3个月工资。\n（2）项目奖金：项目完成并产生效益后，按税后利润的3%—5%提取，根据参与人员的贡献度发放。\n（3）专项奖金：对在技术创新、降本增效、市场开拓等方面有突出贡献的员工设立的特别奖励。\n第三章 薪酬定级与调整\n第十条 新员工定薪：新员工入职时，根据其学历、工作经验、岗位要求和市场薪酬水平，由用人部门与人力资源部共同确定初始薪酬等级。\n第十一条 薪酬调整类型：\n（1）年度普调：公司每年根据市场薪酬水平、CPI变动和公司经营状况进行薪酬整体调整。\n（2）绩效调薪：根据年度绩效考核结果进行个人薪酬调整。考核为\"优秀\"者可晋升一档，连续两年\"优秀\"者可晋升一级。\n（3）岗位变动调薪：员工岗位发生变动（晋升、降级、平调）时，薪酬相应调整。晋升的从批准次月起执行新薪酬，降级的从批准当月起执行。\n（4）特殊调薪：对紧缺人才、特殊贡献者可进行特殊调薪，须经总经理审批。\n第四章 薪资核算与发放\n第十二条 薪资计算周期：每月1日至月末最后一天为一个薪酬计算周期。\n第十三条 薪资发放日期：每月10日发放上月薪资。若遇休息日或法定假日，提前至最近工作日发放。\n第十四条 日工资计算：日工资=月基本工资÷21.75天（国家规定的月平均计薪天数）。\n第十五条 新入职/离职员工薪资计算：\n（1）新入职员工：当月薪酬=月基本工资÷21.75×当月实际出勤天数。\n（2）离职员工：薪酬结算至最后工作日，于最近薪资发放日统一支付。\n第十六条 薪资扣除项：根据国家法规，公司依法代扣代缴个人所得税、社会保险及住房公积金个人缴纳部分。\n第十七条 薪资保密：公司实行薪酬保密制度。员工不得泄露本人薪资，不得打听他人薪资，违者将视情节给予纪律处分。\n第五章 特殊情况薪酬管理\n第十八条 试用期薪酬：试用期员工薪酬为转正后薪酬的80%，试用期不超过6个月。\n第十九条 病假薪酬：因病请假，按以下标准计发：\n（1）病假1天以内：不扣工资。\n（2）病假2天以上、1个月以内：按本人工资的80%计发。\n（3）病假超过1个月：按当地最低工资标准的80%计发。\n第二十条 事假薪酬：事假按实际出勤天数计发工资，事假期间不享受绩效工资。\n第二十一条 待岗薪酬：公司因经营需要安排员工待岗的，第一个月按正常工资发放，第二个月起按当地最低工资标准发放生活费。\n第六章 附则\n第二十二条 本制度由人力资源部负责解释和修订。\n第二十三条 本制度自发布之日起施行，原有薪酬相关规定同时废止。','cat_doc_salary','WORD','1.2','文件替换: 薪酬制度.docx','PUBLISHED','INHERIT','hr001','/uploads/薪酬制度.docx',1841,1,'completed','2026-06-30 14:32:42','2026-06-30 03:29:23','2026-06-30 14:32:46'),('73b945e6ca349f8d','绩效制度','**绩效考核管理制度**\n\n（2026年修订版）\n\n# 第一章 总则\n\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，特制定本制度。\n\n第二条 适用范围：本制度适用于公司全体正式员工。试用期员工、实习生的考核办法另行规定。\n\n第三条 考核原则：\n\n（1）结果导向原则：以工作成果和业绩为考核核心。\n\n（2）客观公正原则：以事实和数据为依据，避免主观偏见。\n\n（3）公开透明原则：考核标准、程序和结果及时公开，接受监督。\n\n（4）持续改进原则：通过考核发现问题、促进改进，而非单纯惩罚。\n\n（5）分层分类原则：不同层级、不同岗位类别采用差异化的考核方式。\n\n# 第二章 考核周期与内容\n\n第四条 考核周期：\n\n（1）月度考核：每月进行一次，针对当月工作目标完成情况进行评价。\n\n（2）季度考核：每季度进行一次综合评估，关注阶段性目标达成情况。\n\n（3）年度考核：每年12月进行全年综合考核，作为年终奖、晋升、调薪的主要依据。\n\n第五条 考核维度：绩效考核主要从以下三个维度进行评价：\n\n（1）工作业绩（权重70%）：主要考核KPI指标完成情况、工作质量、工作效率、目标达成度等。\n\n（2）工作能力（权重20%）：主要考核专业技能、问题解决能力、学习创新能力、沟通协作能力等。\n\n（3）工作态度（权重10%）：主要考核责任心、积极性、团队合作精神、纪律性等。\n\n# 第三章 考核指标体系\n\n第六条 KPI设定：各级管理者与下属在考核周期初共同制定关键绩效指标（KPI），KPI须符合SMART原则（具体、可量化、可实现、相关性、时限性）。\n\n第七条 普通员工KPI指标：\n\n（1）工作任务完成率：考核周期内计划任务的完成比例。\n\n（2）工作质量：差错率、返工率、客户满意度等。\n\n（3）工作效率：任务按时完成率、平均处理时长等。\n\n（4）考勤纪律：出勤率、迟到早退次数等。\n\n第八条 管理者KPI指标：在员工指标基础上增加：\n\n（1）团队管理：下属员工流失率、团队绩效提升率。\n\n（2）人才发展：下属培训完成率、人才梯队建设情况。\n\n（3）预算控制：部门费用预算执行率。\n\n（4）跨部门协作：关联部门满意度评价。\n\n# 第四章 考核流程\n\n第九条 考核流程：考核按以下五个步骤进行：\n\n（1）目标设定：考核周期初，考核者与被考核者沟通确认考核目标与标准。\n\n（2）过程跟踪：考核周期中，考核者持续关注被考核者工作进展，及时指导反馈。\n\n（3）自我评价：考核周期结束时，被考核者对照目标进行自评，撰写工作总结。\n\n（4）上级评价：直属上级根据客观数据和工作表现进行评价打分。\n\n（5）结果确认：考核结果经双方沟通确认后，报上一级领导审核。\n\n第十条 申诉机制：员工对考核结果有异议的，可在考核结果公示后5个工作日内向人力资源部提出书面申诉，人力资源部在10个工作日内组织复核并反馈。\n\n# 第五章 考核等级与比例\n\n第十一条 考核等级划分：\n\nA级（优秀）：考核分数≥90分，占比≤10%。\n\nB级（良好）：考核分数80—89分，占比≤20%。\n\nC级（称职）：考核分数70—79分。\n\nD级（待改进）：考核分数60—69分，占比≥5%。\n\nE级（不称职）：考核分数＜60分。\n\n第十二条 强制分布：各部门考核结果须符合等级比例要求，确保区分度。A级和B级不超过部门总人数的30%。\n\n# 第六章 考核结果应用\n\n第十三条 薪酬调整：\n\n（1）年度考核为A级：薪酬晋升2档，年终奖系数1.5倍。\n\n（2）年度考核为B级：薪酬晋升1档，年终奖系数1.2倍。\n\n（3）年度考核为C级：薪酬不变，年终奖系数1.0倍。\n\n（4）年度考核为D级：薪酬冻结，年终奖系数0.5倍，制定改进计划。\n\n（5）年度考核为E级：降薪一档或调岗，不享受年终奖。\n\n第十四条 晋升与淘汰：\n\n（1）连续两年年度考核为A级的，优先纳入晋升候选人。\n\n（2）年度考核为E级或连续两年为D级的，进行岗位调整或进入绩效改进计划。\n\n（3）绩效改进计划（PIP）期为3个月，期满考核仍不合格的，依法解除劳动合同。\n\n第十五条 培训发展：考核结果作为培训需求分析和培训资源分配的重要依据。优秀员工优先获得外派培训、轮岗锻炼等发展机会。\n\n# 第七章 特殊情形\n\n第十六条 试用期员工：试用期员工参加月度考核，考核结果作为是否转正的重要依据。试用期考核不合格的，依法解除劳动合同。\n\n第十七条 调岗员工：考核周期内调动岗位的，调入部门与调出部门各按实际工作时间占比出具考核意见。\n\n第十八条 长期休假员工：考核周期内累计休假（含病假、事假、产假等）超过考核周期50%的，当期考核结果按\"待定\"处理，不参与当期绩效薪酬核算。\n\n# 第八章 考核组织与管理\n\n第十九条 考核组织：人力资源部是绩效考核的归口管理部门，负责制度制定、流程监督、数据汇总和结果应用。\n\n第二十条 考核纪律：考核者须遵守公平公正原则，严禁徇私舞弊、打击报复。违反者按公司纪律处分制度处理。\n\n第二十一条 考核档案：绩效考核结果纳入员工档案，保存期限不少于2年。\n\n# 第九章 附则\n\n第二十二条 本制度由人力资源部负责解释和修订。\n\n第二十三条 各部门可在本制度框架下制定实施细则，报人力资源部备案。\n\n第二十四条 本制度自发布之日起施行，原有绩效相关规定同时废止。','cat_doc_perf','WORD','1.0','','PUBLISHED','ALL_ROLES','user-admin-001','/uploads/绩效制度.docx',2237,2,'completed',NULL,NULL,'2026-06-30 14:05:11'),('7ab9fe6efcb24b4e9d9c77a9c5a1f027','考勤制度','**考勤管理制度**\n\n（2026年修订版）\n\n# 第一章 总则\n\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情况，特制定本制度。\n\n第二条 适用范围：本制度适用于公司全体正式聘用员工。实习生、兼职人员及劳务派遣人员参照本制度执行或另行约定。\n\n第三条 基本原则：坚持公平、公正、公开原则，实行标准化、数字化的考勤管理机制。\n\n# 第二章 工作时间\n\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\n\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。\n\n第六条 弹性工作制：经部门负责人批准，部分岗位可实行弹性工作制，核心工作时间为10:00—16:00，其余时间可在规定范围内自主安排。\n\n第七条 特殊工时制：因业务需要实行综合计算工时制或不定时工作制的岗位，须经人力资源部审核并报劳动行政部门批准后执行。\n\n# 第三章 考勤方式\n\n第八条 考勤工具：公司采用电子考勤系统（人脸识别/指纹/打卡），员工须在规定时间内完成签到、签退。\n\n第九条 签到签退：每个工作日须签到一次、签退一次。上午9:00前完成签到，下午18:00后完成签退。未按时签到签退的，视为迟到或早退。\n\n第十条 外出登记：工作时间内因公外出，须提前在OA系统或纸质《外出登记表》中登记，经直属上级审批后方可外出。\n\n第十一条 出差管理：员工出差须提前填写《出差申请单》，经部门负责人审批后报人力资源部备案。出差期间考勤以出差单为准。\n\n第十二条 外勤/现场人员：因工作性质无法正常考勤的，由部门负责人每月出具考勤确认单，报人力资源部审核备案。\n\n# 第四章 迟到、早退与旷工\n\n第十三条 迟到：超过规定上班时间30分钟以内到岗的，视为迟到。\n\n（1）月累计迟到1-2次：口头提醒。\n\n（2）月累计迟到3-5次：每次扣款30元，并予以书面警告。\n\n（3）月累计迟到6次及以上：视为严重违纪，扣发当月全勤奖，纳入绩效考核负面记录。\n\n第十四条 早退：未经批准在下班时间前擅自离岗的，视为早退。早退处理标准与迟到相同。\n\n第十五条 旷工：以下情形视为旷工：\n\n（1）未履行请假手续或请假未获批准而擅自缺勤的。\n\n（2）迟到或早退超过30分钟以上且未说明合理理由的，按旷工半天处理。\n\n（3）假期届满未经续假或续假未获批准而未到岗的。\n\n第十六条 旷工处理：\n\n（1）旷工半天：扣除当日工资及当月全勤奖。\n\n（2）旷工1天：扣除当日工资、当月全勤奖，并予以书面警告。\n\n（3）连续旷工3天（含）以上或月累计旷工5天（含）以上：属于严重违反公司规章制度，公司有权单方解除劳动合同，不予经济补偿。\n\n# 第五章 加班管理\n\n第十七条 加班定义：因工作需要，经审批后在正常工作时间以外延长工作时间的，视为加班。\n\n第十八条 加班申请：加班须提前填写《加班申请单》，经部门负责人审批后报人力资源部备案。未经审批的不视为加班。\n\n第十九条 加班时限：依据《劳动法》规定，每月加班不得超过36小时。确需超时须经总经理审批。\n\n第二十条 加班补偿：\n\n（1）工作日延长工作时间：按不低于本人小时工资的150%支付加班工资。\n\n（2）休息日安排工作且不能补休的：按不低于本人日工资的200%支付加班工资。\n\n（3）法定节假日安排工作的：按不低于本人日工资的300%支付加班工资。\n\n（4）经理级及以上管理人员实行不定时工作制，不计算加班工资，可申请调休。\n\n第二十一条 调休：休息日加班的，应优先安排调休。调休须在加班发生后1个月内完成，逾期作废。\n\n# 第六章 全勤奖\n\n第二十二条 全勤奖标准：当月无迟到、早退、旷工、请假（年假除外）记录的员工，享受全勤奖200元/月。\n\n第二十三条 取消条件：当月有迟到/早退记录、病假/事假记录、旷工记录的，取消当月全勤奖。法定假期（年假、婚假、产假、丧假等）不影响全勤奖。\n\n# 第七章 考勤数据管理\n\n第二十四条 考勤统计：每月5日前，人力资源部完成上月考勤数据统计汇总，经公示无异议后作为薪资核算依据。\n\n第二十五条 考勤异议：员工对考勤结果有异议的，须在公示后3个工作日内向人力资源部提出书面申诉，逾期不予受理。\n\n第二十六条 考勤档案：考勤原始记录至少保存2年备查，考勤汇总表长期保存。\n\n# 第八章 附则\n\n第二十七条 本制度由人力资源部负责解释和修订。\n\n第二十八条 本制度与国家法律法规不一致的，以国家法律法规为准。\n\n第二十九条 本制度自发布之日起施行，原有考勤相关规定同时废止。','cat_doc_attend','WORD','1.3','文件替换: 考勤制度.docx','PUBLISHED','INHERIT','hr001','/uploads/考勤制度.docx',1951,1,'completed','2026-06-30 14:39:42','2026-06-30 02:57:13','2026-06-30 14:39:44'),('87d0b8363a47c8ca','福利制度','**员工福利管理制度**\n\n（2026年修订版）\n\n# 第一章 总则\n\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\n\n第二条 适用范围：本制度适用于公司全体正式员工。试用期员工和特殊劳动关系人员适用相应条款。\n\n第三条 福利原则：\n\n（1）合法性原则：各项福利须符合国家及地方相关法律法规。\n\n（2）普惠性原则：保障全体员工享有基本福利权益。\n\n（3）激励性原则：部分福利与员工贡献、绩效相挂钩。\n\n（4）可持续原则：福利支出控制在公司人力成本预算范围内。\n\n# 第二章 法定社会保险与公积金\n\n第四条 五险一金：公司依法为转正员工缴纳养老保险、医疗保险、工伤保险、失业保险、生育保险（现已并入医疗保险）及住房公积金。\n\n第五条 缴费基数与比例：社保缴费基数根据员工上年度月平均工资（在社平工资60%—300%之间）确定，缴费比例按国家及地方政府最新规定执行。\n\n第六条 公积金缴纳：住房公积金公司及个人缴存比例均为当地规定标准的最高档（一般为5%—12%）。\n\n# 第三章 补充商业保险\n\n第七条 补充医疗保险：公司为全体员工购买补充医疗保险，用于报销基本医保目录外的合理医疗费用，年度报销上限为2万元/人。\n\n第八条 意外伤害保险：公司为全体员工购买意外伤害保险，保额为20万元/人。对长期外派、项目现场员工，保额提升至50万元/人。\n\n第九条 重大疾病保险：工作满2年的员工，公司为其购买重大疾病保险，保额10万元。\n\n# 第四章 带薪假期福利\n\n第十条 法定节假日：员工享有国家规定的全部法定节假日（元旦、春节、清明节、劳动节、端午节、中秋节、国庆节等），共计11天/年。\n\n第十一条 年休假：员工累计工作满1年不满10年的，年休假5天；满10年不满20年的，年休假10天；满20年的，年休假15天。\n\n第十二条 婚假：员工依法办理结婚登记的，享受婚假3天。符合晚婚条件的，额外增加晚婚假，按当地规定执行。\n\n第十三条 产假/陪产假：女职工生育享受不少于98天产假，难产或多胞胎生育的，按国家规定增加。男职工享受陪产假15天。\n\n第十四条 丧假：员工直系亲属（父母、配偶、子女）去世的，给予丧假3天。\n\n第十五条 病假：员工因病需治疗休养的，凭医院证明申请病假，公司给予每年5天全薪病假，超出部分按薪酬制度执行。\n\n# 第五章 健康关怀\n\n第十六条 年度健康体检：公司每年组织一次员工健康体检，体检项目包括常规项目及专项筛查。体检费用由公司承担，标准为：普通员工800元/人，40岁以上员工1200元/人。\n\n第十七条 心理健康关怀：公司提供员工心理援助计划（EAP），包括心理咨询热线、心理健康讲座等，费用由公司承担。\n\n第十八条 员工健身房/运动补贴：公司在办公区域设立健身房，或为员工提供运动健身补贴300元/月。\n\n# 第六章 生活福利\n\n第十九条 节日福利：春节、端午节、中秋节等传统节日，公司发放节日礼金或礼品，标准为300—500元/人。\n\n第二十条 生日福利：员工生日当月发放生日礼金200元或等值礼物。\n\n第二十一条 结婚礼金：员工结婚，公司赠送礼金1000元。\n\n第二十二条 生育礼金：员工生育子女，公司赠送礼金800元。\n\n第二十三条 抚恤金：员工直系亲属去世，公司发放慰问金500元。\n\n# 第七章 住房与交通福利\n\n第二十四条 住房补贴：公司为未享受公司宿舍的员工提供住房补贴，标准根据职级确定：普通员工500元/月，主管级800元/月，经理级1500元/月。\n\n第二十五条 员工宿舍：公司为外地员工提供员工宿舍，标准间配置，个人承担水电费。\n\n第二十六条 通勤班车：公司在主要居住区提供通勤班车服务。未覆盖区域提供交通补贴。\n\n# 第八章 培训与发展福利\n\n第二十七条 培训经费：公司每年按员工工资总额的2%提取培训经费。\n\n第二十八条 学历提升资助：员工在职攻读与工作岗位相关的学历、学位，取得证书后，公司给予1000—5000元一次性奖励。\n\n第二十九条 职业资格补贴：员工考取与岗位相关的国家职业资格证书，公司给予一次性奖励500—2000元，并按月发放资格补贴100—500元。\n\n# 第九章 附则\n\n第三十条 本制度由人力资源部负责解释和修订。\n\n第三十一条 本制度自发布之日起施行，原有福利相关规定同时废止。','cat_doc_benefit','WORD','1.0','','PUBLISHED','ALL_ROLES','user-admin-001','/uploads/福利制度.docx',1825,1,'completed',NULL,NULL,'2026-06-30 14:05:15');
/*!40000 ALTER TABLE `documents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employee_data_sensitivity`
--

DROP TABLE IF EXISTS `employee_data_sensitivity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee_data_sensitivity` (
  `field_id` int NOT NULL AUTO_INCREMENT,
  `field_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `field_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sensitivity_level` enum('PUBLIC','DEPARTMENT','PRIVATE') COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_table` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_column` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`field_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee_data_sensitivity`
--

LOCK TABLES `employee_data_sensitivity` WRITE;
/*!40000 ALTER TABLE `employee_data_sensitivity` DISABLE KEYS */;
INSERT INTO `employee_data_sensitivity` VALUES (1,'name','姓名','PUBLIC','users','name',NULL,NULL,NULL),(2,'employee_id','工号','PUBLIC','users','employee_id',NULL,NULL,NULL),(3,'email','邮箱','DEPARTMENT','users','email',NULL,NULL,NULL),(4,'phone','手机号','PRIVATE','users','phone',NULL,NULL,NULL),(5,'job_level','职级','DEPARTMENT','users','job_level',NULL,NULL,NULL),(6,'hire_date','入职日期','DEPARTMENT','users','hire_date',NULL,NULL,NULL),(7,'work_location','工作地','DEPARTMENT','users','work_location',NULL,NULL,NULL),(8,'marital_status','婚姻状态','PRIVATE','users','marital_status',NULL,NULL,NULL);
/*!40000 ALTER TABLE `employee_data_sensitivity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faqs`
--

DROP TABLE IF EXISTS `faqs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faqs` (
  `faq_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `question` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `answer` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `related_doc_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `keywords` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `view_count` int DEFAULT NULL,
  `status` enum('ACTIVE','ARCHIVED') COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_by` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`faq_id`),
  KEY `category_id` (`category_id`),
  KEY `related_doc_id` (`related_doc_id`),
  KEY `created_by` (`created_by`),
  FULLTEXT KEY `ft_faq_search` (`question`,`keywords`) /*!50100 WITH PARSER `ngram` */ ,
  CONSTRAINT `faqs_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`),
  CONSTRAINT `faqs_ibfk_2` FOREIGN KEY (`related_doc_id`) REFERENCES `documents` (`document_id`) ON DELETE SET NULL,
  CONSTRAINT `faqs_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faqs`
--

LOCK TABLES `faqs` WRITE;
/*!40000 ALTER TABLE `faqs` DISABLE KEYS */;
INSERT INTO `faqs` VALUES ('faq-attend-01','每天的上下班时间是什么？','公司实行标准工时制，每日工作时间为上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。部分岗位经部门负责人批准可实行弹性工作制，核心工作时间为10:00—16:00。','cat_faq_root',NULL,'上下班 时间 考勤',2,'ACTIVE','user-admin-001',NULL,'2026-06-30 12:28:24'),('faq-attend-02','迟到会有什么处罚？','月累计迟到1-2次给予口头提醒；3-5次每次扣款30元并书面警告；6次及以上视为严重违纪，扣发当月全勤奖并纳入绩效考核负面记录。迟到超过30分钟以上且未说明合理理由的按旷工半天处理。','cat_faq_root',NULL,'迟到 处罚 扣款',1,'ACTIVE','user-admin-001',NULL,'2026-06-30 12:39:57'),('faq-attend-03','如何申请加班？','加班须提前填写《加班申请单》，经部门负责人审批后报人力资源部备案，未经审批的不视为加班。平时延长工作时间按150%支付加班工资，休息日加班按200%支付（或安排调休），法定节假日按300%支付。','cat_faq_root',NULL,'加班 申请 加班费',1,'ACTIVE','user-admin-001',NULL,'2026-06-30 13:56:15'),('faq-benefit-01','公司有哪些福利？','公司福利包括：五险一金、补充医疗保险（年度报销上限2万元）、意外伤害保险（保额20万）、年度健康体检、节日福利（300-500元/人）、生日礼金200元、结婚礼金1000元、住房补贴（500-1500元/月）、员工心理援助计划（EAP）等。','cat_faq_benefit',NULL,'福利 五险一金 保险 体检 补贴',NULL,'ACTIVE','user-admin-001',NULL,NULL),('faq-benefit-02','年度体检什么时候安排？','公司每年组织一次员工健康体检，具体时间由人力资源部统一安排并提前通知。体检费用由公司承担：普通员工800元/人，40岁以上员工1200元/人。','cat_faq_benefit',NULL,'体检 安排 时间',NULL,'ACTIVE','user-admin-001',NULL,NULL),('faq-leave-01','年假有多少天？怎么计算？','员工累计工作满1年不满10年的，年休假5天；满10年不满20年的，年休假10天；满20年的，年休假15天。年假须提前5个工作日申请，经部门负责人审批后执行。','cat_faq_leave',NULL,'年假 休假 天数 计算',NULL,'ACTIVE','user-admin-001',NULL,NULL),('faq-leave-02','婚假、产假怎么规定的？','员工依法办理结婚登记的享受婚假3天；女职工生育享受不少于98天产假，难产或多胞胎生育的按国家规定增加；男职工享陪产假15天。','cat_faq_leave',NULL,'婚假 产假 陪产假',1,'ACTIVE','user-admin-001',NULL,'2026-06-30 13:56:31'),('faq-leave-03','病假和事假有什么区别？','病假需凭医院证明申请，公司给予每年5天全薪病假，超出部分按薪酬制度执行。事假为无薪假期，须提前申请并获批准，原则上每月不超过2天。','cat_faq_leave',NULL,'病假 事假 区别',NULL,'ACTIVE','user-admin-001',NULL,NULL),('faq-perf-01','绩效考核怎么评定？','绩效考核采用季度考核与年度考核相结合的方式。考核指标包括工作业绩（60%）、工作能力（20%）、工作态度（20%）三个维度。考核结果分为S/A/B/C/D五个等级，直接关联晋升和奖金。','cat_faq_perf',NULL,'绩效 考核 评定 等级',NULL,'ACTIVE','user-admin-001',NULL,NULL),('faq-perf-02','晋升需要什么条件？','晋升需满足：1）在当前岗位任职满1年以上；2）近两次绩效考核评级均在A级以上；3）通过晋升评审委员会评审。职级每晋升一级，基本工资相应上调10%-20%。','cat_faq_perf',NULL,'晋升 条件 职级',NULL,'ACTIVE','user-admin-001',NULL,NULL),('faq-salary-01','工资什么时候发放？','公司实行月薪制，每月15日发放上月工资（遇节假日顺延）。工资包括基本工资、岗位津贴、绩效工资等组成部分。','cat_faq_salary',NULL,'工资 发放 时间 发薪日',NULL,'ACTIVE','user-admin-001',NULL,NULL),('faq-salary-02','什么是全勤奖？如何获得？','当月无迟到、早退、旷工、请假（年假除外）记录的员工可享受全勤奖200元/月。法定假期（年假、婚假、产假、丧假等）不影响全勤奖。','cat_faq_salary',NULL,'全勤奖 条件 金额',NULL,'ACTIVE','user-admin-001',NULL,NULL);
/*!40000 ALTER TABLE `faqs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `policy_interpretations`
--

DROP TABLE IF EXISTS `policy_interpretations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `policy_interpretations` (
  `interpretation_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `doc_version` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `summary` text COLLATE utf8mb4_unicode_ci,
  `flowchart` text COLLATE utf8mb4_unicode_ci,
  `comparison_table` text COLLATE utf8mb4_unicode_ci,
  `key_points` json DEFAULT NULL,
  `model` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`interpretation_id`),
  UNIQUE KEY `uq_interpretation_doc_version` (`document_id`,`doc_version`),
  CONSTRAINT `policy_interpretations_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`document_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `policy_interpretations`
--

LOCK TABLES `policy_interpretations` WRITE;
/*!40000 ALTER TABLE `policy_interpretations` DISABLE KEYS */;
INSERT INTO `policy_interpretations` VALUES ('2988887c9a3f4c3381306f51934dfed6','73b945e6ca349f8d','1.0','公司实行月度、季度、年度绩效考核，以工作业绩（占70%）、能力（20%）、态度（10%）为核心评价维度。考核结果分为A（优秀）到E（不称职）五级，并强制规定A、B级总人数不超过部门30%。年度考核结果直接决定薪酬调整、年终奖系数以及晋升机会，例如A级可晋升2档工资并拿到1.5倍年终奖。考核流程包括目标设定、过程跟踪、自评、上级评价和结果确认，若对结果有异议可在公示后5个工作日内申诉。','flowchart TD\n  A[考核周期初：目标设定与标准沟通] --> B[考核周期中：过程跟踪与指导反馈]\n  B --> C[考核周期结束：自我评价与工作总结]\n  C --> D[直属上级根据数据表现评价打分]\n  D --> E[双方沟通确认结果并报上一级审核]','| 等级 | 考核分数 | 强制分布比例 | 年度薪酬调整 | 年终奖系数 | 备注 |\n|------|----------|--------------|--------------|------------|------|\n| A级（优秀） | ≥90分 | ≤10% | 薪酬晋升2档 | 1.5倍 | |\n| B级（良好） | 80-89分 | ≤20% | 薪酬晋升1档 | 1.2倍 | A、B总人数≤部门30% |\n| C级（称职） | 70-79分 | 无限制 | 薪酬不变 | 1.0倍 | |\n| D级（待改进） | 60-69分 | ≥5% | 薪酬冻结 | 0.5倍 | 需制定改进计划 |\n| E级（不称职） | ＜60分 | 按分数确定 | 降薪一档或调岗 | 不享受 | |','[\"年度考核等级直接影响工资、年终奖和晋升，A级涨薪2档并拿1.5倍奖金，E级可能降薪且无年终奖。\", \"考核采取强制分布，优秀（A）和良好（B）的名额有限，加起来不超过部门人数的30%，待改进（D）比例至少5%。\", \"连续两年D级或一年E级会进入岗位调整或绩效改进计划（PIP），期满仍不合格可能被解除劳动合同。\", \"对考核结果有疑问可在公示后5个工作日内向人力资源部书面申诉，复核结果10个工作日内反馈。\", \"员工在周期内因休假（病假、事假、产假等）累计超50%工作时间，当期考核按“待定”处理，不参与当期绩效薪酬核算。\"]','deepseek-v4-pro','2026-07-01 00:00:13'),('50c2b276882f4e7fac602b22072be0f8','2a046aad5cfb4948a9cf99c31b2c4511','1.2','这份制度规定了公司正式员工的薪酬构成、定级调整和发放规则。你的工资由基本工资、岗位工资、绩效工资、津贴补贴和奖金五部分组成。基本工资与学历、工龄挂钩，绩效工资根据考核结果浮动，各类津贴有明确标准。薪酬每年可能普调，个人绩效优秀有机会上调，所有调整需按规定流程办理。工资每月10号发放，公司实行薪酬保密，不得泄露或打听。','','| 病假天数 | 薪酬计发标准 |\n| --- | --- |\n| 1天以内 | 不扣工资 |\n| 2天以上、1个月以内 | 按本人工资的80%计发 |\n| 超过1个月 | 按当地最低工资标准的80%计发 |','[\"薪酬由基本工资、岗位工资、绩效工资、津贴补贴、奖金五部分组成，其中绩效工资浮动占比20%-50%。\", \"学历工资按大专300元、本科500元、硕士800元、博士1200元/月发放，工龄工资每年增加50元/月，上限500元。\", \"病假1天以内不扣工资，2天至1个月发80%，超过1个月按当地最低工资80%计发；事假期间不计发绩效工资。\", \"试用期薪酬按转正后80%发放，试用期最长不超过6个月；待岗首月全额工资，次月起发当地最低标准生活费。\", \"薪酬严格保密，不得泄露本人薪资或打听他人薪资，违者将受纪律处分。\"]','deepseek-v4-pro','2026-06-30 23:58:50'),('92c89b7db0084451902e74ff6a3fab3b','7ab9fe6efcb24b4e9d9c77a9c5a1f027','1.3','本制度规定了公司的考勤规则。标准工作时间为周一至周五上午9点到下午6点，午休1小时，通过电子系统打卡。迟到、早退和旷工有明确的处罚，严重者可能被解除劳动合同。加班必须提前申请并经过审批，未经审批不计入加班，加班可按法定标准获得工资或调休。当月无任何迟到、早退、请假（年假除外）的员工可享受200元全勤奖。考勤结果每月公示，员工如有异议需在3个工作日内提出。','flowchart TD\n    A[员工需加班] --> B[提前填写《加班申请单》]\n    B --> C[部门负责人审批]\n    C --> D[人力资源部备案]\n    D --> E[实际加班]\n    E --> F{是否休息日加班？}\n    F -- 是 --> G[1个月内安排调休]\n    F -- 否 --> H[工作日加班发150%工资]\n    F -- 法定节假日 --> I[法定节假日加班发300%工资]\n    G --> J[逾期未调休作废]\n    H --> K[薪资核算发放]\n    I --> K','| 违规类型 | 具体情形 | 处理标准 |\n|----------|----------|------------|\n| 迟到/早退 | 月累计1-2次 | 口头提醒 |\n| 迟到/早退 | 月累计3-5次 | 每次扣款30元，书面警告 |\n| 迟到/早退 | 月累计6次及以上 | 视为严重违纪，扣发当月全勤奖，纳入绩效考核负面记录 |\n| 旷工 | 旷工半天 | 扣除当日工资及当月全勤奖 |\n| 旷工 | 旷工1天 | 扣除当日工资及当月全勤奖，书面警告 |\n| 旷工 | 连续旷工3天（含）以上或月累计旷工5天（含）以上 | 严重违反公司规章制度，公司有权单方解除劳动合同，不予经济补偿 |','[\"标准工时制为周一至周五 9:00-18:00（午休1小时），需通过电子系统打卡签到签退。\", \"迟到或早退30分钟内按次数累计处罚，超过30分钟未说明理由按旷工半天处理，连续旷工3天或月累计5天可被解雇。\", \"加班必须提前申请并审批，休息日加班优先调休（1个月内有效），法定节假日加班按300%支付工资。\", \"当月无迟到、早退、旷工及事假病假记录（年假除外）可获200元全勤奖。\", \"对考勤结果有异议须在公示后3个工作日内向人力资源部书面申诉，逾期不受理。\"]','deepseek-v4-pro','2026-07-01 00:09:32'),('e99e161d001847f0827e29c4b8944243','87d0b8363a47c8ca','1.0','本制度是公司为正式员工提供的全面福利保障方案，涵盖法定五险一金、补充商业保险、带薪假期、健康关怀、生活礼金、住房与交通补贴以及培训发展资助。福利遵循合法、普惠、激励和可持续原则，不同福利项目与职级、工龄、年龄等条件挂钩。员工可享受年度体检、生日礼金、节日福利等普惠待遇，也需了解带薪假期的天数标准和补充保险的适用门槛。具体标准根据岗位、工作年限和年龄有所差异，建议查看详细规则。','','| 福利项目 | 分档/分类条件 | 享受标准 |\n|----------|--------------|----------|\n| 年休假 | 工作满1年不满10年 | 5天/年 |\n| 年休假 | 工作满10年不满20年 | 10天/年 |\n| 年休假 | 工作满20年 | 15天/年 |\n| 健康体检 | 普通员工（40岁以下） | 800元/人 |\n| 健康体检 | 40岁以上员工 | 1200元/人 |\n| 住房补贴 | 普通员工 | 500元/月 |\n| 住房补贴 | 主管级 | 800元/月 |\n| 住房补贴 | 经理级 | 1500元/月 |\n| 意外保险保额 | 普通员工 | 20万元/人 |\n| 意外保险保额 | 长期外派/项目现场员工 | 50万元/人 |\n| 重大疾病保险 | 工作满2年员工 | 保额10万元 |','[\"公司为转正员工缴纳五险一金，住房公积金按当地最高标准缴纳。\", \"补充商业保险包括补充医疗（报销上限2万）、意外伤害和重大疾病，外派员工意外保额有提升。\", \"带薪年假按累计工作年限分档，满1年5天，满10年10天，满20年15天；另有婚假、产假、陪产假、丧假和全薪病假。\", \"健康关怀包含年度体检（普通员工800元，40岁以上1200元）、心理援助计划和每月300元运动补贴或公司健身房。\", \"生活福利包括节日礼金、生日礼金、结婚礼金、生育礼金和慰问金，住房补贴与交通班车根据职级和居住情况提供。\", \"培训发展福利包括学历提升奖励（1000-5000元）和职业资格补贴（一次500-2000元，每月100-500元）。\"]','deepseek-v4-pro','2026-07-01 00:11:58');
/*!40000 ALTER TABLE `policy_interpretations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qa_records`
--

DROP TABLE IF EXISTS `qa_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `qa_records` (
  `record_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `question` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `answer` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `answer_type` enum('FAQ','RULE','SEARCH','RAG','NO_RESULT') COLLATE utf8mb4_unicode_ci NOT NULL,
  `confidence` float DEFAULT NULL,
  `reference_docs` json DEFAULT NULL,
  `response_time_ms` int DEFAULT NULL,
  `feedback` enum('HELPFUL','NOT_HELPFUL') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `feedback_reason` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_favorite` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`record_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_qa_records_session_id` (`session_id`),
  CONSTRAINT `qa_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qa_records`
--

LOCK TABLES `qa_records` WRITE;
/*!40000 ALTER TABLE `qa_records` DISABLE KEYS */;
INSERT INTO `qa_records` VALUES ('004b4e8cfe9f41d9b38e8e63a05ef05d','hr001','398772e3768b42bc9b9de92cb9529447','每日工作时间','根据公司考勤管理制度，每日工作时间为：**上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时**。\n\n**引用来源**：考勤制度','RAG',0.85,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}]',5205,NULL,NULL,0,'2026-06-30 03:24:19'),('06386c182753465686532832b2381503','2c2e97aac553494f91f1a0f742bbe387','4efc7238c8a84c14bcb96435be7ffc73','你是谁','🔒 抱歉，无法确认您在查询哪位员工的信息。请使用明确姓名后重试，例如「张三的工龄是多少」。如需查询自己，请使用「我的…」句式。','NO_RESULT',1,'[]',11867,NULL,NULL,0,'2026-06-29 00:36:22'),('161e1b1be24742c3a01b66c10771d4d6','2c2e97aac553494f91f1a0f742bbe387','0b0cfc476d514fbf90899d5d08e34012','你是谁','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[]',5267,NULL,NULL,0,'2026-06-29 00:43:23'),('1a79c71be74740c6add715a4190ed3a9','user123','55e65d0443b944c099669c5bf3b0745f','婚假、产假怎么规定的？','员工依法办理结婚登记的享受婚假3天；女职工生育享受不少于98天产假，难产或多胞胎生育的按国家规定增加；男职工享陪产假15天。','FAQ',0.845154,'[{\"title\": \"FAQ标准答案\", \"doc_id\": null}]',4,NULL,NULL,0,'2026-06-30 13:56:31'),('1c9e14d00e5948c88abf375123b5e4fe','hr001','398772e3768b42bc9b9de92cb9529447','每天几点上班','根据公司制度，标准上班时间为**上午 09:00**。\n\n对于批准实行弹性工作制的岗位，核心工作时间为 10:00—16:00，但员工仍需确保在 09:00 至 18:00 的框架内完成 8 小时标准工作时长。\n\n**引用来源：**\n- [来源1: 考勤制度] 第二章 第五条、第六条','RAG',0.85,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}]',6186,NULL,NULL,0,'2026-06-30 03:24:41'),('28a04c75c1cb4368b515a93084aa90ef','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"...时间\\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准\"}]',4333,NULL,NULL,0,'2026-06-30 03:16:07'),('4e0b3ffd62f14dd18dfbf1f0ea3b767e','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','[{\"document_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"title\": \"考勤制度\", \"snippet\": \"...时间\\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。\\n第六条 弹性工作制：经部门负责人批准，部分岗位可实行弹性工作制，核心工作时间为10:0...\", \"category\": \"考勤制度\", \"version\": \"1.0\"}]','SEARCH',NULL,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\"}]',17,'NOT_HELPFUL',NULL,0,'2026-06-30 02:58:34'),('5298ba88a83344689207b4e27f3cbf12','2c2e97aac553494f91f1a0f742bbe387','9a58fee97b304bc782e54e52137e11d8','我的薪资','🔒 该内容需要HR权限才能查看。如有疑问，请联系HR部门（hr@company.com）','NO_RESULT',0,'[]',2528,NULL,NULL,0,'2026-06-29 01:41:10'),('578d03106fa24304af1a9f944c4754b1','user123','55e65d0443b944c099669c5bf3b0745f','你是谁','我是基于您提供的企业HR制度文档内容提供解答的智能助手。我的知识范围仅限于您当前上传的《薪酬管理制度》、《绩效考核管理制度》和《考勤管理制度》这三份文档。\n\n**引用来源：**\n- 薪酬制度：《薪酬管理制度》（2026年修订版）\n- 绩效制度：《绩效考核管理制度》（2026年修订版）\n- 考勤制度：《考勤管理制度》（2026年修订版）','RAG',0.85,'[{\"title\": \"薪酬制度\", \"doc_id\": \"2a046aad5cfb4948a9cf99c31b2c4511\", \"section\": \"薪酬管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\"}, {\"title\": \"薪酬制度\", \"doc_id\": \"2a046aad5cfb4948a9cf99c31b2c4511\", \"section\": \"薪酬管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}]',6283,NULL,NULL,1,'2026-06-30 13:56:45'),('5a9d21c67cd14e128d2dd5a70f364499','2c2e97aac553494f91f1a0f742bbe387','9b121a8a530f4125bff39f8f8f3b82fe','你是什么模型','🔒 该内容需要HR权限才能查看。如有疑问，请联系HR部门（hr@company.com）','NO_RESULT',0,'[]',5416,NULL,NULL,0,'2026-06-29 01:40:08'),('5bcbad67d0de48a7bc932ae06201854a','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"...时间\\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准\"}]',4102,NULL,NULL,0,'2026-06-30 03:08:17'),('5c45623c3c62496a816fecaff34ee24a','hr001','c4a51bc685f54e318406c1c94284fa64','你可以回答我关于考勤的问题吗','可以。根据我掌握的制度文档，我可以回答您关于 **工作时间、考勤方式、外出/出差登记、迟到/早退/旷工** 等方面的问题。\n\n具体来说，我可以为您解答：\n- **工作时间安排**（如标准工时、弹性工作制的核心时间）\n- **考勤要求**（如打卡方式、每日签到签退时间）\n- **异常情况处理**（如外勤、出差、迟到早退的认定等）\n\n请随时提出您的具体问题。\n\n---\n引用来源：考勤管理制度','RAG',0.85,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"**考勤管理制度**\\n\\n（2026年修订版）\\n\\n# 第一章 总则\\n\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，\"}, {\"title\": \"薪酬制度\", \"doc_id\": \"2a046aad5cfb4948a9cf99c31b2c4511\", \"section\": \"薪酬管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\"}, {\"title\": \"福利制度\", \"doc_id\": \"87d0b8363a47c8ca\", \"section\": \"**员工福利管理制度**\\n\\n（2026年修订版）\\n\\n# 第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定\"}, {\"title\": \"绩效制度\", \"doc_id\": \"73b945e6ca349f8d\", \"section\": \"第十九条 考核组织：人力资源部是绩效考核的归口管理部门，负责制度制定、流程监督、数据汇总和结果应用。\\n\\n第二十条 考核纪律：考核者须遵守公平公正原则，严禁徇私舞弊、打击报复。违反者按公司纪律处分制度处\"}, {\"title\": \"绩效制度\", \"doc_id\": \"73b945e6ca349f8d\", \"section\": \"**绩效考核管理制度**\\n\\n（2026年修订版）\\n\\n# 第一章 总则\\n\\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，\"}]',8140,NULL,NULL,0,'2026-06-30 16:33:53'),('5d93b08775084d6f92fb3697592b441a','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','根据《考勤管理制度》第二章第五条规定，每日工作时间为：上午09:00—12:00，下午13:00—18:00。其中包含午休1小时，每日标准工作时长为8小时。\n\n来源：考勤制度','RAG',0.85,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}]',7744,NULL,NULL,1,'2026-06-30 03:23:44'),('5ded1c9a6163403096fab621e7e1c2b7','2c2e97aac553494f91f1a0f742bbe387','820258db16014427a5e32d91b428a7df','你好','🔒 抱歉，无法确认您在查询哪位员工的信息。请使用明确姓名后重试，例如「张三的工龄是多少」。如需查询自己，请使用「我的…」句式。','NO_RESULT',1,'[]',924,NULL,NULL,0,'2026-06-29 00:30:50'),('6063c1987afb46aebbdaac91a0b16a01','hr001','7b4f8776b92d43289881f552b88378b3','几点上班','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[]',1502,NULL,NULL,0,'2026-06-30 02:58:08'),('631d59f683f04280b4027d98810222c7','hr001','05f856ba8db545ac9a6d575a1fa8bcd2','迟到会有什么处罚？','月累计迟到1-2次给予口头提醒；3-5次每次扣款30元并书面警告；6次及以上视为严重违纪，扣发当月全勤奖并纳入绩效考核负面记录。迟到超过30分钟以上且未说明合理理由的按旷工半天处理。','FAQ',0.912871,'[{\"title\": \"FAQ标准答案\", \"doc_id\": null}]',4,NULL,NULL,1,'2026-06-30 12:39:57'),('653f453fa24841adb7254bbce364712e','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"...时间\\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准\"}]',4186,NULL,NULL,0,'2026-06-30 03:13:13'),('7142966d63814908ad78689ce7d93f11','hr001','f7d8ea9729f04dee9b2cf5eb448fe4d6','薪资多少','根据提供的文档，无法给出一个固定的“薪资多少”的确切数字，因为薪资由多个浮动部分组成。文档中仅明确了以下具体金额标准：\n\n- **学历工资**：大专300元/月，本科500元/月，硕士800元/月，博士1200元/月。\n- **工龄工资**：每年增加50元/月，上限500元/月。\n- **通讯补贴**：普通员工100元/月，主管级200元/月，经理级300元/月。\n- **交通补贴**：300元/月（统一标准）。\n- **餐补**：20元/工作日出勤日。\n\n其他薪酬组成部分如**岗位工资、绩效工资**及**年终奖金**，文档仅说明了计算原则或占比范围，未列明具体金额，因此无法提供完整的薪资数额。\n\n**引用来源**：薪酬管理制度','RAG',0.85,'[{\"title\": \"薪酬制度\", \"doc_id\": \"2a046aad5cfb4948a9cf99c31b2c4511\", \"section\": \"薪酬管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\"}, {\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"第一章 总则\\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，特制定本制度。\\n第二条 适用范围：本制度适用于公司全体正式\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}]',14101,NULL,NULL,1,'2026-06-30 12:28:47'),('730461c8c2784aa8a6f032e85410cca6','hr001','3da44d83b2ac4ba09bc9d28ec631b919','薪资多少','根据您提供的制度文档内容，无法回答“薪资多少”的问题。\n\n所提供的文档包括《员工福利管理制度》、《考勤管理制度》和《绩效考核管理制度》，这些文档主要规定了福利保障、工作时间、考勤纪律和绩效考核方式。其中虽然提到了社保公积金缴费基数、绩效作为“调薪的主要依据”等信息，但**完全没有包含任何关于具体薪资数额、薪资等级或薪资结构的说明**。\n\n如需了解具体薪资信息，建议查阅公司的《薪酬管理制度》或直接咨询人力资源部。\n\n---\n- **引用来源**：[来源1: 福利制度]、[来源2: 考勤制度]、[来源3: 绩效制度]、[来源4: 绩效制度]','RAG',0.85,'[{\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"第一章 总则\\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，特制定本制度。\\n第二条 适用范围：本制度适用于公司全体正式\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}]',9592,NULL,NULL,0,'2026-06-30 03:28:45'),('7ee68670b54c4fce91f13c687f86bb9a','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"...时间\\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准\"}]',8296,NULL,NULL,0,'2026-06-30 03:21:39'),('84532418d3ac40c8be9327bb28a72157','2c2e97aac553494f91f1a0f742bbe387','501e7c158c7b4037977f5bb43ba4b814','我的薪资','根据您提供的制度文档，其中并未包含关于薪资结构、工资标准、调薪机制、薪酬计算等直接描述“薪资”的条款。文档仅涉及：\n\n- 《员工福利管理制度》：法定社保、公积金、补充商业保险、带薪假期等福利性内容，但不涉及薪资发放标准。\n- 《考勤管理制度》：工作时间、考勤方式及迟到早退旷工等规定，可能影响工资扣款，但未给出具体薪资数值或计算规则。\n- 《绩效考核管理制度》：考核周期、维度和指标，指出年度考核结果将作为“年终奖、晋升、调薪的主要依据”，但同样未说明薪资具体构成或金额。\n\n因此，基于现有文档，**无法回答您关于“我的薪资”的具体问题**。建议您参考公司的《薪酬管理制度》或向人力资源部咨询个人薪资详情。\n\n引用来源：\n- 《员工福利管理制度》（2026年修订版）\n- 《考勤管理制度》（2026年修订版）\n- 《绩效考核管理制度》（2026年修订版）','RAG',0.85,'[{\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"第一章 总则\\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，特制定本制度。\\n第二条 适用范围：本制度适用于公司全体正式\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}]',37244,NULL,NULL,0,'2026-06-30 12:11:28'),('8fd1e1cb5bc24e6ea8e61ac538513edc','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"...时间\\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准\"}]',501,NULL,NULL,0,'2026-06-30 03:16:46'),('91f3ae9dd15546edb3092dd2821d509e','2c2e97aac553494f91f1a0f742bbe387','9a58fee97b304bc782e54e52137e11d8','我的职位是什么','🔒 该内容需要HR权限才能查看。如有疑问，请联系HR部门（hr@company.com）','NO_RESULT',0,'[]',2936,NULL,NULL,0,'2026-06-29 01:41:29'),('9202c4b6b0b34d698abed758a28f8a58','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"...时间\\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准\"}]',643,NULL,NULL,0,'2026-06-30 03:19:58'),('9ec7f44f24214b3eac622e1df0e9c589','hr001','3da44d83b2ac4ba09bc9d28ec631b919','薪资多少','根据提供的文档内容，无法直接给出具体的“薪资多少”数额，因为最终薪资取决于个人的学历、工龄、所在岗位、绩效表现等多种因素。\n\n但根据**《薪酬管理制度》**，员工薪资结构由以下部分构成：\n\n1.  **基本工资**：包含根据个人情况确定的学历工资和工龄工资。\n    *   **学历工资**：大专300元/月，本科500元/月，硕士800元/月，博士1200元/月。\n    *   **工龄工资**：每年增加50元/月，上限500元/月。\n2.  **岗位工资**：根据所在岗位的职级（P1-P10共十个级别）确定，具体金额未在文档中列出。\n3.  **绩效工资**：浮动薪酬，一般员工占总薪酬的20%-30%，管理层占30%-50%。\n4.  **津贴补贴**：包含固定金额的通讯补贴、交通补贴、餐补等。\n    *   **通讯补贴**：普通员工100元/月，主管级200元/月，经理级300元/月。\n    *   **交通补贴**：300元/月。\n    *   **餐补**：20元/工作日出勤日。\n5.  **奖金**：包含年终奖金等，年终奖金与公司年度经营效益和个人年度绩效考核结果挂钩。\n\n综上所述，要确定您的具体薪资，需结合您应聘的岗位职级、您的个人学历工龄信息，以及公司和个人的绩效考核结果综合计算。\n\n引用来源：[来源1: 薪酬制度]','RAG',0.85,'[{\"title\": \"薪酬制度\", \"doc_id\": \"2a046aad5cfb4948a9cf99c31b2c4511\", \"section\": \"薪酬管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\"}, {\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"第一章 总则\\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，特制定本制度。\\n第二条 适用范围：本制度适用于公司全体正式\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}]',9875,NULL,NULL,0,'2026-06-30 03:29:48'),('a110f3a8fee84d79898374270cf22c26','2c2e97aac553494f91f1a0f742bbe387','9a58fee97b304bc782e54e52137e11d8','年假有多少天','根据公司《休假制度》规定，您的年假天数为：\n- 工龄1-3年：5天\n- 工龄3-10年：10天\n- 工龄10年以上：15天\n\n您当前工龄0年，年假为5天。','RULE',0.9,'[]',642,'NOT_HELPFUL',NULL,1,'2026-06-29 01:39:45'),('aa99ef19ff714ac3928b0d8c57172c3f','2c2e97aac553494f91f1a0f742bbe387','535aa35c467e4bebbac9af65a88a4178','你是谁','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[]',2656,NULL,NULL,0,'2026-06-29 00:47:55'),('b1a754be40b14883b607d532d87b14e4','user123','793d6b28028842ea88e0ecf544feb372','上下班时间','根据《考勤管理制度》（2026年修订版）第二章的规定，公司上下班时间分为两种情况：\n\n1. **标准工时制**：工作时间为上午09:00—12:00，下午13:00—18:00（含午休1小时）。\n2. **弹性工作制**：经部门负责人批准的部分岗位，核心工作时间为10:00—16:00，其余时间可自主安排。\n\n引用来源：《考勤管理制度》（2026年修订版）第五条、第六条。','RAG',0.85,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}]',5240,NULL,NULL,0,'2026-06-30 13:57:45'),('bad85f0d95524cd1a3ac99cea7ded1f3','2c2e97aac553494f91f1a0f742bbe387','cb62aa4f90814cd9be6aaf0202ddb763','你是谁','🔒 抱歉，无法确认您在查询哪位员工的信息。请使用明确姓名后重试，例如「张三的工龄是多少」。如需查询自己，请使用「我的…」句式。','NO_RESULT',1,'[]',7619,NULL,NULL,0,'2026-06-29 00:40:00'),('c0303b14baf74c1ea90ac6970ce9420a','user123','e5d0aaf71644412fa9a10e9c7128ec9c','薪资多少','根据提供的制度文档，无法给出一个固定的“薪资”数额，因为员工薪资是根据多个组成部分综合计算的。薪酬结构由以下五部分构成，部分有明确标准，部分则根据岗位和个人情况浮动：\n\n**一、有具体金额标准的薪酬部分**\n\n*   **基本工资（部分固定）**：\n    *   **学历工资**：大专300元/月，本科500元/月，硕士800元/月，博士1200元/月。\n    *   **工龄工资**：每年增加50元/月，上限500元/月。\n*   **津贴补贴（部分固定）**：\n    *   **通讯补贴**：普通员工100元/月，主管级200元/月，经理级300元/月。\n    *   **交通补贴**：统一标准300元/月。\n    *   **餐补**：20元/工作日出勤日。\n    *   **高温补贴**：每年6-9月，按国家规定标准发放。\n    *   **项目现场津贴**：外派项目现场人员，按项目地标准给予补贴。\n\n**二、浮动或无具体金额标准的薪酬部分**\n\n*   **岗位工资**：根据员工所在岗位的职级（P1—P10）确定，文档未列出每个职级对应的具体金额。\n*   **绩效工资**：根据月度/年度绩效考核结果核发的浮动薪酬。文档未给出具体金额，仅说明一般员工绩效工资占比为总薪酬的20%—30%，管理层占比为30%—50%。\n*   **奖金**：年终奖金根据公司年度经营效益和个人年度绩效考核结果发放，文档内容不完整，未给出具体计算标准。\n\n综上，您个人的具体薪资数额需结合您的学历、工龄、职级、绩效考核结果等多方面因素，依据上述规则计算得出。\n\n---\n**引用来源**：[来源1: 薪酬制度] - 《薪酬管理制度》（2026年修订版）第四条、第五条、第六条、第七条、第八条、第九条','RAG',0.85,'[{\"title\": \"薪酬制度\", \"doc_id\": \"2a046aad5cfb4948a9cf99c31b2c4511\", \"section\": \"薪酬管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\"}, {\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"第一章 总则\\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，特制定本制度。\\n第二条 适用范围：本制度适用于公司全体正式\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}]',18667,NULL,NULL,0,'2026-06-30 13:23:41'),('c38413f513e842e5a584288c1e738bbd','2c2e97aac553494f91f1a0f742bbe387','653f2eaf1a86404a9e35386e979a577d','年假有几天','根据公司《休假制度》规定，您的年假天数为：\n- 工龄1-3年：5天\n- 工龄3-10年：10天\n- 工龄10年以上：15天\n\n您当前工龄0年，年假为5天。','RULE',0.9,'[]',987,NULL,NULL,0,'2026-06-29 01:26:32'),('c9d3048999a14b8bbe004aaf254dc979','user123','db62566162974004a8acceca7aa03e6f','你是谁','我是基于您提供的企业HR制度文档为您提供查询和解答的智能助手。我的知识范围仅限于这些文档中所包含的信息，包括薪酬管理、绩效考核及考勤管理等相关制度内容。\n\n*来源：薪酬制度、绩效制度、考勤管理制度*','RAG',0.85,'[{\"title\": \"薪酬制度\", \"doc_id\": \"2a046aad5cfb4948a9cf99c31b2c4511\", \"section\": \"薪酬管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\"}, {\"title\": \"薪酬制度\", \"doc_id\": \"2a046aad5cfb4948a9cf99c31b2c4511\", \"section\": \"薪酬管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}]',5056,NULL,NULL,0,'2026-06-30 13:57:15'),('e0fb13948b814876b2a384b4280430bf','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"...时间\\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准\"}]',399,NULL,NULL,0,'2026-06-30 03:02:54'),('e84374687e9e4aeda12dbfd18b4be935','hr001','7b4f8776b92d43289881f552b88378b3','每日工作时间','未找到相关制度，建议联系HR部门获取帮助。','NO_RESULT',NULL,'[{\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"...时间\\n第四条 标准工时制：公司实行每周五天工作制，周一至周五为工作日，周六、周日为休息日。\\n第五条 每日工作时间：上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准\"}]',3584,NULL,NULL,0,'2026-06-30 03:02:42'),('e999abb6361d43728cca5cbd2101b9ef','hr001','3da44d83b2ac4ba09bc9d28ec631b919','薪资多少','根据您提供的制度文档，无法给出一个具体的“薪资多少”的固定数字。员工的薪酬是由多个部分组成的，具体数额因人而异。\n\n根据《薪酬管理制度》的规定，您的薪资主要由以下部分构成：\n\n*   **基本工资**：这是相对固定的部分，包括：\n    *   **学历工资**：大专300元/月，本科500元/月，硕士800元/月，博士1200元/月。\n    *   **工龄工资**：每年增加50元/月，上限为500元/月。\n*   **岗位工资**：根据您所在岗位的职级（P1-P10）来确定，文档未列出每个职级的具体金额。\n*   **绩效工资**：这是一项浮动薪酬，根据您的月度/年度绩效考核结果发放，一般员工占比为总薪酬的20%—30%。\n*   **津贴补贴**：包括但不限于：\n    *   通讯补贴：普通员工100元/月。\n    *   交通补贴：300元/月（统一标准）。\n    *   餐补：20元/每个出勤日。\n    *   高温补贴：每年6-9月按国家规定发放。\n*   **奖金**：例如根据公司效益和个人绩效核发的年终奖金。\n\n由于您的薪资与您的**学历、工龄、所在岗位职级、绩效考核结果**等多种因素相关，仅凭“薪资多少”这一问题无法计算出准确数字。建议您结合自身情况，对照上述构成部分进行估算。\n\n---\n引用来源：\n[来源1: 薪酬制度] 薪酬管理制度','RAG',0.85,'[{\"title\": \"薪酬制度\", \"doc_id\": \"2a046aad5cfb4948a9cf99c31b2c4511\", \"section\": \"薪酬管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为建立科学合理的薪酬体系，充分体现按劳分配、效率优先、兼顾公平的原则，吸引、保留和激励优秀人才，促进公司战略目标的实现，特制定本制度。\"}, {\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"第一章 总则\\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，特制定本制度。\\n第二条 适用范围：本制度适用于公司全体正式\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}]',17985,NULL,NULL,1,'2026-06-30 12:30:01'),('e9eda995d11544e1ac34369fcdd55e16','hr001','3da44d83b2ac4ba09bc9d28ec631b919','绩效制度是什么','根据提供的文档内容，绩效制度是指《绩效考核管理制度（2026年修订版）》。该制度旨在建立科学、公正、透明的绩效考核体系，以全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现。该制度适用于公司全体正式员工，并遵循结果导向、客观公正、公开透明、持续改进和分层分类的原则。在考核内容上，制度规定了月度、季度和年度的考核周期，以及包含工作业绩（权重70%）、工作能力（20%）和工作态度（10%）的考核维度。在指标体系方面，制度要求基于SMART原则设定关键绩效指标（KPI），并分别针对普通员工和管理者规定了具体的KPI指标项。\n\n引用来源：绩效考核管理制度（2026年修订版）','RAG',0.85,'[{\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"绩效考核管理制度\\n（2026年修订版）\"}, {\"title\": \"绩效制度\", \"doc_id\": \"f56c26f55490432e98cb3696399c3f8c\", \"section\": \"第一章 总则\\n第一条 目的：为建立科学、公正、透明的绩效考核体系，全面客观地评价员工工作业绩和表现，激励员工持续改进，促进公司战略目标的实现，特制定本制度。\\n第二条 适用范围：本制度适用于公司全体正式\"}, {\"title\": \"考勤制度\", \"doc_id\": \"7ab9fe6efcb24b4e9d9c77a9c5a1f027\", \"section\": \"考勤管理制度\\n（2026年修订版）\\n\\n第一章 总则\\n第一条 目的：为规范公司员工考勤管理，严肃工作纪律，保障公司正常运营秩序，提高工作效率，根据《中华人民共和国劳动法》及相关法律法规，结合本公司实际情\"}, {\"title\": \"福利制度\", \"doc_id\": \"d5fa6f616fda49bab22fc338d36f502a\", \"section\": \"员工福利管理制度\\n\\n（2026年修订版）\\n\\n第一章 总则\\n\\n第一条 目的：为建立完善的员工福利保障体系，提升员工归属感和满意度，吸引和留住优秀人才，根据国家相关法律法规，结合公司实际，制定本制度。\\n\\n\"}]',7639,NULL,NULL,0,'2026-06-30 03:27:51'),('ee44057d86614d90bd6f97f4431448f8','user123','55e65d0443b944c099669c5bf3b0745f','如何申请加班？','加班须提前填写《加班申请单》，经部门负责人审批后报人力资源部备案，未经审批的不视为加班。平时延长工作时间按150%支付加班工资，休息日加班按200%支付（或安排调休），法定节假日按300%支付。','FAQ',0.866025,'[{\"title\": \"FAQ标准答案\", \"doc_id\": null}]',820,NULL,NULL,0,'2026-06-30 13:56:15'),('f7668474a27e40a1bc31e6c36301f232','hr001','f7d8ea9729f04dee9b2cf5eb448fe4d6','每天的上下班时间','公司实行标准工时制，每日工作时间为上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。部分岗位经部门负责人批准可实行弹性工作制，核心工作时间为10:00—16:00。','FAQ',0.755929,'[{\"title\": \"FAQ标准答案\", \"doc_id\": null}]',825,NULL,NULL,1,'2026-06-30 03:33:29'),('f7f9b9095db14c31b76e16c6aafd309b','hr001','f7d8ea9729f04dee9b2cf5eb448fe4d6','每天的上下班时间','公司实行标准工时制，每日工作时间为上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。部分岗位经部门负责人批准可实行弹性工作制，核心工作时间为10:00—16:00。','FAQ',0.755929,'[{\"title\": \"FAQ标准答案\", \"doc_id\": null}]',7,NULL,NULL,0,'2026-06-30 12:28:24');
/*!40000 ALTER TABLE `qa_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `employee_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('EMPLOYEE','HR_SPECIALIST','ADMIN') COLLATE utf8mb4_unicode_ci NOT NULL,
  `department_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `job_level` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `hire_date` date NOT NULL,
  `work_location` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `marital_status` enum('SINGLE','MARRIED') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('ACTIVE','DISABLED') COLLATE utf8mb4_unicode_ci NOT NULL,
  `login_attempts` int DEFAULT NULL,
  `locked_until` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `ix_users_employee_id` (`employee_id`),
  KEY `department_id` (`department_id`),
  KEY `ix_users_email` (`email`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('2c2e97aac553494f91f1a0f742bbe387','1234','哈哈哈',NULL,NULL,'$2b$12$U/cW1NyV3nA/JFxbur5wQuz2SNFngCBsBmvdtqBsNwuMA99V.g74e','EMPLOYEE','dept-002',NULL,'2026-06-29',NULL,NULL,'ACTIVE',0,NULL,'2026-06-29 00:08:27','2026-07-01 00:40:43'),('hr001','HR001','张HR','hr@company.com','13800000001','$2b$12$IlEBGdtiluBEo.SQEaw.Oem4hwRrogY0Yg9CgAzMfvuaZcuH5Ic/S','HR_SPECIALIST','root','M2','2024-03-01','总部','MARRIED','ACTIVE',0,NULL,NULL,'2026-06-30 02:33:03'),('user-admin-001','admin001','系统管理员','admin@company.com',NULL,'$2b$12$zzuv0xJuwBPysautmhBv9etU03pYXPb/dCUib67SD08RPA2cWH56O','ADMIN','dept-004',NULL,'2020-01-01',NULL,NULL,'ACTIVE',0,NULL,NULL,'2026-06-26 00:31:02'),('user123','123','测试用户',NULL,NULL,'$2b$12$hSlAhczG0vrt4WMUAmeiI.2P3MppnF0CBOvFIrbR.KjIcNVpYAk22','ADMIN','root',NULL,'2024-01-01','总部',NULL,'ACTIVE',0,NULL,NULL,'2026-06-30 12:26:53');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'hr_policy_qa'
--

--
-- Dumping routines for database 'hr_policy_qa'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-01  9:18:48
