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

建立一個名稱為```docker-monitor```的使用者：
```sh
$ SERVICE="docker-monitor"
$ sudo useradd --home-dir "/var/lib/${SERVICE}" \
--create-home --system \
--shell /bin/false ${SERVICE}
```

建立 conf 目錄，並複製 conf 檔案到 etc 底下：
```sh
$ sudo mkdir -p /var/run/${SERVICE}
$ sudo mkdir -p /etc/${SERVICE}
$ sudo cp -r etc/docker-monitor/docker-monitor.conf /etc/${SERVICE}/
$ sudo touch /var/lib/${SERVICE}/data.json
$ sudo chown -R ${SERVICE}:${SERVICE} /var/run/${SERVICE}
$ sudo chown -R ${SERVICE}:${SERVICE} /etc/${SERVICE}
$ sudo chown -R ${SERVICE}:${SERVICE} /var/lib/${SERVICE}
```

編輯```/etc/docker-monitor/docker-monitor.conf```檔案，並修改一下：
```
[default]
debug = True
window_time = 1
meters = all
save_path = /var/lib/docker-monitor/data.json

[rabbit_messaging]
username = docker
password = docker
host = localhost
port = 5672
queue = stat

# This value has 'consumer', 'producer', 'None'
role = None

timeout = 60
```

安裝```docker-monitor```服務套件：
```sh
$ sudo pip install .
```
> 也可以透過以下方式安裝：
```sh
$ sudo python setup.py install
```

複製```scripts/docker-monitor```到```/etc/init.d```底下：
```sh
$ sudo cp -r scripts/docker-monitor /etc/init.d/
$ sudo chmod 775 /etc/init.d/docker-monitor
```
完成檔案複製後，使用 update-rc.d 指令設定開機啟動：
```sh
$ sudo update-rc.d docker-monitor defaults
```

啟動 docker monitor 服務：
```sh
$ sudo service docker-monitor start
* Starting docker monitor service ...                                                                                [ OK ]
```
> Debug 可以使用```sudo service docker-monitor systemd-start```。

也可以透過以下指令執行 monitor：
```sh
$ sudo docker-monitor \
--config-file etc/docker-monitor/docker-monitor.conf
```