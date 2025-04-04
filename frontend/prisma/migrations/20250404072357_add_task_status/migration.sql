/*
  Warnings:

  - Added the required column `status` to the `Task` table without a default value. This is not possible if the table is not empty.

*/
-- CreateEnum
CREATE TYPE "Status" AS ENUM ('running', 'complete', 'error');

-- AlterTable
ALTER TABLE "Task" ADD COLUMN     "status" "Status" NOT NULL;
