from __future__ import print_function
import csv
import sys
from socket import gethostname
import time


from flask import Flask, jsonify, abort, request
from flask_cors import CORS, cross_origin

import logging
import pymysql

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*","methods":"POST,DELETE,PUT,GET,OPTIONS"}})


hostnm = gethostname()
ip = sys.argv[1]



def createConnection():
	connectString = ip+":3306/mydatabase"
	hostname = connectString[:connectString.index(":")]
	database = connectString[connectString.index("/")+1:]
	conn = pymysql.connect(host=hostname, 
                           port=3306, 
                           user="root", 
                           passwd="KAnika##123", 
                           db=database,
                           cursorclass=pymysql.cursors.DictCursor)
	return conn                   

createConnection()

def setupDB():
    conn = createConnection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS PREDICTION (ID INTEGER NOT NULL AUTO_INCREMENT,Date VARCHAR(255),Domain_A VARCHAR(255),Domain_P VARCHAR(10),Title VARCHAR(255),PRIMARY KEY (ID));''')
    conn.commit()
    cur.close()
    conn.close()
    return 'The PREDICTION table was created succesfully'


@app.route('/')
def index():
	return ' The application is running!'

@app.route('/predictions')
def predictions():
    conn = createConnection()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM PREDICTION''')
    results = cur.fetchall()	
    cur.close()
    conn.close()
    return jsonify( results)

@app.route('/save_to_table', methods=['POST'])
def create_employee():
	setupDB()
	conn = createConnection()
	cur = conn.cursor()
	try:
		timestamp = time.time()
		cur.execute('''INSERT INTO PREDICTION (Date, Domain_A, Domain_P, Title) 
	                VALUES('%s','%s','%s','%s') '''%(str(timestamp),request.json['Domain_A'],request.json['Domain_P'],request.json['Title']))
		conn.commit()
		message = {'status': 'New prediction record is created succesfully'}
		cur.close()
	except Exception as e:
		logging.error('DB exception: %s' % e)
		message = {'status': 'The creation of the new prediction record failed.'}
	conn.close()
	return jsonify(message)

	
if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8055)
