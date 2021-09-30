-- MySQL dump 10.14  Distrib 5.5.68-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: dev_paas
-- ------------------------------------------------------
-- Server version	5.5.68-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `esb_component_system`
--

DROP TABLE IF EXISTS `esb_component_system`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `esb_component_system` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `label` varchar(128) NOT NULL,
  `component_admin` varchar(128) NOT NULL,
  `interface_admin` varchar(128) NOT NULL,
  `system_link` varchar(1024) NOT NULL,
  `belong_to` varchar(128) NOT NULL,
  `remark` longtext NOT NULL,
  `execute_timeout` int(11) DEFAULT NULL,
  `query_timeout` int(11) DEFAULT NULL,
  `doc_category_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `esb_component_system`
--

LOCK TABLES `esb_component_system` WRITE;
/*!40000 ALTER TABLE `esb_component_system` DISABLE KEYS */;
INSERT INTO `esb_component_system` VALUES (1,'BK_LOGIN','蓝鲸统一登录','','','','','',NULL,NULL,NULL),(2,'CC','蓝鲸配置平台','','','','','',NULL,NULL,NULL),(3,'GSE','蓝鲸管控平台','','','','','',NULL,NULL,NULL),(4,'JOB','蓝鲸作业平台','','','','','',NULL,NULL,NULL),(5,'CMSI','蓝鲸消息管理','','','','','',NULL,NULL,NULL),(6,'SOPS','标准运维','','','','','',NULL,NULL,NULL),(7,'CMDB','我买云资源平台','','admin','','','',NULL,NULL,3),(8,'CONTROL','我买云管控平台','','admin','','','',NULL,NULL,3),(9,'WORKBENCH','我买云工作台','','guoyuchen','','','',30,30,3),(10,'TASK','我买云作业平台','','','','','',NULL,NULL,3),(11,'rbac','我买云企业管理后台','','zhangyusheng','','','',NULL,NULL,3),(12,'MONITOR','监控平台','','guoyuchen','','','',30,30,3),(13,'CMP','我买云云管平台','','','','','',NULL,NULL,3),(14,'DEVOPS','我买云应用平台','','huxingqi','','','',NULL,NULL,3),(15,'BASTION','堡垒机','','huxingqi','','','',NULL,NULL,3);
/*!40000 ALTER TABLE `esb_component_system` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-09-23 16:44:14
