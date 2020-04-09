INSERT INTO Person (username, password, firstName, lastName, email) VALUES
('A', 'A', 'Ann', 'Andrews', 'ann123@gmail.com'),
('B', 'B', 'Bill', 'Barker', 'washyourhands@hotmail.com'),
('C', 'C', 'Cathy', 'Chen', 'ilovedatabases@gmail.com'),
('D', 'D', 'Dave', 'Davis', 'davedavis1@gmail.com'),
('E', 'E', 'Emily', 'Elhaj', 'stayhomestaysafe@aol.com');

INSERT INTO Photo (pID, postingdate, filepath, allFollowers, caption, poster) VALUES
(1, '2020-01-01 00:00:00', '1.jpg', 1, 'photo 1', 'A'),
(2, '2020-02-02 00:00:00', '2.jpg', 1, 'photo 2', 'C'),
(3, '2020-1-11 00:00:00', '3.jpg', 1, 'photo 3', 'D'),
(4, '2020-2-11 00:00:00', '4.jpg', 1, NULL, 'D'),
(5, '2020-3-11 00:00:00', '5.jpg', 0, 'photo 5', 'E');

INSERT INTO FriendGroup (groupName, groupCreator, description) VALUES
('best friends', 'E', 'Emily: best friends'),
('best friends', 'D', 'Dave: best friends'),
('roommates', 'D', 'Dave: roommates');

INSERT INTO BelongTo (username, groupName, groupCreator) VALUES
('A', 'best friends', 'E'),
('B', 'roommates', 'D');

INSERT INTO Follow (follower, followee, followStatus) VALUES
('B', 'A', 1),
('C', 'A', 0),
('D', 'A', 0),
('B', 'D', 1),
('A', 'B', 1),
('E', 'A', 1),
('D', 'B', 1),
('E', 'B', 0),
('D', 'C', 1),
('A', 'E', 1);

INSERT INTO Tag (pID, username, tagStatus) VALUES
(1, 'B', 0),
(1, 'C', 1),
(2, 'D', 1),
(1, 'E', 1);

INSERT INTO ReactTo (username, pID, reactionTime, comment, emoji) VALUES
('D', 2, '2020-04-03 00:00:00', 'nice photo!', 'heart'),
('E', 1, '2020-04-03 00:00:00', NULL, 'thumbs up');

INSERT INTO SharedWith (pID, groupName, groupCreator) VALUES
(2, 'best friends', 'E'),
(3, 'best friends', 'D');