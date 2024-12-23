-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2024-12-23 18:21:03
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
-- 資料庫： `food_pangolin`
--

-- --------------------------------------------------------

--
-- 資料表結構 `delivery_man`
--

CREATE TABLE `delivery_man` (
  `Did` int(10) NOT NULL,
  `name` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `phone` varchar(10) NOT NULL,
  `id` varchar(11) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pw` varchar(11) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `address` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `delivery_man`
--

INSERT INTO `delivery_man` (`Did`, `name`, `phone`, `id`, `pw`, `address`) VALUES
(1, '張小', '0985645', '555', '555', '走道'),
(2, '許大', '054065', '11111', '11111', '廁所'),
(3, '張小', '046546', '777', '777', '公園');

-- --------------------------------------------------------

--
-- 資料表結構 `dish`
--

CREATE TABLE `dish` (
  `dish_id` int(10) NOT NULL,
  `Rid` int(10) NOT NULL,
  `restaurant_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `dish_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `price` int(10) NOT NULL,
  `content` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `dish`
--

INSERT INTO `dish` (`dish_id`, `Rid`, `restaurant_name`, `dish_name`, `price`, `content`) VALUES
(1, 1, '麥當勞', '漢堡', 50, '好好吃'),
(2, 1, '麥當勞', '薯條', 30, '好鹹'),
(3, 2, '肯德基', '蛋塔', 20, '好吃'),
(4, 2, '肯德基', '炸雞', 50, '真好吃'),
(5, 1, '麥當勞', '薯餅', 20, '早餐才有'),
(6, 1, '麥當勞', '奶茶', 10, '好喝');

-- --------------------------------------------------------

--
-- 資料表結構 `guest`
--

CREATE TABLE `guest` (
  `name` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `phone` varchar(11) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `Gid` int(10) NOT NULL,
  `address` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `id` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pw` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `guest`
--

INSERT INTO `guest` (`name`, `phone`, `Gid`, `address`, `id`, `pw`) VALUES
('陳仙聲', '0911123123', 1, '南投縣埔里鎮大學路2號', '123', '123'),
('小王', '01445155', 2, '埔里', '666', '666'),
('qqq', '09809', 3, 'hyh', '321', '321');

-- --------------------------------------------------------

--
-- 資料表結構 `guest_cart`
--

CREATE TABLE `guest_cart` (
  `Gid` int(10) NOT NULL,
  `restaurant_name` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `dish_name` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `price` int(10) NOT NULL,
  `quantity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `history_orderlists`
--

CREATE TABLE `history_orderlists` (
  `order_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `history_orderlists`
--

INSERT INTO `history_orderlists` (`order_id`, `quantity`, `price`) VALUES
(20, 4, 50),
(20, 5, 30),
(21, 2, 50),
(22, 2, 20),
(23, 1, 50),
(24, 1, 20),
(24, 1, 50),
(25, 1, 50),
(26, 2, 50);

-- --------------------------------------------------------

--
-- 資料表結構 `orderlist`
--

CREATE TABLE `orderlist` (
  `Rid` int(10) NOT NULL,
  `Gid` int(10) NOT NULL,
  `Did` int(10) DEFAULT NULL,
  `order_id` int(10) NOT NULL,
  `finish_time` datetime NOT NULL,
  `pickup_time` datetime DEFAULT NULL,
  `arrive_time` datetime DEFAULT NULL,
  `status` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '待接單',
  `point` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `orderlist`
--

INSERT INTO `orderlist` (`Rid`, `Gid`, `Did`, `order_id`, `finish_time`, `pickup_time`, `arrive_time`, `status`, `point`) VALUES
(1, 1, 3, 20, '2024-12-23 21:46:35', '2024-12-23 22:45:53', '2024-12-23 22:54:17', '已完成', 4),
(1, 2, 3, 21, '2024-12-23 21:46:36', '2024-12-23 22:56:06', '2024-12-23 22:56:11', '已完成', NULL),
(2, 3, 3, 22, '2024-12-23 21:46:46', '2024-12-23 23:34:22', '2024-12-23 23:34:37', '已完成', NULL),
(2, 1, 3, 24, '2024-12-23 23:27:56', '2024-12-24 00:02:31', '2024-12-24 00:03:00', '已完成', 5),
(1, 1, 3, 25, '2024-12-23 23:34:02', '2024-12-23 23:35:11', '2024-12-24 00:03:02', '已完成', 5),
(1, 1, 3, 26, '2024-12-24 00:34:46', '2024-12-24 00:35:32', '2024-12-24 00:35:34', '已完成', 4);

-- --------------------------------------------------------

--
-- 資料表結構 `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `Gid` int(11) DEFAULT NULL,
  `order_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `orders`
--

INSERT INTO `orders` (`order_id`, `Gid`, `order_date`) VALUES
(1, 1, '2024-12-16 11:37:17'),
(2, 2, '2024-12-16 14:49:24'),
(3, 2, '2024-12-16 14:56:35'),
(4, 2, '2024-12-16 14:58:10'),
(5, 1, '2024-12-16 15:00:44'),
(6, 1, '2024-12-18 17:25:14'),
(7, 3, '2024-12-18 17:26:35'),
(8, 2, '2024-12-18 17:27:15'),
(9, 1, '2024-12-18 17:30:04'),
(10, 2, '2024-12-18 17:30:24'),
(11, 3, '2024-12-18 17:30:44'),
(12, 1, '2024-12-23 17:42:28'),
(15, 1, '2024-12-23 18:16:33'),
(16, 1, '2024-12-23 19:00:50'),
(17, 1, '2024-12-23 19:14:07'),
(18, 1, '2024-12-23 19:15:11'),
(19, 1, '2024-12-23 19:18:24'),
(20, 1, '2024-12-23 21:45:35'),
(21, 2, '2024-12-23 21:45:59'),
(22, 3, '2024-12-23 21:46:17'),
(23, 3, '2024-12-23 21:51:58'),
(24, 1, '2024-12-23 23:27:40'),
(25, 1, '2024-12-23 23:33:50'),
(26, 1, '2024-12-24 00:34:34');

-- --------------------------------------------------------

--
-- 資料表結構 `prepare_dish`
--

CREATE TABLE `prepare_dish` (
  `Rid` int(10) NOT NULL,
  `dish_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `quantity` int(10) NOT NULL,
  `price` int(10) NOT NULL,
  `Gid` int(10) NOT NULL,
  `guest_name` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `confirm` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '0',
  `order_id` int(10) NOT NULL,
  `confirm_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `restaurant`
--

CREATE TABLE `restaurant` (
  `Rid` int(10) NOT NULL,
  `name` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `address` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `phone` varchar(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `point` float NOT NULL,
  `id` varchar(11) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pw` varchar(11) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `restaurant`
--

INSERT INTO `restaurant` (`Rid`, `name`, `address`, `phone`, `point`, `id`, `pw`) VALUES
(1, '麥當勞', '南投縣埔里鎮埔里路23號', '0423887898', 4.3333, '111', '111'),
(2, '肯德基', '台中市南屯區五權西路', '0423805656', 5, '222', '222'),
(3, '輕井澤', '台中', '0233546', 0, '333', '333'),
(4, '鼎王', '台中市', '04564684', 0, '3333', '3333'),
(5, '屋馬', '埔里鎮', '046546', 0, '123', '123'),
(6, '拿坡里', '埔里鎮', '015654', 0, '999', '999');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `delivery_man`
--
ALTER TABLE `delivery_man`
  ADD PRIMARY KEY (`Did`);

--
-- 資料表索引 `guest`
--
ALTER TABLE `guest`
  ADD PRIMARY KEY (`Gid`);

--
-- 資料表索引 `orderlist`
--
ALTER TABLE `orderlist`
  ADD PRIMARY KEY (`order_id`);

--
-- 資料表索引 `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`);

--
-- 資料表索引 `restaurant`
--
ALTER TABLE `restaurant`
  ADD PRIMARY KEY (`Rid`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
