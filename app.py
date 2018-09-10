from flask import Flask,render_template,request, redirect, url_for, flash, session, logging
import hashlib
import models as dbHandler
from functools import wraps
import os

app=Flask(__name__)
app.secret_key = os.urandom(24)
print app.secret_key


def login_req(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash("You need to login First!!!",'danger')
		 	return redirect(url_for("login"))
	return wrap

@app.route("/")
def index():
	if 'logged_in' in session:
		return redirect(url_for("friends"))
	return render_template("homepage.html")

@app.route("/signup",methods=["POST","GET"])
def signUp():
	if 'logged_in' in session:
		return redirect(url_for("friends"))
	if request.method == "POST":
		email=str(request.form['email'])
		fname=str(request.form['fname'])
		lname=str(request.form['lname'])
		phone=str(request.form['phone'])
		name=fname + " " + lname
		password=str(request.form['pass'])
		conpassword=str(request.form['conpass'])
		Pass=hashlib.sha256(password)
		hashPass=Pass.hexdigest()
		user1 = dbHandler.getUser(email)
		user2 = dbHandler.getUser(phone)
		if password == conpassword: 
			if user1 :
				flash("Email-ID Already Exists.",'danger')
				redirect(url_for("signUp"))
			elif user2 :
				flash("Phone Number Already Exists.",'danger')
				return render_template("signup.html")
			else:
				dbHandler.insertUser(email,name,hashPass,phone)	
				return redirect(url_for("login"))
		else:
			flash("Password don't match",'danger')
			return render_template("signup.html")
	return render_template("signup.html")

@app.route("/logout")
@login_req
def logout():
	session.clear()
	flash("You are logged out.",'success')
	return render_template("login.html")
 
@app.route("/login",methods=["POST","GET"])
def login():
	if 'logged_in' in session:
		return redirect(url_for("friends"))
	if request.method == "POST":
		data=str(request.form["data"])
		password=str(request.form["pass"])
		Pass=hashlib.sha256(password)
		hashPass=Pass.hexdigest()
		user = dbHandler.getUser(data)
		userPass = dbHandler.getUserPass(data)
		if user :
			if userPass[0] == hashPass:
				session['logged_in']=True
				session['email']=user[1]
				session['name']=user[0]
				return redirect(url_for("friends"))
			else:
				flash("Invalid Password",'danger')
		 		return render_template("login.html")
		else:
			flash("No such user",'danger')
			return render_template("login.html")
		cursor.close()
	else:
		return render_template("login.html")


@app.route("/friends",methods=["POST","GET"])
@login_req
def friends():
	friends = dbHandler.getFriends(session['email'],"friends")
	amount = dbHandler.getTotal(session['email'])
	
	if request.method == "POST":
		settle = request.form.get('settle')
		money = request.form.get('money')
		if money:
			user2 = str(request.form['money'])
			return redirect(url_for("transaction",user2=user2))
		elif settle:
			dbHandler.settle(session['email'],settle)
			name = dbHandler.getName(settle)
			flash("You are now settled up with "+name,'success')
			return redirect(url_for("friends"))
	return render_template('friends.html',friends=friends,amount =amount)

@app.route("/activities",methods=["POST","GET"])
@login_req
def activities():
	acts = dbHandler.getActs(session['email'])
	return render_template('activities.html',acts=acts,user=session['email'])


@app.route("/transaction+<user2>",methods=["POST","GET"])
@login_req	
def transaction(user2):
	if request.method == "POST":
		description = str(request.form['description'])
		amount = float(request.form['amount'])
		value = int(request.form['options'])
		dbHandler.doTransaction(session['email'],user2,amount,value,description)
		flash("Transaction Recorded",'success')
		return redirect(url_for("friends"))
	return render_template('transaction.html')

@app.route("/friendrequest",methods=["POST","GET"])
@login_req
def friendrequest():
	friends=dbHandler.getFriends(session['email'],"got_request")
	if request.method == "POST":
		user2 = request.form['btn']
		dbHandler.acceptRequest(session['email'],user2)
		flash("Request Accepted",'success')
		return render_template('friendrequest.html')
	return render_template('friendrequest.html',friends=friends)

@app.route("/addfriends",methods=["POST","GET"])
@login_req
def addfriends():
	if request.method == "POST":
		if request.form['btn'] == 'Search':
			data=str(request.form['search'])
			user = dbHandler.getUser(data)
			if user:
				if user[1] == session['email']:
					flash("You cannot send a request to yourself",'danger')
					return render_template("addfriends.html")
				session['addFriend'] = user[1]
				session['addFriendName'] = user[0]
				return render_template('addfriends.html',user=user)
			else:
				flash("No such user",'danger')
				return redirect(url_for("addfriends"))
		else :
			user = request.form['btn']
			status = dbHandler.sendRequest(session['email'],session['addFriend'])
			if status == "sent":
				flash("Friend Request Sent",'success')
			else:
				flash(status+session['addFriendName'],'danger')
			del session['addFriend']
			del session['addFriendName']
			return render_template('addfriends.html')		
	return render_template('addfriends.html')

@app.route("/groups",methods=["POST","GET"])
@login_req
def groups():
	groups = dbHandler.getGroups(session['email'])
	if request.method == 'POST':
		
		if request.form['group_page'] == 'create':
			return redirect(url_for('createGroup'))
		else:
			return redirect(url_for('group_page',id1 = request.form['group_page']))
	
	return render_template('groups.html',groups = groups)

@app.route("/group_page+<id1>",methods=["POST","GET"])
@login_req
def group_page(id1):
	group_name = dbHandler.getGroupFromId(id1)
	members = dbHandler.groupMembers(session['email'],id1)
	comments = dbHandler.getComments(id1)
	if request.method == 'POST':
		if request.form.get('addMember'):
			return redirect(url_for('addMember',id1 = id1))
		if request.form.get('settle'):			
			user = request.form.get('settle')
			dbHandler.settleInGroup(id1,session['email'],user)
			return redirect(url_for('group_page',id1=id1))
		if request.form.get('addTrans'):
			return redirect(url_for("groupTransaction",id1=id1))
		if request.form.get('setGroup'):
			dbHandler.settleGroup(id1,session['email'])
			return redirect(url_for("groups"))
		if request.form.get('comment'):
			comment = request.form.get('comment')
			dbHandler.addComment(id1,comment,session['email'])
			return redirect(url_for('group_page',id1=id1))
	return render_template('group_page.html',group_name = group_name, members = members,comments = comments)

@app.route("/addMember+<id1>",methods=["POST","GET"])
@login_req
def addMember(id1):
	if request.method == "POST":
		user = request.form['user']
		msg1 = dbHandler.checkFriend(session['email'],user)
		msg2 = dbHandler.checkMember(user,id1)
		if msg1 == "no":
			flash("No such user in your friendlist",'danger')
			return render_template('addMember.html')
		elif msg2 == "member":
			flash("Already a member of this group.",'danger')
			return render_template('addMember.html')
		else:
			dbHandler.addNewMember(user,id1)
			flash("Member Added",'success')
			return redirect(url_for('group_page',id1 = id1))
	return render_template('addMember.html')

@app.route("/createGroup",methods=["POST","GET"])
@login_req
def createGroup():
	if request.method == 'POST':
		name = request.form['name']
		dbHandler.insertGroup(name,session['email'])
		return redirect(url_for('groups'))
	return render_template('createGroup.html')


@app.route("/groupTransaction+<id1>",methods=["POST","GET"])
@login_req
def groupTransaction(id1):
	if request.method == 'POST':
		members = dbHandler.groupMembers(session['email'],id1)
		desc = request.form['description']
		amount = float(request.form['amount'])
		am = float(amount/len(members))
		am = round(am,2)
		if request.form['submit'] == "equal":
			mems = []
			for member in members:
				mems.append((member[1],am))
			dbHandler.addGroupTrans(session['email'],id1,mems,desc)
			flash("Transaction Recorded",'success')
			return redirect(url_for('group_page',id1=id1))
		else:
			return redirect(url_for('groupTransactionUnequal',id1=id1,desc=desc,amount=amount))
	return render_template("groupTransaction.html")

@app.route("/groupTransaction+<id1>+unequal+<amount>+<desc>",methods=["POST","GET"])
@login_req
def groupTransactionUnequal(id1,amount,desc):
	members = dbHandler.groupMembers(session['email'],id1)
	am = float(float(amount)/len(members))
	am = round(am,2)
	if request.method == 'POST':
		mems = []
		for member in members:
			amt = request.form[member[1]]
			mems.append((member[1],amt))
		dbHandler.addGroupTrans(session['email'],id1,mems,desc)
		flash("Transaction Recorded",'success')
		return redirect(url_for('group_page',id1=id1))
	return render_template("groupTransactionUnequal.html",desc=desc,amount=amount,members=members,am=am)

@app.route("/groupactivities",methods=["POST","GET"])
@login_req
def groupactivities():
	acts = dbHandler.getGroupActs(session['email'])
	return render_template('groupactivities.html',acts=acts,user=session['email'])


if __name__ == "__main__":
	app.run(debug=True)
