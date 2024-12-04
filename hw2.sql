-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2024-10-28 09:27:13
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `hw2`
--

-- --------------------------------------------------------

--
-- 資料表結構 `accounts1`
--

CREATE TABLE `accounts1` (
  `Uid` int(11) NOT NULL,
  `Uname` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pw` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `accounts1`
--

INSERT INTO `accounts1` (`Uid`, `Uname`, `pw`) VALUES
(111, '草頭黃', '111'),
(222, '爾東陳', '222'),
(333, '木子李', '333'),
(444, '呂寶寶', '444'),
(999, 'www', '999'),
(12345, '賴皮豬', '1111'),
(654321, 'zzzz', '123456');

-- --------------------------------------------------------

--
-- 資料表結構 `price1`
--

CREATE TABLE `price1` (
  `bid_id` int(11) NOT NULL,
  `Pid` int(11) DEFAULT NULL,
  `Uid` int(11) DEFAULT NULL,
  `name` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `now_price` int(10) NOT NULL,
  `bid_time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `price1`
--

INSERT INTO `price1` (`bid_id`, `Pid`, `Uid`, `name`, `now_price`, `bid_time`) VALUES
(6, 8, 222, '膠帶', 50, '2024-10-28 02:59:50'),
(9, 12, 222, '眼鏡', 61, '2024-10-28 03:41:36'),
(10, 12, 222, '眼鏡', 70, '2024-10-28 03:41:39'),
(11, 7, 111, '水壺', 50, '2024-10-28 06:27:11'),
(12, 9, 12345, '外套', 150, '2024-10-28 06:54:48'),
(13, 7, 111, '水壺', 120, '2024-10-28 06:59:30'),
(14, 11, 111, '手錶', 70, '2024-10-28 07:24:02'),
(15, 11, 111, '手錶', 80, '2024-10-28 07:24:04'),
(16, 11, 333, '手錶', 90, '2024-10-28 07:24:37');

-- --------------------------------------------------------

--
-- 資料表結構 `website1`
--

CREATE TABLE `website1` (
  `Pid` int(11) NOT NULL,
  `name` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `content` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `starting_price` int(10) NOT NULL,
  `Uid` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `website1`
--

INSERT INTO `website1` (`Pid`, `name`, `content`, `starting_price`, `Uid`, `created_at`) VALUES
(7, '水壺', '綠色水壺', 60, 111, '2024-10-28 01:53:38'),
(8, '膠帶', '透明膠帶', 20, 111, '2024-10-28 02:22:40'),
(9, '外套', '黑色外套', 120, 222, '2024-10-28 02:23:13'),
(11, '手錶', '藍色手錶', 50, 333, '2024-10-28 03:04:17'),
(12, '眼鏡', '黑框眼鏡', 60, 222, '2024-10-28 03:41:16'),
(14, '馬克杯', '111', 20, 111, '2024-10-28 08:10:01');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `accounts1`
--
ALTER TABLE `accounts1`
  ADD PRIMARY KEY (`Uid`);

--
-- 資料表索引 `price1`
--
ALTER TABLE `price1`
  ADD PRIMARY KEY (`bid_id`),
  ADD KEY `Pid` (`Pid`),
  ADD KEY `Uid` (`Uid`);

--
-- 資料表索引 `website1`
--
ALTER TABLE `website1`
  ADD PRIMARY KEY (`Pid`),
  ADD KEY `Uid` (`Uid`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `accounts1`
--
ALTER TABLE `accounts1`
  MODIFY `Uid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=654322;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `price1`
--
ALTER TABLE `price1`
  MODIFY `bid_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `website1`
--
ALTER TABLE `website1`
  MODIFY `Pid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `price1`
--
ALTER TABLE `price1`
  ADD CONSTRAINT `price1_ibfk_1` FOREIGN KEY (`Pid`) REFERENCES `website1` (`Pid`),
  ADD CONSTRAINT `price1_ibfk_2` FOREIGN KEY (`Uid`) REFERENCES `accounts1` (`Uid`);

--
-- 資料表的限制式 `website1`
--
ALTER TABLE `website1`
  ADD CONSTRAINT `website1_ibfk_1` FOREIGN KEY (`Uid`) REFERENCES `accounts1` (`Uid`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
