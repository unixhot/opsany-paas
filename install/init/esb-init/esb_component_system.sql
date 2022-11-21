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
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `esb_component_system`
--

LOCK TABLES `esb_component_system` WRITE;
/*!40000 ALTER TABLE `esb_component_system` DISABLE KEYS */;
INSERT INTO `esb_component_system` VALUES (1,'BK_LOGIN','统一登录','','admin','','','',NULL,NULL,NULL),(2,'CC','配置平台','','admin','','','',NULL,NULL,NULL),(3,'GSE','管控平台','','admin','','','',NULL,NULL,NULL),(4,'JOB','作业平台','','admin','','','',NULL,NULL,NULL),(5,'CMSI','消息管理','','admin','','','',NULL,NULL,NULL),(6,'SOPS','标准运维','','admin','','','',NULL,NULL,NULL),(7,'CMDB','OpsAny 资源平台','','admin','','','',NULL,NULL,3),(8,'CONTROL','OpsAny 管控平台','','admin','','','',NULL,NULL,3),(9,'WORKBENCH','OpsAny 工作台','','admin','','','',30,30,3),(10,'TASK','OpsAny 作业平台','','admin','','','',NULL,NULL,3),(11,'rbac','OpsAny 企业管理后台','','admin','','','',NULL,NULL,3),(12,'MONITOR','OpsAny 监控平台','','admin','','','',30,30,3),(13,'CMP','OpsAny 云管平台','','admin','','','',NULL,NULL,3),(14,'DEVOPS','OpsAny 应用平台','','admin','','','',NULL,NULL,3),(15,'BASTION','OpsAny 堡垒机','','admin','','','',NULL,NULL,3),(16,'PROM','OpsAny 应用监控','','admin','','','',NULL,NULL,3),(17,'AUTO','OpsAny 智能巡检','','admin','','','',NULL,NULL,4),(18,'K8S','OpsAny 容器平台','','admin','','','',NULL,NULL,4),(19,'EVENT','OpsAny 事件中心','','admin','','','',NULL,NULL,4),(20,'DASHBOARD','OpsAny 可视化大屏','','admin','','','',NULL,NULL,4);
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

-- Dump completed on 2022-11-15 18:14:07
