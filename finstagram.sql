CREATE TABLE Person (
	username VARCHAR(10) NOT NULL,
	firstName VARCHAR(10),
	lastName VARCHAR(10),
	password VARCHAR(32),
	email VARCHAR(62),
	PRIMARY KEY (username)
);

CREATE TABLE Photo (
	pID int NOT NULL;
	postingDate DATETIME,
	filePath VARCHAR(255),
	allFollowers BOOLEAN,
	caption VARCHAR(255),
	PRIMARY KEY (pID)
);

CREATE TABLE Posted_By (
	FOREIGN KEY photoID int references Photo (pID),
	FOREIGN KEY posterUsername VARCHAR(10) references Person (username),
	UNIQUE(photoID)
);

CREATE TABLE ReactTo (
	userReact VARCHAR(10) references Person(username),
	react2PhotoID int references Photo(pID),
	reactionTime DATETIME,
	comment VARCHAR(140),
	emoji 
);