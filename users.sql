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

 Date: 03/02/2024 16:15:38
*/


-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS "public"."users";
CREATE TABLE "public"."users" (
  "id" int8 NOT NULL DEFAULT nextval('id_auto_seq'::regclass),
  "first_name" varchar(255) COLLATE "pg_catalog"."default",
  "last_name" varchar(255) COLLATE "pg_catalog"."default",
  "type" varchar(255) COLLATE "pg_catalog"."default",
  "tele_id" varchar(255) COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "public"."users" OWNER TO "whm_db";

-- ----------------------------
-- Primary Key structure for table users
-- ----------------------------
ALTER TABLE "public"."users" ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");
