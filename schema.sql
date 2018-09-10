DROP TABLE IF EXISTS users;
CREATE TABLE users (
	email text PRIMARY KEY,
	fullname text,
	password varchar(64),
	phone varchar(10) UNIQUE);

DROP TABLE IF EXISTS friends;
CREATE TABLE friends (
	user1 text,
	user2 text,
	status text,
	amount DECIMAL);

DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
	description text,
	user1 text,
	user2 text,
	amount1 decimal,
	amount2 decimal,
	datetime timestamp);

DROP TABLE IF EXISTS groups;
CREATE TABLE groups (
	id int primary key,
	name text,
	user1 text);
INSERT INTO groups VALUES(0,"a","a");
DROP TABLE IF EXISTS groupmems;
CREATE TABLE groupmems (
	id int,
	user1 text,
	user2 text,
	amount DECIMAL,
	foreign key (id) references groups(id),
	foreign key (user1,user2) references users(email,email));

DROP TABLE IF EXISTS grouptransactions;
CREATE TABLE grouptransactions (
	id int ,
	description text,
	user1 text,
	user2 text,
	amount1 decimal,
	datetime timestamp);

DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
	id int,
	comment text,
	user text,
	foreign key (id) references groups(id),
	foreign key (user) references users(email));
