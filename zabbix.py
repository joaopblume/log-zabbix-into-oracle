#! /usr/bin/python3

# import needed libs
import config_oracle
import config_mysql
import mysql.connector
import sys
import ast
import os
from datetime import datetime
import cx_Oracle

# set env LD_LIBRARY_PATH var
if 'LD_LIBRARY_PATH' not in os.environ:
    os.environ['LD_LIBRARY_PATH'] = '/usr/lib/oracle/18.5/client64/lib'
    try:
        os.execv(sys.argv[0], sys.argv)
    except:
        print('failed')


# control variables for init and end of strings
init = 1000
end = 0

# get the parameters passed by zabbix in the python script call
parameters = '{' + sys.argv[1] + '}'  # transform it to str json model
parameters = parameters.replace('\n', '')  # avoid scapes

# transform to json properly
try:
    parameters = ast.literal_eval(parameters)
except:
    e = open('/var/lib/zabbix/erros.txt', 'w')
    e.write(parameters)
    e.close()

# get the keys from json to use it as variables
event_id = parameters['event_id']
host = parameters['host']
problem = parameters['problem']
date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
severity = parameters ['severity']
hostgroup = parameters['hostgroup']
trigger_id = parameters['trigger_id']
status = parameters['status']

# log the parameters entries
log = open('/var/lib/zabbix/teste.txt', 'w')
log.write(date + ' - ')
log.write(str(parameters))

# connect to oracle using a config db file
oracle_connection = cx_Oracle.connect(f'{config_oracle.USERNAME}/{config_oracle.PASSWD}@//{config_oracle.HOST}:{config_oracle.PORT}/{config_oracle.SERVICE_NAME}')
# create an oracle cursor
oracle_cursor = oracle_connection.cursor()

# connect to mysql using a config db file
mysql_connection = mysql.connector.connect(host=config_mysql.HOST,
                                         port=config_mysql.PORT,
                                         user=config_mysql.USERNAME,
                                         passwd=config_mysql.PASSWD,
                                         database=config_mysql.DATABASE)
# create a mysql cursor
mysql_cursor = mysql_connection.cursor()

# get the description from triggers from trigger_id variable
mysql_cursor.execute(f"SELECT description FROM triggers WHERE triggerid='{trigger_id}'")
description = mysql_cursor.fetchone()[0]
description = description.decode()

# remove parameters inside "{}" and the keys
atual = 0
final = len(description) - 1
for char in description:
    if char == '{':
        init = description.index(char)
    elif char == '}':
        end = description.index(char)
    
        if init < end:
            description = description[:init] + description[end+1:]
            description = ' '.join(description.split())
            final = len(description) - 1
# remove any special chars
while True:
    if not description[atual].isalnum():
        if description[atual] != ' ':
            description = description[:atual] + description[atual+1:]
            final-=1
    
    if atual >= final:
        break
    else:
        atual+=1
log.write(description)

# insert in oracle table, incoming zabbix problems
oracle_cursor.execute(f"INSERT INTO logs_zabbix (EVENT_ID, CLIENTE, HOST, PROBLEMA, TRIGGERID, SEVERIDADE, DATA, STATUS, TRIGGER_DESC) VALUES ('{event_id}', '{hostgroup}', '{host}', '{problem}', '{trigger_id}', '{severity}', TO_DATE('{date}', 'yyyy-mm-dd hh24:mi:ss'), '{status}', '{description}')")

# commits
oracle_cursor.execute(f"commit")
