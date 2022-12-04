import os

currentPath = os.getcwd().replace('\\','/')
accesslg = currentPath+'/log/gunicorn_access.log'
errorlog = currentPath+'/log/gunicorn_error.log'
port = 20000
while port<20005:
    os.system("nohup /Library/Frameworks/Python.framework/Versions/3.10/bin/gunicorn -w 1 -b 0.0.0.0:%d --error-logfile %s --access-logfile %s  trade_robot:app&"%(port,errorlog,accesslg))
    port = port + 1