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

 Date: 03/02/2024 16:15:50
*/


-- ----------------------------
-- Table structure for wallet
-- ----------------------------
DROP TABLE IF EXISTS "public"."wallet";
CREATE TABLE "public"."wallet" (
  "id" int8 NOT NULL DEFAULT nextval('id_auto'::regclass),
  "tele_id" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "private_key" text COLLATE "pg_catalog"."default",
  "public_key" text COLLATE "pg_catalog"."default",
  "is_connected" bool,
  "is_snipe" bool,
  "balance" varchar(255) COLLATE "pg_catalog"."default",
  "default" bool
)
;
ALTER TABLE "public"."wallet" OWNER TO "whm_db";

-- ----------------------------
-- Primary Key structure for table wallet
-- ----------------------------
ALTER TABLE "public"."wallet" ADD CONSTRAINT "wallet_pkey" PRIMARY KEY ("id");
