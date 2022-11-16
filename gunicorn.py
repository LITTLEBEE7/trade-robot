# gunicorn配置文件

# 并行的工作进程数
workers = 4
# 指定每个工作者的线程数
threads = 2
# 监听内网的端口
bind = '127.0.0.1:8090'
# 设置守护进程
daemon = 'false'
# 设置最大并发量
worker_connections = 2000
# 设置访问日志和错误信息日志路径
accesslg = '/log/gunicorn_access.log'
errorlog = '/log/gunicorn_error.log'
# 设置日志等级
loglevel = 'warning'