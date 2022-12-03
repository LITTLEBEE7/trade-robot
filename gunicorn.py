# gunicorn配置文件
# import multprocessing

# 并行的工作进程数
import multiprocessing
import os

currentPath = os.getcwd().replace('\\','/')
# workers = 4
workers = multiprocessing.cpu_count()*2+1
# 指定每个工作者的线程数
threads = 2
# 监听内网的端口
bind = '0.0.0.0:80'
# 设置守护进程
daemon = 'false'
# 设置最大并发量
worker_connections = 2000
# 设置访问日志和错误信息日志路径
accesslg = currentPath+'/log/gunicorn_access.log'
errorlog = currentPath+'/log/gunicorn_error.log'
# 设置日志等级
loglevel = 'warning'