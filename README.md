# log-zabbix-into-oracle
The ideia is: get the client name, datetime, the host, severity, the problem description and its status which occurs during the day at our monitoring tool Zabbix, so that we can generate a monthly summarized report, grouping by how often a certain problem happens by client using Apex.

1- First of all we should retrieve the informations from Zabbix needed to insert at Oracle. Fortunetly, Zabbix provides some macros that we can use as arguments for some custom action (run a python script everytime a problem with a defined severity occur). 

Using them, we could get the client name, the host which the problem occured, the problem' severity, etc, but not the description (for some reason the macro's tag is being ignored).

The easiest solution is connect to mysql db that Zabbix uses, and running a query inside triggers table we have the description that we need.

2- As the report is going to group problems by frequence, the data needs to be exactly the same for similar problems. The way Zabbix stores them is completly customized, which means our data have some variables inside that causes differences for similar problemas. So we should transform:

The user: CAMILLA.FERRAZ sid: 374 is causing locks.
The user: ALBERTO.ALABAMA sid: 882 is causing locks.

into

The user is causing locks.

in order to use a group by expression inside Oracle Database.

There are some ways to get there, but I made a simple string treatment that remove variables indes { } and any special characters to make it cleaner.

3 - Then we bake our INSERT with all collected data and send to "logs_zabbix" table at Oracle db.
