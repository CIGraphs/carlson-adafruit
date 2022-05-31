from flask import Flask, redirect, url_for, render_template, request
import json
import csv

import psycopg2
import pswdconf

import re

import pandas as pd

app = Flask(__name__)


#connectingTo = 'local'
connectingTo = 'remote'

if connectingTo == 'local':
    ip = pswdconf.localIP
    user = pswdconf.localuser
    pwd = pswdconf.localpwd
    db = pswdconf.localdb
else:
    ip = pswdconf.remoteIP
    user = pswdconf.remoteuser
    pwd = pswdconf.remotepwd
    db = pswdconf.remotedb

#GraphDB name
GraphDBname = 'adafruit'



# Redirect to another url (by def name
@app.route("/")
def redirecthome():
    
    
    return redirect(url_for("home"))

#you can have mutiple url locations use the same def
@app.route("/home/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    pageTitle = "Adafruit Application Search"
    
    if request.method == "GET":
         return render_template(
            "main.html", 
            title = pageTitle, 
            humanReadableQueryVerify = None,
            res_fields = None,
            res_data = None,
            #Not used, but still in template
            progress_bar_pct = 0, step_running_name = "not used"
            )
    elif request.method == "POST":
        #Someone Has at least clicked the "Magic" button grab the value from the webpage
        #NOTE never trust the end user you should make sure the request is valid and not malicious :)
        webquestion = request.form["nmwebquestion"]

        processedQuestionDictionary = extractIntent(webquestion)
        
        if processedQuestionDictionary == "Error":
            return redirect(url_for("home"))
        
        queryverify = processedQuestionDictionary['humanReadableQueryVerify']
        fields = processedQuestionDictionary['res_fields']
        data = processedQuestionDictionary['res_data']
        
        #return processedQuestionDictionary
        
        #Link to the main.html pages in the templates folder for rendering in the user's web browser
        
        
        return render_template(
            "main.html", 
            title = pageTitle, 
            humanReadableQueryVerify = queryverify,
            res_fields = fields,
            res_data = data,
            #Not used, but still in template
            progress_bar_pct = 0, step_running_name = "not used"
            )
      
      
#This is the main code to determine the users intent To check if the webpage is working pass TEST to this
def extractIntent(UserInput):
    if UserInput == "":
        #You could do some feedback but for now it just goes back home
        return "Error"
    
    if UserInput == "TEST":
        TestDict = {
            'humanReadableQueryVerify': "The Intent of your request is to test Flask Output",
            'res_fields': ['Data Colunm Name 1', '2nd Data Column', 'URL'],
            'res_data': [
                ["This is the data in the first Column first row", "2nd column first row", 'https://www.google.com'],
                ["first Column 2nd row", "2nd column 2nd row", 'http://www.yahoo.com'],
                ["first Column 3nd row", "2nd column 3nd row", 'http://www.bing.com']
                       ]
            }
        return TestDict
    
    if UserInput == "TEST SQL":
        SQL_Results = runSQL("""
            SELECT CURRENT_DATE, random() as Rand_num, table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema not in ('pg_catalog', 'information_schema')
            ORDER BY table_schema,table_name;
            """)
        SQL_Results['humanReadableQueryVerify'] = "Testing PostgreSQL and Database Connection"
        
        return SQL_Results

    if UserInput == "TEST OpenCypher":
        SQL_Results = runCypher("""
            SELECT * FROM cypher('adafruit', $$ MATCH (a) RETURN a.entity, label(a), id(a) $$) as (NodeName agtype, NodeLabel agtype, NodeID agtype);
            """)
        SQL_Results['humanReadableQueryVerify'] = "Testing PostgreSQL and Cypher Query Results"
        
        return SQL_Results

def runSQL(qry):
    conn = psycopg2.connect(host=ip, database=db, user=user, password=pwd)
    cur = conn.cursor()

    #Test the connection and cursor by selecting the current_date from the postgreSQL server   
    cur.execute(qry)

    data_rows = []
    #Return all the column names
    fields = [desc[0] for desc in cur.description]
    for row in cur:
        data_rows.append(row)
    queryResults = {'res_fields': fields,
                    'res_data': data_rows
                    }
    return queryResults
 
def runCypher(qry):

 
    conn = psycopg2.connect(host=ip, database=db, user=user, password=pwd)
    cur = conn.cursor()
    
    #Load Prereqs for Cypher
    cur.execute("LOAD '$libdir/plugins/age';")
    cur.execute("SET search_path = ag_catalog, '$user', public;")

    #Test the connection and cursor by selecting the current_date from the postgreSQL server   
    cur.execute(qry)

    data_rows = []
    #Return all the column names
    fields = [desc[0] for desc in cur.description]
    for row in cur:
        data_rows.append(row)
    queryResults = {'res_fields': fields,
                    'res_data': data_rows
                    }
    return queryResults
    
if __name__ == "__main__":
    #adding the host 0.0.0.0 any computer on the local network should be albe to open the webpage
    app.run(host='0.0.0.0', debug=True, port = 8080)
