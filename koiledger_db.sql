-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 13, 2026 at 03:10 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `koiledger_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `auctions`
--

CREATE TABLE `auctions` (
  `auction_id` int(11) NOT NULL,
  `koi_id` int(11) DEFAULT NULL,
  `auction_house` varchar(100) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `final_price` decimal(10,2) DEFAULT NULL,
  `winner_org_id` int(11) DEFAULT NULL,
  `xrpl_tx` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auctions`
--

INSERT INTO `auctions` (`auction_id`, `koi_id`, `auction_house`, `start_date`, `end_date`, `final_price`, `winner_org_id`, `xrpl_tx`) VALUES
(1, 2, 'Sakura Auctions', '2024-06-01', '2024-06-10', 1500.00, 3, 'AUCTX001');

-- --------------------------------------------------------

--
-- Table structure for table `certificates`
--

CREATE TABLE `certificates` (
  `certificate_id` int(11) NOT NULL,
  `koi_id` int(11) DEFAULT NULL,
  `certificate_type` enum('ORIGIN','HEALTH','EXPORT') DEFAULT NULL,
  `issued_by` varchar(100) DEFAULT NULL,
  `issue_date` date DEFAULT NULL,
  `document_path` varchar(255) DEFAULT NULL,
  `xrpl_tx` varchar(200) DEFAULT NULL,
  `date_created` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `certificates`
--

INSERT INTO `certificates` (`certificate_id`, `koi_id`, `certificate_type`, `issued_by`, `issue_date`, `document_path`, `xrpl_tx`, `date_created`) VALUES
(1, 1, 'ORIGIN', 'Tanaka Koi Farm', '2023-04-01', '/docs/cert_koi_1.pdf', 'CERTTX001', '2023-04-01 12:48:50'),
(2, 2, 'HEALTH', 'Niigata Vet Center', '2024-03-06', '/docs/cert_koi_2.pdf', 'CERTTX002', '2024-03-06 12:48:50');

-- --------------------------------------------------------

--
-- Table structure for table `farms`
--

CREATE TABLE `farms` (
  `farm_id` int(11) NOT NULL,
  `farm_code` varchar(10) DEFAULT NULL,
  `farm_name` varchar(100) DEFAULT NULL,
  `country_code` varchar(3) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `contact_email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `fish_types`
--

CREATE TABLE `fish_types` (
  `type_code` varchar(10) NOT NULL,
  `type_name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `koi`
--

CREATE TABLE `koi` (
  `koi_id` int(11) NOT NULL,
  `org_id` int(11) DEFAULT NULL,
  `koi_code` varchar(50) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `variety` varchar(50) DEFAULT NULL,
  `gender` enum('MALE','FEMALE','UNKNOWN') DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `breeder_name` varchar(120) DEFAULT NULL,
  `size_cm` decimal(5,2) DEFAULT NULL,
  `weight_kg` decimal(6,2) DEFAULT NULL,
  `body_type` enum('LONG','SHORT','STANDARD') DEFAULT NULL,
  `skin_quality` enum('EXCELLENT','GOOD','AVERAGE','POOR') DEFAULT NULL,
  `pattern_quality_score` int(11) DEFAULT NULL,
  `color_pattern` varchar(120) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `current_owner_id` int(11) DEFAULT NULL,
  `status` enum('ACTIVE','SOLD','DECEASED') DEFAULT NULL,
  `xrpl_registration_tx` varchar(200) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `registration_datetime` timestamp NOT NULL DEFAULT current_timestamp(),
  `registration_code` varchar(60) DEFAULT NULL,
  `farm_code` varchar(10) DEFAULT NULL,
  `photo_path` varchar(200) DEFAULT NULL,
  `standard_koi_id` varchar(60) DEFAULT NULL,
  `blockchain_koi_id` varchar(80) DEFAULT NULL,
  `country_code` varchar(5) DEFAULT 'JPN',
  `last_measured_date` date DEFAULT NULL,
  `health_status` enum('ACTIVE','SICK','QUARANTINE') DEFAULT 'ACTIVE',
  `pond_location` varchar(50) DEFAULT NULL,
  `purchase_price` decimal(10,2) DEFAULT NULL,
  `current_value` decimal(10,2) DEFAULT NULL,
  `registered_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `purchase_currency` varchar(5) DEFAULT 'JPY',
  `current_currency` varchar(5) DEFAULT 'JPY'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `koi`
--

INSERT INTO `koi` (`koi_id`, `org_id`, `koi_code`, `name`, `variety`, `gender`, `birth_date`, `breeder_name`, `size_cm`, `weight_kg`, `body_type`, `skin_quality`, `pattern_quality_score`, `color_pattern`, `notes`, `current_owner_id`, `status`, `xrpl_registration_tx`, `created_at`, `registration_datetime`, `registration_code`, `farm_code`, `photo_path`, `standard_koi_id`, `blockchain_koi_id`, `country_code`, `last_measured_date`, `health_status`, `pond_location`, `purchase_price`, `current_value`, `registered_at`, `purchase_currency`, `current_currency`) VALUES
(1, 1, 'KOI-001', 'Sakura Beauty', 'Kohaku', 'FEMALE', '2023-03-10', 'Tanaka Koi Farm', 45.50, 3.00, 'STANDARD', 'GOOD', NULL, 'Red and White', NULL, 5, 'ACTIVE', 'TXHASH001', '2026-02-03 11:42:56', '2026-02-04 14:59:10', NULL, NULL, 'koi_photos\\koi_1.png', 'JPN-KOI-01-20260204-0003', NULL, 'JPN', NULL, 'ACTIVE', NULL, NULL, NULL, '2026-02-04 15:04:26', 'JPY', 'JPY'),
(2, 1, 'KOI-002', 'Golden Dragon', 'Ogon', 'MALE', '2022-06-21', 'Tanaka Koi Farm', 52.30, 2.00, 'STANDARD', 'GOOD', NULL, 'Solid Gold', NULL, 3, 'ACTIVE', 'TXHASH002', '2026-02-03 11:42:56', '2026-02-04 14:59:10', NULL, NULL, NULL, 'JPN-KOI-01-20260204-0004', NULL, 'JPN', NULL, 'ACTIVE', NULL, NULL, NULL, '2026-02-04 15:04:26', 'JPY', 'JPY'),
(3, 1, 'KOI-003', 'Midnight Star', 'Showa', 'FEMALE', '2023-01-15', 'Tanaka Koi Farm', 41.00, 1.50, 'STANDARD', 'GOOD', NULL, 'Black, Red, White', NULL, 3, 'ACTIVE', 'TXHASH003', '2026-02-03 11:42:56', '2026-02-04 14:59:10', NULL, NULL, NULL, 'JPN-KOI-01-20260204-0016', NULL, 'JPN', NULL, 'ACTIVE', NULL, NULL, NULL, '2026-02-04 15:04:26', 'JPY', 'JPY'),
(4, 1, 'KOI1001', 'Sakura', 'Kohaku', 'FEMALE', '2022-04-12', 'Tanaka Farm', 45.00, 1.50, 'SHORT', 'GOOD', 20, 'Red & White', NULL, 1, 'ACTIVE', NULL, '2026-02-04 16:00:36', '2026-02-04 16:00:36', NULL, NULL, NULL, 'JPN-KOI-01-20260204-0001', NULL, 'JPN', NULL, 'ACTIVE', 'Tanaka-Tokyo', 50.00, 2.00, '2026-02-04 16:00:36', 'JPY', 'XRP'),
(5, 1, 'KOI1002', 'Shiro', 'Shiro Utsuri', 'MALE', '2021-09-05', 'Yamamoto Koi', 50.00, 1.75, 'STANDARD', 'GOOD', 35, '50', NULL, 1, 'ACTIVE', NULL, '2026-02-04 16:49:04', '2026-02-04 16:49:04', NULL, NULL, NULL, 'KOI-JPN-01-20260204-0002', NULL, 'JPN', NULL, 'ACTIVE', 'Yamamoto', NULL, NULL, '2026-02-04 16:49:04', 'JPY', 'JPY'),
(7, 1, 'KOI1003', 'Hikari', 'Ogon', 'FEMALE', '2023-01-20', 'Saito Breeders', 32.00, 1.00, 'STANDARD', 'GOOD', 55, 'Solid Gold', NULL, 1, 'ACTIVE', NULL, '2026-02-04 17:26:16', '2026-02-04 17:26:16', NULL, NULL, NULL, 'KOI-JPN-01-20260204-0005', NULL, 'JPN', NULL, 'ACTIVE', 'Saito', NULL, NULL, '2026-02-04 17:26:16', 'JPY', 'JPY'),
(8, 1, 'KOI1005', 'Momo', 'Asagi', 'FEMALE', '2021-03-11', 'Osaka Koi House', 42.00, 2.00, 'LONG', 'GOOD', 55, 'Blue & Red', NULL, 1, 'ACTIVE', NULL, '2026-02-04 17:39:53', '2026-02-04 17:39:53', NULL, NULL, NULL, 'KOI-JPN-01-20260204-0006', NULL, 'JPN', NULL, 'ACTIVE', 'Osaka', NULL, NULL, '2026-02-04 17:39:53', 'JPY', 'JPY'),
(9, 1, 'KOI1006', 'Tora', 'Bekko', 'MALE', '2022-11-30', 'Kyoto Nishiki', 37.00, 2.00, 'STANDARD', 'GOOD', 45, 'Yellow & Black', NULL, 1, 'ACTIVE', NULL, '2026-02-04 19:40:56', '2026-02-04 19:40:56', NULL, NULL, NULL, 'KOI-JPN-01-20260205-0010', NULL, 'JPN', NULL, 'ACTIVE', 'Nishiki', 45.00, 0.00, '2026-02-04 19:40:56', 'XRP', 'JPY'),
(10, 1, 'KOI1007', 'Hana', 'Sanke', 'FEMALE', '2023-02-15', 'Tanaka Farm', 28.00, 67.00, 'STANDARD', 'GOOD', 65, 'Red, Black & White', NULL, 1, 'ACTIVE', NULL, '2026-02-04 20:39:11', '2026-02-04 20:39:11', NULL, NULL, NULL, 'KOI-JPN-01-20260205-0011', NULL, 'JPN', NULL, 'ACTIVE', 'Osaka', 6.00, 0.00, '2026-02-04 20:39:11', 'JPY', 'JPY'),
(11, 1, 'KOI1008', 'Ryu', 'Ginrin Kohaku', 'MALE', '2019-06-22', 'Yamamoto Koi', 68.00, 3.45, 'STANDARD', 'GOOD', 78, 'Sparkling Red & White', NULL, 1, 'ACTIVE', NULL, '2026-02-04 21:03:02', '2026-02-04 21:03:02', NULL, NULL, NULL, 'KOI-JPN-01-20260205-0012', NULL, 'JPN', NULL, 'ACTIVE', 'Osaka', 345.00, 0.00, '2026-02-04 21:03:02', 'JPY', 'JPY'),
(12, 1, 'KOI1009', 'Yuki', 'Platinum Ogon', 'FEMALE', '2022-08-10', 'Saito Breeders', 40.00, 3.00, 'STANDARD', 'GOOD', 76, 'Metallic White', NULL, 1, 'ACTIVE', '810ADEE0D6C13A78007CAF157B595068E8BCD2E31790457FBFED07CC393EA3D1', '2026-02-04 21:34:16', '2026-02-04 21:34:16', NULL, NULL, NULL, 'KOI-JPN-01-20260205-0013', NULL, 'JPN', NULL, 'ACTIVE', 'Saito', 345.00, 0.00, '2026-02-04 21:34:16', 'XRP', 'JPY'),
(13, 1, 'KOI1010', 'Kaze', 'Chagoi', 'MALE', '2020-12-05', 'Osaka Koi House', 72.00, 3.75, 'STANDARD', 'GOOD', 69, 'Brown', NULL, 1, 'ACTIVE', '3C175F356361E56C2F0C1CE1B5A93165B33710F34C01C426104CBF6FF46510B5', '2026-02-04 21:46:05', '2026-02-04 21:46:05', NULL, NULL, NULL, 'KOI-JPN-01-20260205-0014', NULL, 'JPN', NULL, 'ACTIVE', 'Osaka', 678.00, 0.00, '2026-02-04 21:46:05', 'XRP', 'JPY'),
(14, 1, 'KOI1011', 'Aoi', 'Doitsu Sanke', 'FEMALE', '2021-05-17', 'Kyoto Nishiki', 48.00, 4.00, 'STANDARD', 'GOOD', 0, 'Scaleless Red/Black', NULL, 1, 'ACTIVE', 'F1CD42FF164F706FABF8F916C5AF9EE9E61258126CBA632E8BCF3E6C57BA6EF5', '2026-02-04 21:58:21', '2026-02-04 21:58:21', NULL, NULL, NULL, 'KOI-JPN-01-20260205-0015', NULL, 'JPN', NULL, 'ACTIVE', 'Tokyo', 987.00, 0.00, '2026-02-04 21:58:21', 'XRP', 'JPY');

-- --------------------------------------------------------

--
-- Table structure for table `koi_health_records`
--

CREATE TABLE `koi_health_records` (
  `record_id` int(11) NOT NULL,
  `koi_id` int(11) DEFAULT NULL,
  `record_date` date DEFAULT NULL,
  `weight` decimal(5,2) DEFAULT NULL,
  `size_cm` decimal(5,2) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `vet_name` varchar(100) DEFAULT NULL,
  `treatment` text DEFAULT NULL,
  `xrpl_tx` varchar(200) DEFAULT NULL,
  `date_created` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `koi_health_records`
--

INSERT INTO `koi_health_records` (`record_id`, `koi_id`, `record_date`, `weight`, `size_cm`, `notes`, `vet_name`, `treatment`, `xrpl_tx`, `date_created`) VALUES
(1, 1, '2024-01-10', 2.30, 40.00, 'Regular health check', 'Dr. Saito', 'Vitamin supplement', 'HEALTHTX001', '2024-01-10 12:18:17'),
(2, 1, '2024-06-12', 2.80, 44.00, 'Minor fin damage', 'Dr. Saito', 'Antibacterial treatment', 'HEALTHTX002', '2024-06-12 12:18:17'),
(3, 2, '2024-03-05', 3.10, 50.00, 'Healthy condition', 'Dr. Nakamura', 'None', 'HEALTHTX003', '2024-03-05 12:18:17'),
(4, 1, '2026-02-04', 1.00, 48.00, 'size and weight change', 'Takasomi', '', NULL, '2026-02-04 12:18:17'),
(5, 1, '2026-02-13', 1.03, 49.00, 'Health improvement program', 'Takasomi', 'Vitamines', NULL, '2026-02-13 12:18:17');

-- --------------------------------------------------------

--
-- Table structure for table `koi_id_sequence`
--

CREATE TABLE `koi_id_sequence` (
  `id` int(11) NOT NULL,
  `farm_code` varchar(10) DEFAULT NULL,
  `last_seq` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `koi_id_sequence`
--

INSERT INTO `koi_id_sequence` (`id`, `farm_code`, `last_seq`) VALUES
(1, '01', 1),
(2, NULL, 0),
(3, NULL, 0),
(4, NULL, 0),
(5, NULL, 0),
(6, NULL, 0),
(7, NULL, 0),
(8, NULL, 0),
(9, NULL, 0),
(10, NULL, 0),
(11, NULL, 0),
(12, NULL, 0),
(13, NULL, 0),
(14, NULL, 0),
(15, NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `koi_pedigree`
--

CREATE TABLE `koi_pedigree` (
  `pedigree_id` int(11) NOT NULL,
  `koi_id` int(11) DEFAULT NULL,
  `father_koi_code` varchar(50) DEFAULT NULL,
  `mother_koi_code` varchar(50) DEFAULT NULL,
  `bloodline` varchar(100) DEFAULT NULL,
  `breeder` varchar(100) DEFAULT NULL,
  `date_created` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `koi_pedigree`
--

INSERT INTO `koi_pedigree` (`pedigree_id`, `koi_id`, `father_koi_code`, `mother_koi_code`, `bloodline`, `breeder`, `date_created`) VALUES
(2, 2, 'FTH-300', 'MTH-400', 'Yamazaki Ogon', 'Tanaka Koi Farm', '2026-02-13 12:13:42'),
(3, 3, 'FTH-500', 'MTH-600', 'Isa Showa', 'Tanaka Koi Farm', '2026-02-13 12:13:42'),
(6, 8, 'FAT-01', 'MOT-01', NULL, NULL, '2026-02-13 12:13:42'),
(7, 1, 'FTH-120', 'MTH-200', 'Dainichi Kohaku', 'Tanaka Koi Farm', '2026-02-13 11:13:42'),
(8, 1, 'FTH-100', 'MTH-200', 'Dainichi Kohaku', 'Tanaka Koi Farm', '2026-02-13 12:13:42');

-- --------------------------------------------------------

--
-- Table structure for table `koi_photos`
--

CREATE TABLE `koi_photos` (
  `photo_id` int(11) NOT NULL,
  `koi_id` int(11) DEFAULT NULL,
  `record_date` date DEFAULT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `main_photo` tinyint(1) DEFAULT 0,
  `xrpl_tx` varchar(200) DEFAULT NULL,
  `date_created` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `koi_photos`
--

INSERT INTO `koi_photos` (`photo_id`, `koi_id`, `record_date`, `photo_path`, `description`, `main_photo`, `xrpl_tx`, `date_created`) VALUES
(1, 8, '2026-02-04', 'koi_photos/694cf652-9bcd-47d8-99e3-0ea93fa4f625.jpg', '', 0, NULL, '2026-02-04 15:38:38'),
(2, 8, '2026-02-04', 'C:/Users/LeObr/OneDrive/Desktop/JFIIP Competition/KoiLedger/images/Koi_2.png', '', 0, NULL, '2026-02-04 18:38:38'),
(3, 1, '2026-02-13', 'koi_photos\\koi_1_1770980849.png', NULL, 0, NULL, '2026-02-13 16:07:29'),
(4, 1, '2026-02-13', 'koi_photos\\koi_1_1770981846.png', NULL, 1, NULL, '2026-02-13 16:24:06');

-- --------------------------------------------------------

--
-- Table structure for table `organizations`
--

CREATE TABLE `organizations` (
  `org_id` int(11) NOT NULL,
  `org_name` varchar(150) DEFAULT NULL,
  `farm_code` varchar(10) DEFAULT '01',
  `country_code` char(3) DEFAULT 'JPN',
  `org_type` enum('BREEDER','AUCTION','DEALER','COLLECTOR') DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `contact_email` varchar(120) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `xrpl_wallet` varchar(100) DEFAULT NULL,
  `xrpl_secret` varchar(100) DEFAULT NULL,
  `xrpl_tag` varchar(20) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `organizations`
--

INSERT INTO `organizations` (`org_id`, `org_name`, `farm_code`, `country_code`, `org_type`, `country`, `address`, `contact_email`, `created_at`, `xrpl_wallet`, `xrpl_secret`, `xrpl_tag`, `phone`) VALUES
(1, 'Tanaka Koi Farm', '01', 'JPN', 'BREEDER', 'Japan', 'Niigata Prefecture, Japan', 'info@tanakakoi.jp', '2026-02-03 11:42:23', 'rM3Eq9kfVmEYBWTVZYripuLwkkCdvhH7Zz', 'sEdVwTzP8iEwgPzLw5USK9LEZh6svFD', NULL, NULL),
(2, 'Sakura Auctions', '01', 'JPN', 'AUCTION', 'Japan', 'Tokyo, Japan', 'auctions@sakura.jp', '2026-02-03 11:42:23', 'rwqc83yNYw6nufsRH6LVEy9T5vC4rkmaLG', 'sEdSkSCghYR5RwQyipXSsaBsH1Tg9k2', NULL, '+808123543223'),
(3, 'Yamamoto Collectors', '01', 'JPN', 'COLLECTOR', 'Japan', 'Osaka, Japan', 'yamamoto@koi.jp', '2026-02-03 11:42:23', 'rDiVCXx5bCFdxoubTGBNeEr8K51rf2xmbD', NULL, NULL, '+8084367890'),
(4, 'Global Koi Dealers', '01', 'JPN', 'DEALER', 'USA', 'California, USA', 'sales@globalkoi.com', '2026-02-03 11:42:23', 'rEtTcuaKNMydPinWDigsa64BRek2sJp1ds', NULL, NULL, '+18081234567'),
(5, 'Bona Zawa', '01', 'JPN', 'BREEDER', 'Japan', NULL, 'bona@Zewa.com', '2026-02-11 11:06:07', 'r3YW6YUyyby1R3qGiKbnf71V8qXfA5xGvS', 'sEdVH6Xzb8Xv1YRaBczSLEPEGiN1nwi', NULL, '+8084583763');

-- --------------------------------------------------------

--
-- Table structure for table `ownership_history`
--

CREATE TABLE `ownership_history` (
  `history_id` int(11) NOT NULL,
  `koi_id` int(11) DEFAULT NULL,
  `from_org_id` int(11) DEFAULT NULL,
  `to_org_id` int(11) DEFAULT NULL,
  `transfer_date` date DEFAULT NULL,
  `transfer_type` enum('SALE','GIFT','AUCTION') DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `xrpl_tx` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ownership_history`
--

INSERT INTO `ownership_history` (`history_id`, `koi_id`, `from_org_id`, `to_org_id`, `transfer_date`, `transfer_type`, `price`, `xrpl_tx`) VALUES
(1, 2, 1, 3, '2024-07-01', 'SALE', 1500.00, 'TRANSFERTX001'),
(2, 3, 1, 3, '2024-08-15', 'GIFT', 0.00, 'TRANSFERTX002'),
(3, 4, 2, 5, '2026-02-12', 'SALE', 987.00, '74E31B6B4B9370B3889A310452B299B1B76E1E39BF40228FFB149271A0C9F1D4'),
(4, 4, 5, 1, '2026-02-12', 'GIFT', 1023.00, '8FF9874DB9DEB4FD8C2B6F2B2F6290D7553496C6643959E2538134446A1D8935');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `org_id` int(11) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `role` enum('ADMIN','BREEDER','OWNER','VET','AUCTION') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `org_id`, `username`, `password_hash`, `full_name`, `email`, `role`, `created_at`) VALUES
(1, 1, 'tanaka_admin', '$2b$12$zDh0lGjvIy7JBZf.O7.Jb.OzZGTBqguh0lcGuDetLh8kDBMQpEvx2', 'Hiro Tanaka', 'hiro@tanakakoi.jp', 'BREEDER', '2026-02-03 11:42:44'),
(2, 2, 'auction_mgr', '$2b$12$zDh0lGjvIy7JBZf.O7.Jb.OzZGTBqguh0lcGuDetLh8kDBMQpEvx2', 'Akira Sato', 'akira@sakura.jp', 'AUCTION', '2026-02-03 11:42:44'),
(3, 3, 'yamamoto', '$2b$12$zDh0lGjvIy7JBZf.O7.Jb.OzZGTBqguh0lcGuDetLh8kDBMQpEvx2', 'Kenji Yamamoto', 'kenji@koi.jp', 'OWNER', '2026-02-03 11:42:44'),
(4, 4, 'global_admin', '$2b$12$zDh0lGjvIy7JBZf.O7.Jb.OzZGTBqguh0lcGuDetLh8kDBMQpEvx2', 'John Smith', 'john@globalkoi.com', '', '2026-02-03 11:42:44');

-- --------------------------------------------------------

--
-- Table structure for table `xrpl_transactions`
--

CREATE TABLE `xrpl_transactions` (
  `tx_id` int(11) NOT NULL,
  `koi_id` int(11) DEFAULT NULL,
  `event_type` enum('REGISTRATION','TRANSFER','HEALTH_UPDATE','CERTIFICATE','AUCTION') DEFAULT NULL,
  `xrpl_hash` varchar(200) DEFAULT NULL,
  `memo` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `xrpl_transactions`
--

INSERT INTO `xrpl_transactions` (`tx_id`, `koi_id`, `event_type`, `xrpl_hash`, `memo`, `created_at`) VALUES
(1, 1, 'REGISTRATION', 'TXHASH001', 'Initial registration of Sakura Beauty', '2026-02-03 11:44:07'),
(2, 2, 'REGISTRATION', 'TXHASH002', 'Initial registration of Golden Dragon', '2026-02-03 11:44:07'),
(3, 3, 'REGISTRATION', 'TXHASH003', 'Initial registration of Midnight Star', '2026-02-03 11:44:07'),
(4, 2, 'TRANSFER', 'TRANSFERTX001', 'Transfer from Tanaka Farm to Yamamoto', '2026-02-03 11:44:07'),
(5, 3, 'TRANSFER', 'TRANSFERTX002', 'Gift transfer to Yamamoto', '2026-02-03 11:44:07'),
(6, 1, 'HEALTH_UPDATE', 'HEALTHTX001', 'Health check record', '2026-02-03 11:44:07'),
(7, 1, 'HEALTH_UPDATE', 'HEALTHTX002', 'Treatment for fin damage', '2026-02-03 11:44:07'),
(8, 14, 'REGISTRATION', 'F1CD42FF164F706FABF8F916C5AF9EE9E61258126CBA632E8BCF3E6C57BA6EF5', 'Paid 987 XRP for Koi', '2026-02-04 21:58:21'),
(9, 4, 'TRANSFER', '74E31B6B4B9370B3889A310452B299B1B76E1E39BF40228FFB149271A0C9F1D4', 'KOI|TRANSFER|KOI_ID:4|BUYER:5|SELLER:2|JPY:987.0|XRP:2.76|REASON:SALE|DATE:2026-02-12', '2026-02-12 12:25:14'),
(10, 4, 'TRANSFER', '8FF9874DB9DEB4FD8C2B6F2B2F6290D7553496C6643959E2538134446A1D8935', 'KOI|TRANSFER|KOI_ID:4|BUYER:1|SELLER:5|JPY:1023.0|XRP:2.86|REASON:GIFT|DATE:2026-02-12', '2026-02-12 12:30:56'),
(11, 1, 'HEALTH_UPDATE', NULL, 'Added health record', '2026-02-13 05:54:58'),
(12, 1, '', NULL, 'Updated pedigree', '2026-02-13 06:11:28'),
(13, 1, '', NULL, 'Added new pedigree record', '2026-02-13 07:09:30');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auctions`
--
ALTER TABLE `auctions`
  ADD PRIMARY KEY (`auction_id`),
  ADD KEY `koi_id` (`koi_id`);

--
-- Indexes for table `certificates`
--
ALTER TABLE `certificates`
  ADD PRIMARY KEY (`certificate_id`),
  ADD KEY `koi_id` (`koi_id`);

--
-- Indexes for table `farms`
--
ALTER TABLE `farms`
  ADD PRIMARY KEY (`farm_id`),
  ADD UNIQUE KEY `farm_code` (`farm_code`);

--
-- Indexes for table `fish_types`
--
ALTER TABLE `fish_types`
  ADD PRIMARY KEY (`type_code`);

--
-- Indexes for table `koi`
--
ALTER TABLE `koi`
  ADD PRIMARY KEY (`koi_id`),
  ADD UNIQUE KEY `koi_code` (`koi_code`),
  ADD KEY `org_id` (`org_id`);

--
-- Indexes for table `koi_health_records`
--
ALTER TABLE `koi_health_records`
  ADD PRIMARY KEY (`record_id`),
  ADD KEY `koi_id` (`koi_id`);

--
-- Indexes for table `koi_id_sequence`
--
ALTER TABLE `koi_id_sequence`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `farm_code` (`farm_code`);

--
-- Indexes for table `koi_pedigree`
--
ALTER TABLE `koi_pedigree`
  ADD PRIMARY KEY (`pedigree_id`),
  ADD KEY `koi_id` (`koi_id`);

--
-- Indexes for table `koi_photos`
--
ALTER TABLE `koi_photos`
  ADD PRIMARY KEY (`photo_id`),
  ADD KEY `koi_id` (`koi_id`);

--
-- Indexes for table `organizations`
--
ALTER TABLE `organizations`
  ADD PRIMARY KEY (`org_id`);

--
-- Indexes for table `ownership_history`
--
ALTER TABLE `ownership_history`
  ADD PRIMARY KEY (`history_id`),
  ADD KEY `koi_id` (`koi_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD KEY `org_id` (`org_id`);

--
-- Indexes for table `xrpl_transactions`
--
ALTER TABLE `xrpl_transactions`
  ADD PRIMARY KEY (`tx_id`),
  ADD KEY `koi_id` (`koi_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auctions`
--
ALTER TABLE `auctions`
  MODIFY `auction_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `certificates`
--
ALTER TABLE `certificates`
  MODIFY `certificate_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `farms`
--
ALTER TABLE `farms`
  MODIFY `farm_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `koi`
--
ALTER TABLE `koi`
  MODIFY `koi_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `koi_health_records`
--
ALTER TABLE `koi_health_records`
  MODIFY `record_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `koi_id_sequence`
--
ALTER TABLE `koi_id_sequence`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `koi_pedigree`
--
ALTER TABLE `koi_pedigree`
  MODIFY `pedigree_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `koi_photos`
--
ALTER TABLE `koi_photos`
  MODIFY `photo_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `organizations`
--
ALTER TABLE `organizations`
  MODIFY `org_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `ownership_history`
--
ALTER TABLE `ownership_history`
  MODIFY `history_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `xrpl_transactions`
--
ALTER TABLE `xrpl_transactions`
  MODIFY `tx_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auctions`
--
ALTER TABLE `auctions`
  ADD CONSTRAINT `auctions_ibfk_1` FOREIGN KEY (`koi_id`) REFERENCES `koi` (`koi_id`);

--
-- Constraints for table `certificates`
--
ALTER TABLE `certificates`
  ADD CONSTRAINT `certificates_ibfk_1` FOREIGN KEY (`koi_id`) REFERENCES `koi` (`koi_id`);

--
-- Constraints for table `koi`
--
ALTER TABLE `koi`
  ADD CONSTRAINT `koi_ibfk_1` FOREIGN KEY (`org_id`) REFERENCES `organizations` (`org_id`);

--
-- Constraints for table `koi_health_records`
--
ALTER TABLE `koi_health_records`
  ADD CONSTRAINT `koi_health_records_ibfk_1` FOREIGN KEY (`koi_id`) REFERENCES `koi` (`koi_id`);

--
-- Constraints for table `koi_pedigree`
--
ALTER TABLE `koi_pedigree`
  ADD CONSTRAINT `koi_pedigree_ibfk_1` FOREIGN KEY (`koi_id`) REFERENCES `koi` (`koi_id`);

--
-- Constraints for table `koi_photos`
--
ALTER TABLE `koi_photos`
  ADD CONSTRAINT `koi_photos_ibfk_1` FOREIGN KEY (`koi_id`) REFERENCES `koi` (`koi_id`);

--
-- Constraints for table `ownership_history`
--
ALTER TABLE `ownership_history`
  ADD CONSTRAINT `ownership_history_ibfk_1` FOREIGN KEY (`koi_id`) REFERENCES `koi` (`koi_id`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`org_id`) REFERENCES `organizations` (`org_id`);

--
-- Constraints for table `xrpl_transactions`
--
ALTER TABLE `xrpl_transactions`
  ADD CONSTRAINT `xrpl_transactions_ibfk_1` FOREIGN KEY (`koi_id`) REFERENCES `koi` (`koi_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
