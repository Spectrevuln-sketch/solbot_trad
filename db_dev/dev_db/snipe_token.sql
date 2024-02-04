/*
 Navicat Premium Data Transfer

 Source Server         : WHM DB
 Source Server Type    : PostgreSQL
 Source Server Version : 130012 (130012)
 Source Host           : localhost:5445
 Source Catalog        : solana_sniper
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 130012 (130012)
 File Encoding         : 65001

 Date: 03/02/2024 16:14:48
*/


-- ----------------------------
-- Table structure for snipe_token
-- ----------------------------
DROP TABLE IF EXISTS "public"."snipe_token";
CREATE TABLE "public"."snipe_token" (
  "id" int8 NOT NULL DEFAULT nextval('id_auto'::regclass),
  "payer_wallet" varchar(255) COLLATE "pg_catalog"."default",
  "amount_buy" varchar(255) COLLATE "pg_catalog"."default",
  "token_pub" varchar(255) COLLATE "pg_catalog"."default",
  "tele_id" varchar(255) COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "public"."snipe_token" OWNER TO "whm_db";

-- ----------------------------
-- Primary Key structure for table snipe_token
-- ----------------------------
ALTER TABLE "public"."snipe_token" ADD CONSTRAINT "snipe_token_pkey" PRIMARY KEY ("id");
