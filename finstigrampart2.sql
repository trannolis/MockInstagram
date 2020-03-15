create table Person(
    username         varchar(16),
    first_name         varchar(16),
    last_name         varchar(16),
    password         varchar(16),
    email             varchar(32),
    primary key(username)
);

create table Photo(
    pID            INT,
    postingDate        DATETIME,
    filePath        varchar(32),
    allFollowers        BOOLEAN,
    caption            varchar(64),
    primary key(pID)
    );

create table Tag(
    username         varchar(16),
    pID            INT,
    tagStatus        BOOLEAN,
    primary key(username,pID),
    foreign key (username) references Person(username),
    foreign key (pID) references Photo(pID)
    );

create table ReactTo(
    username         varchar(16),
    pID            INT,
    reactionTime        DATETIME,
    comment        varchar(64),
    emoji            varchar(16),
    primary key(username,pID),
    foreign key (username) references Person(username),
    foreign key (pID) references Photo(pID)
    );

create table PostedBy(
    username         varchar(16),
    pID            INT,
    primary key(username,pID),
    foreign key (username) references Person(username),
    foreign key (pID) references Photo(pID)
    );

create table Follow(
    follower         varchar(16),
    followee         varchar(16),
    followStatus         BOOLEAN,
    primary key(follower,followee),
    Foreign key (follower) references Person(username),
    Foreign key (followee) references Person(username)
    );

create table FriendGroup(
    username         varchar(16),
    groupName        varchar(16),
    description         varchar(64),
    primary key(username,groupName),
    foreign key (username) references Person(username)
    );

create table BelongTo(
    groupMember         varchar(16),
    creator         varchar(16),
    groupName        varchar(16),
    primary key(groupMember,creator,groupName),
    foreign key (groupMember) references Person(username),
    foreign key (creator,groupName) references FriendGroup(username,groupName)
    );

create table SharedWith(
    pID            INT,
    username         varchar(16),
    groupName        varchar(16),
    primary key(pID,username,groupName),
    foreign key(pID) references Photo(pID),
    foreign key (creator,groupName) references FriendGroup(username,groupName)
    );

SELECT DISTINCT pID
FROM SharedWith NATURAL JOIN FriendGroup NATURAL JOIN BelongTo ON (FriendGroup.groupName=BelongTo.groupName AND FriendGroup.username=BelongTo.Creator)
WHERE groupMember = ‘Ann’
