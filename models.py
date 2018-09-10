import sqlite3 as sql
from datetime import datetime
def getUser(data):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT fullname,email,phone FROM users WHERE phone = '"+data+"' OR email ='"+data+"'")
	user = cursor.fetchone()
	conn.close()
	return user

def getName(data):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT fullname FROM users WHERE phone = '"+data+"' OR email ='"+data+"'")
	user = cursor.fetchone()
	conn.close()
	return user[0]

def getUserPass(data):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT password FROM users WHERE phone = '"+data+"' OR email ='"+data+"'")
	userPass = cursor.fetchone()
	conn.close()
	return userPass	

def sendRequest(user1,user2):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT status FROM friends WHERE user1 ='"+user1+"' and user2 ='"+user2+"' ")
	status = cursor.fetchone()
	if not status :
		cursor.execute("INSERT INTO friends VALUES(?,?,?,?)",(user1,user2,"sent_request","0.00"))
		cursor.execute("INSERT INTO friends VALUES(?,?,?,?)",(user2,user1,"got_request","0.00"))
		conn.commit()
		return "sent"
	elif status[0] == "sent_request":
		return "You have already sent a request to "
	elif status[0] == "friends":
		return "You are already friends with "
	elif status[0] == "got_request":
		return "You already got friend request from "
	conn.close()

def insertUser(email,name,hashPass,phone):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("INSERT INTO users VALUES(?,?,?,?)",(email,name,hashPass,phone))
	conn.commit()
	conn.close()

def acceptRequest(user1,user2): 
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("UPDATE friends SET status = 'friends' WHERE user1= '"+user1+"' AND user2 = '"+user2+"' ")
	cursor.execute("UPDATE friends SET status = 'friends' WHERE user1= '"+user2+"' AND user2 = '"+user1+"' ")
	conn.commit()
	conn.close()

def getFriends(user1,status):
	conn = sql.connect("database.db")
	cursor1=conn.cursor()
	cursor2=conn.cursor()
	cursor1.execute("SELECT user2 FROM friends WHERE user1 ='"+user1+"' AND status ='"+status+"'")
	user = cursor1.fetchone()
	friends=[]
	while user:
		cursor2.execute("SELECT fullname,email,phone FROM users WHERE email ='"+user[0]+"'")
		user = cursor2.fetchone()
		user = list(user)
		if status == "friends":
			amount = getAmount(user1,user[1])
			user.append(amount)
		friends.append(user)		
		user = cursor1.fetchone()
	conn.close()
	return friends

def getAmount(user1,user2):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT amount FROM friends WHERE user1 ='"+user1+"' AND user2 = '"+user2+"' ")
	amount = cursor.fetchone()
	conn.close()
	return amount[0]

def doTransaction(user1,user2,payment,value,description):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	amount1=0.00
	amount2=0.00
	if value == 1:
		amount1 = payment/2
		amount2 = -payment/2
	elif value == 2:
		amount1 = -payment
		amount2 = payment
	elif value == 3:
		amount1 = payment
		amount2 = -payment
	elif value == 4:
		amount1 = -payment/2
		amount2 = payment/2
	amount1 = round(amount1,2)
	amount2 = round(amount2,2)
	cursor.execute("INSERT INTO transactions VALUES(?,?,?,?,?,?)",(description,user1,user2,amount1,amount2,datetime.now()))
	cursor.execute("SELECT amount FROM friends WHERE user1= '"+user1+"' AND user2 = '"+user2+"' ")
	amount=cursor.fetchone()
	amount1 = float(amount[0]) + amount1

	cursor.execute("SELECT amount FROM friends WHERE user1= '"+user2+"' AND user2 = '"+user1+"' ")
	amount=cursor.fetchone()
	amount2 = float(amount[0]) + amount2

	cursor.execute("UPDATE friends SET amount = (?) WHERE user1= '"+user1+"' AND user2 = '"+user2+"' ",(amount1,))
	cursor.execute("UPDATE friends SET amount = (?) WHERE user1= '"+user2+"' AND user2 = '"+user1+"' ",(amount2,))
	conn.commit()
	conn.close()

def getTotal(user):	
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT sum(amount) FROM friends WHERE user1 = (?)",(user,))
	amount = cursor.fetchone()
	conn.close()
	return amount[0]

def getActs(user1):
	conn = sql.connect("database.db")
	cursor1=conn.cursor()
	cursor2=conn.cursor()
	cursor1.execute("SELECT * FROM transactions WHERE user1 ='"+user1+"' OR user2 = '"+user1+"' ORDER BY datetime DESC")
	act = cursor1.fetchone()
	acts = []
	while act:
		if act[1] == user1:
			cursor2.execute("SELECT fullname FROM users WHERE email ='"+act[2]+"'")
		elif act[2] == user1:
			cursor2.execute("SELECT fullname FROM users WHERE email ='"+act[1]+"'") 
		name = cursor2.fetchone()
		act = list(act)
		act.append(name[0])
		acts.append(act)		
		act = cursor1.fetchone()
	conn.close()	
	return acts

def settle(user1,user2):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	amount1 = getAmount(user1,user2)
	amount2 = getAmount(user2,user1)
	description = "Settled Up"
	cursor.execute("UPDATE friends SET amount = (?) WHERE user1= '"+user1+"' AND user2 = '"+user2+"' ",(0.00,))
	cursor.execute("UPDATE friends SET amount = (?) WHERE user1= '"+user2+"' AND user2 = '"+user1+"' ",(0.00,))
	cursor.execute("INSERT INTO transactions VALUES(?,?,?,?,?,?)",(description,user1,user2,amount1,amount2,datetime.now()))
	conn.commit()
	conn.close()

def insertGroup(name,user):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT MAX(id) FROM groups")
	maxVal = cursor.fetchone()
	cursor.execute("INSERT INTO groups VALUES(?,?,?)",(maxVal[0]+1,name,user))
	cursor.execute("INSERT INTO groupmems VALUES(?,?,?,?)",(maxVal[0]+1,user,user,0))
	conn.commit()
	conn.close()

def getGroupFromId(id1):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT name FROM groups WHERE id = (?)",(id1,))
	name = cursor.fetchone()
	conn.close()
	return name[0]

def getGroups(user):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT DISTINCT groups.id,groups.name FROM groupmems LEFT JOIN groups WHERE groups.id = groupmems.id AND groupmems.user1 = (?)",(user,))
	groups = cursor.fetchall()
	conn.close()
	return groups

def addNewMember(user,id1):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT DISTINCT user1 FROM groupmems WHERE id = (?)",(id1,))
	members = cursor.fetchall()
	for i in members:
		cursor.execute("INSERT INTO groupmems VALUES(?,?,?,?)",(id1,user,i[0],0))
		cursor.execute("INSERT INTO groupmems VALUES(?,?,?,?)",(id1,i[0],user,0))
	cursor.execute("INSERT INTO groupmems VALUES(?,?,?,?)",(id1,user,user,0))
	conn.commit()
	conn.close()

def groupMembers(user,id1):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT fullname,email,phone,amount FROM users LEFT JOIN groupmems WHERE groupmems.id = (?) AND user1 = (?) AND user2 = email",(id1,user))
	members = cursor.fetchall()
	conn.close()
	return members

def checkFriend(user1,user2):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT * from friends where user1 = (?) and user2 = (?)",(user1,user2))
	friend = cursor.fetchone()
	conn.close()
	msg = "no"
	if friend:
		msg = "yes"
	return msg

def checkMember(user,id1):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT * from groupmems where user1 = (?) and id = (?)",(user,id1))
	member = cursor.fetchone()
	conn.close()
	msg = "not a member"
	if member:
		msg = "member"
	return msg

def addGroupTrans(user,id1,mems,desc):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	for member in mems:
		if member[0] != user:
			cursor.execute("UPDATE groupmems SET amount = amount + (?) WHERE id=(?) AND user1 = (?) AND user2 = (?)",(member[1],id1,user,member[0]))
			cursor.execute("UPDATE groupmems SET amount = amount - (?) WHERE id=(?) AND user1 = (?) AND user2 = (?)",(member[1],id1,member[0],user))	
			cursor.execute("INSERT INTO grouptransactions VALUES(?,?,?,?,?,?)",(id1,desc,user,member[0],member[1],datetime.now()))
			cursor.execute("INSERT INTO grouptransactions VALUES(?,?,?,?,?,?)",(id1,desc,member[0],user,-float(member[1]),datetime.now()))
	conn.commit()
	conn.close()


def settleInGroup(id1,user1,user2):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT amount FROM groupmems WHERE id = (?) AND user1 = (?) AND user2 = (?)",(id1,user1,user2))
	amount = cursor.fetchone()
	description = "Settled Up"
	cursor.execute("UPDATE groupmems SET amount = (?) WHERE id = (?) AND user1= (?) AND user2 = (?) ",(0.00,id1,user1,user2))
	cursor.execute("UPDATE groupmems SET amount = (?) WHERE id = (?) AND user1= (?) AND user2 = (?) ",(0.00,id1,user2,user1))
	cursor.execute("INSERT INTO grouptransactions VALUES(?,?,?,?,?,?)",(id1,description,user1,user2,amount[0],datetime.now()))
	cursor.execute("INSERT INTO grouptransactions VALUES(?,?,?,?,?,?)",(id1,description,user2,user1,-float(amount[0]),datetime.now()))
	conn.commit()
	conn.close()

def getGroupActs(user):
	conn = sql.connect("database.db")
	cursor1=conn.cursor()
	cursor2=conn.cursor()
	cursor1.execute("SELECT groups.name,description,grouptransactions.user1,users.fullname,amount1 FROM grouptransactions LEFT JOIN users,groups WHERE grouptransactions.user1 = (?) AND groups.id = grouptransactions.id AND email = user2 ORDER BY datetime DESC",(user,))
	acts = cursor1.fetchall()
	conn.close()	
	return acts

def settleGroup(id1,user):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor1=conn.cursor()
	cursor.execute("SELECT * FROM groupmems WHERE id = (?)",(id1,))
	user1 = getUser(user)[0]
	members = cursor.fetchall()
	for member in members:
		cursor1.execute("SELECT amount FROM friends WHERE user1= (?) AND user2 = (?) ",(member[1],member[2]))
		amount = cursor1.fetchone()
		if amount != None:
			payment = float(amount[0]) + float(member[3])
			description = "settled group "+str(getGroupFromId(id1))
			cursor.execute("INSERT INTO transactions VALUES(?,?,?,?,?,?)",(description,member[1],member[2],payment,-float(payment),datetime.now()))
			cursor1.execute("UPDATE friends SET amount = (?) WHERE user1= (?) AND user2 = (?) ",(payment,member[1],member[2]))
	cursor.execute("DELETE FROM groups WHERE id = (?)",(id1,))	
	cursor.execute("DELETE FROM groupmems WHERE id = (?)",(id1,))	
	cursor.execute("DELETE FROM grouptransactions WHERE id = (?)",(id1,))
	conn.commit()
	conn.close()	

def addComment(id1,comment,user):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("INSERT INTO comments VALUES(?,?,?)",(id1,comment,user))
	conn.commit()
	conn.close()

def getComments(id1):
	conn = sql.connect("database.db")
	cursor=conn.cursor()
	cursor.execute("SELECT fullname,comment FROM comments LEFT JOIN users WHERE id = (?) AND email = user ",(id1,))
	comments = cursor.fetchall()
	conn.close()
	return comments
