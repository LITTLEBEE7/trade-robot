# strategy_trade_robot
## develop
```
pip3 install -r requirements.txt
```

### set your excahnge apiKey 
#
### startup program
#
#### 1.singal port
```
gunicorn -c gunicorn.py trade_robot:app
```
#### 2.multi-port
```
python setup.py
```
#### you can set port number in setup.py