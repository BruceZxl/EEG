/*
 Navicat Premium Data Transfer

 Source Server         : 11
 Source Server Type    : MySQL
 Source Server Version : 50726
 Source Host           : localhost:3306
 Source Schema         : sql_software

 Target Server Type    : MySQL
 Target Server Version : 50726
 File Encoding         : 65001

 Date: 06/03/2024 16:59:21
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tb_auto_anlysis_para
-- ----------------------------
DROP TABLE IF EXISTS `tb_auto_anlysis_para`;
CREATE TABLE `tb_auto_anlysis_para`  (
  `type_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '分类名称',
  `type_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '分类代码',
  `sub_type_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '子类名称',
  `sub_type_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '子类代码',
  `para_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '参数名称',
  `para_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '参数代码',
  `unit` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '单位',
  `default_value` decimal(8, 4) DEFAULT NULL COMMENT '缺省值',
  PRIMARY KEY (`type_cd`, `sub_type_cd`, `para_cd`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_awake_rec
-- ----------------------------
DROP TABLE IF EXISTS `tb_awake_rec`;
CREATE TABLE `tb_awake_rec`  (
  `Patient_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '病人姓名',
  `Patient_ID` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '病人ID',
  `seq_no` smallint(6) NOT NULL COMMENT '编号',
  `event_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件名称',
  `event_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件代码',
  `start_tm` datetime DEFAULT NULL COMMENT '开始时间',
  `end_tm` datetime DEFAULT NULL COMMENT '结束时间',
  `Mean_value` decimal(10, 4) DEFAULT NULL COMMENT '平均值',
  PRIMARY KEY (`Patient_ID`, `seq_no`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_body_movement_rec
-- ----------------------------
DROP TABLE IF EXISTS `tb_body_movement_rec`;
CREATE TABLE `tb_body_movement_rec`  (
  `Patient_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '病人姓名',
  `Patient_ID` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '病人ID',
  `seq_no` smallint(6) NOT NULL COMMENT '编号',
  `event_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件名称',
  `event_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件代码',
  `start_tm` datetime DEFAULT NULL COMMENT '开始时间',
  `end_tm` datetime DEFAULT NULL COMMENT '结束时间',
  `Mean_value` decimal(10, 4) DEFAULT NULL COMMENT '平均值',
  PRIMARY KEY (`Patient_ID`, `seq_no`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_breathe_event_rec
-- ----------------------------
DROP TABLE IF EXISTS `tb_breathe_event_rec`;
CREATE TABLE `tb_breathe_event_rec`  (
  `Patient_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '病人姓名',
  `Patient_ID` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '病人id',
  `seq_no` smallint(6) NOT NULL COMMENT '编号',
  `event_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件名称',
  `event_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件代码',
  `start_tm` datetime DEFAULT NULL COMMENT '开始时间',
  `end_tm` datetime DEFAULT NULL COMMENT '结束时间',
  PRIMARY KEY (`Patient_ID`, `seq_no`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_chan_para
-- ----------------------------
DROP TABLE IF EXISTS `tb_chan_para`;
CREATE TABLE `tb_chan_para`  (
  `Patient_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '病人姓名',
  `Patient_ID` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '病人ID',
  `Electrode_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '电极名称',
  `Polarity` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '变量极性',
  `Ref` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '参考电极',
  `Grid_spacing` decimal(6, 4) DEFAULT NULL COMMENT '栅格间隔',
  `size` decimal(6, 4) DEFAULT NULL COMMENT '尺寸',
  `colour` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '颜色',
  `Frequency_reduction` char(4) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '降频（斩波）',
  `zoom` decimal(8, 4) DEFAULT NULL COMMENT '缩放',
  `Bipolar_polarity` char(4) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '双极极性',
  `High_filtering` decimal(8, 4) DEFAULT NULL COMMENT '高通滤波',
  `Low_filtering` decimal(8, 4) DEFAULT NULL COMMENT '低通滤波',
  `power_frequency` char(4) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '工频',
  `Auto_ruler` char(4) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '自动标尺',
  `Signal_offset_corr` char(4) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '信号偏移矫正',
  `Waveform_conversion` char(4) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '波形转换',
  PRIMARY KEY (`Patient_ID`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_heart_rate_rec
-- ----------------------------
DROP TABLE IF EXISTS `tb_heart_rate_rec`;
CREATE TABLE `tb_heart_rate_rec`  (
  `Patient_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '病人姓名',
  `Patient_ID` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '病人ID',
  `seq_no` smallint(6) NOT NULL COMMENT '编号',
  `event_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件名称',
  `event_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件代码',
  `start_tm` datetime DEFAULT NULL COMMENT '开始时间',
  `end_tm` datetime DEFAULT NULL COMMENT '结束时间',
  `Max_value` decimal(10, 4) DEFAULT NULL COMMENT '最大值',
  `Min_value` decimal(10, 4) DEFAULT NULL COMMENT '最小值',
  `Mean_value` decimal(10, 4) DEFAULT NULL COMMENT '平均值',
  PRIMARY KEY (`Patient_ID`, `seq_no`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_sleep_stage_rec
-- ----------------------------
DROP TABLE IF EXISTS `tb_sleep_stage_rec`;
CREATE TABLE `tb_sleep_stage_rec`  (
  `Patient_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '病人姓名',
  `Patient_ID` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '病人ID',
  `Sleep_staging_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '睡眠分期名称',
  `Sleep_staging_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '睡眠分期代码',
  `seq_no` smallint(6) NOT NULL COMMENT '编号 每个病人编号从1开始，每段分期顺序增加，直到最后',
  `start_tm` datetime DEFAULT NULL COMMENT '开始时间 YYYY-MM-DD hh-mm-ss',
  `end_tm` datetime DEFAULT NULL COMMENT '结束时间 YYYY-MM-DD hh-mm-ss',
  `Duration` decimal(10, 4) DEFAULT NULL COMMENT '持续时间 单位：秒',
  `sleep_latency` decimal(10, 4) DEFAULT NULL COMMENT '睡眠潜伏期 单位：秒',
  `Sleep_Duration` decimal(10, 4) DEFAULT NULL COMMENT '睡眠时间 单位：秒',
  PRIMARY KEY (`Patient_ID`, `Sleep_staging_cd`, `seq_no`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_snore_rec
-- ----------------------------
DROP TABLE IF EXISTS `tb_snore_rec`;
CREATE TABLE `tb_snore_rec`  (
  `Patient_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '病人姓名',
  `Patient_ID` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '病人ID',
  `seq_no` smallint(6) NOT NULL COMMENT '编号',
  `event_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件名称',
  `event_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件代码',
  `start_tm` datetime DEFAULT NULL COMMENT '开始时间',
  `end_tm` datetime DEFAULT NULL COMMENT '结束时间',
  `Mean_value` decimal(10, 4) DEFAULT NULL COMMENT '平均值',
  PRIMARY KEY (`Patient_ID`, `seq_no`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tb_spo2_rec
-- ----------------------------
DROP TABLE IF EXISTS `tb_spo2_rec`;
CREATE TABLE `tb_spo2_rec`  (
  `Patient_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '病人姓名',
  `Patient_ID` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '病人ID',
  `seq_no` smallint(6) NOT NULL COMMENT '编号',
  `event_nm` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件名称 ',
  `event_cd` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '事件代码',
  `start_tm` datetime DEFAULT NULL COMMENT '开始时间',
  `end_tm` datetime DEFAULT NULL COMMENT '结束时间',
  `Max_value` decimal(10, 4) DEFAULT NULL COMMENT '最大值',
  `Min_value` decimal(10, 4) DEFAULT NULL COMMENT '最小值',
  `Mean_value` decimal(10, 4) DEFAULT NULL COMMENT '平均值',
  PRIMARY KEY (`Patient_ID`, `seq_no`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8 COLLATE = utf8_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
