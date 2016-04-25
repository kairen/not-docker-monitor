# Collect Docker Meters
本專案透過 RabbitMQ 來收集 Docker Usage 資料。

# 安裝與執行
首先安裝 python 與 python-pip 套件：
```sh
$ sudo apt-get install -y git python-pip
$ sudo pip install --upgrade pip
```

從 Git Server 將 Repositiory 下載至要執行的節點上：
```sh
$ git clone https://github.com/kairen/not-docker-monitor.git
$ cd not-docker-monitor
```

安裝```docker-monitor```服務套件：
```sh
$ sudo pip install .
```
> 也可以透過以下方式安裝：
```sh
$ sudo python setup.py install
```

完成後，即可透過以下指令執行（目前還沒完成 Service 方式執行）：
```sh
$ sudo docker-monitor \
--config-file etc/docker-monitor/docker-monitor.conf
```