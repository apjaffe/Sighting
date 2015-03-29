# application.py
# Flask server backend for sighting
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
from flask import Flask
from flask.ext.dynamo import Dynamo
from flask import request
from flask import Response
import os
import json
import time

application = Flask(__name__)

os.environ["AWS_ACCESS_KEY_ID"] = "-----"
os.environ["AWS_SECRET_ACCESS_KEY"] = "-----"
os.environ["AWS_REGION"] = "us-east-1"
#os.environ["DYNAMO_ENABLE_LOCAL"] = "False" # default
#os.environ["DYNAMO_LOCAL_HOST"] = "None" # default
#os.environ["DYNAMO_LOCAL_PORT"] = "None" # default

application.config['DYNAMO_TABLES'] = [
	Table('users', schema=[HashKey('username')]),
	Table('groups', schema=[HashKey('name')]),
]

dynamo = Dynamo(application)

#with application.app_context():
#	dynamo.create_all()
def getUser(req):
	try:
		user = dynamo.users.get_item(username = req.args.get('user'))
		return user
	except Exception:
		return None

def getGroup(req):
	try:
		group = dynamo.groups.get_item(name = req.args.get('group'))
		return group
	except Exception:
		return None

def user_info(user):
	result = {'username':user['username'],'groups':listGroups(user['groups']),'success':True}
	return result

def group_info(groupNameStatus):
	groupName = groupNameStatus[2:]
	groupStatus = int(groupNameStatus[:1])
	try:
		group = dynamo.groups.get_item(name = groupName)
	except Exception:
		return None
	result = {'name':group['name'],'status':groupStatus,'description':group['description'],'alerts':listAlert(group['alerts'])}
	return result

def listGroups(groupSet):
	if(groupSet is None): return []
	result = []
	for group in groupSet:
		result.append(group_info(group))
	return result


def listAlert(alertSet):
	if(alertSet is None): return []
	result = []
	for alert in alertSet:
		result.append(json.loads(alert))
	return result

def returnJSON(js):
	return Response(js,mimetype='application/json')

def returnJSONIFY(js):
	return returnJSON(json.dumps(js))

def success(succeeded):
	return returnJSON(json.dumps({'success':succeeded}))

def groupInList(group,lists):
	for eachGroup in lists:
		if(group==eachGroup[2:]): return True
	return False

@application.route('/')
def hello_world():
	return 'Node.js is the only real dev language'


@application.route('/register')
def register():
	try:
		dynamo.users.put_item(data={
			'username': request.args.get('user'),
			'password': request.args.get('pass'),
			'groups': set([])
		})
		return success(True)
	except Exception:
		return success(False)


#user, group, title, lat, lng
@application.route('/add_alert')
def add_alert():
	user = getUser(request)
	if(user is None): return success(False)
	group = getGroup(request)
	if(user is None): return success(False)
	title = request.args.get('title')
	lat = request.args.get('lat')
	lng = request.args.get('lng')
	times = int(time.time())

	alert = json.dumps({"user":user["username"],"title":title,"lat":lat,"lng":lng,"time":times})
	if(group['alerts'] is None): group['alerts']=set()
	group['alerts'].add(alert)
	group.save()

	return returnJSON(alert)

def addGroupToUser(groupName,groups,user,status):
	if(groups is None):
		user["groups"]=set()
		groups=user["groups"]
	if (status+":"+groupName) not in groups:
		for i in xrange(10):
			tmp = str(i)+":"+groupName
			if (tmp in groups):
				groups.remove(tmp)

		groups.add(status+":"+groupName)
		user["groups"]=groups
		user.save()
		return success(True)
	else:
		return success(False)

#user
@application.route('/recommend')
def recommendedGroups():
	user = getUser(request)
	if(user is None): return success(False)
	user_groups = user["groups"]
	if(user_groups is None): user_groups= set()
	all_groups = dynamo.groups.scan()
	result = []
	for group in all_groups:
		if(not groupInList(group["name"],user_groups)):
			result.append(group_info("0:"+group["name"]))
	return returnJSONIFY(result)

#user, group, status
#description (if new group)
@application.route('/create')
@application.route('/join')
def joinGroup(): # used to join or create a group
	user = getUser(request)
	if(user is None): return success(False)
	group = getGroup(request) #determine if group exists already
	groupName = request.args.get('group')
	groups = user['groups']
	if(group is not None):
		return addGroupToUser(groupName,groups,user,request.args.get('status'))
	else:
		try:
			dynamo.groups.put_item(data={
				"name": groupName,
				"description": request.args.get('description'),
				"alerts": []
			})
			return addGroupToUser(groupName,groups,user,request.args.get('status'))
		except:
			return success(False)

#user, group, status
@application.route('/update')
def updateGroup(): #update group status
	user = getUser(request)
	if(user is None): return success(False)
	group = getGroup(request)
	if(group is None): return success(False)
	groupName = request.args.get('group')
	status = request.args.get('status')
	groups = user["groups"]
	if(groups is None):
		user["groups"]=set()
		groups=user["groups"]

	for i in xrange(10):
		tmp = str(i)+":"+groupName
		if (tmp in groups):
			groups.remove(tmp)

	if (status+":"+groupName) not in groups:
		groups.add(status+":"+groupName)

	user["groups"]=groups
	user.save()

	return success(True)
#user
@application.route('/user_data')
def user_data():
	user = getUser(request)
	if(user is None): return success(False)
	return returnJSONIFY(user_info(user))

@application.route('/login')
def login():
	user = getUser(request)
	if(user is None): return success(False)
	if user['password']==request.args.get('pass'):
		return returnJSONIFY(user_info(user))
	else:
		return success(False)

#user, status, group
@application.route('/quit')
def quitGroup():
	user = getUser(request)
	if(user is None): return success(False)
	try:
		status = request.args.get('status')
		group = request.args.get('group')
		groupString = status + ":" + group
	except: return success(False)
	groups = user['groups']
	if groups is not None and groupString in groups:
		groups.remove(groupString)
		user.save()
		return success(True)
	else:
		return success(False)

@application.route('/alerts')
def getAlerts():
	user = getUser(request)
	if(user is None): return success(False)
	groupData = user['groups']
	groups = []
	for groupInfo in groupData:
		groupString = groupInfo[2:]
		status = groupInfo[0]
		groups.append((groupString, status))
	alerts = []
	for item in groups:
		status = item[1]
		try:
			group = dynamo.groups.get_item(name = item[0])
			for alert in listAlert(group['alerts']):
				alert['group'] = group
				alert['status'] = status
				alerts.append(alert)
		except: continue # group does not exist, just keep moving
	result = {'success':True, 'alerts':alerts}
	return json.dumps(result)

if __name__ == '__main__':
	application.run(host='0.0.0.0', port=8080, debug=True)
