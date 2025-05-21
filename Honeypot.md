# Honeypot

##  Hfish

!!! note "相关资料"
    [CSDN-HFish](https://blog.csdn.net/qq_49422880/article/details/121937941)<br>
    [CentOS7](https://www.cnblogs.com/tanghaorong/p/13210794.html)<br>
    [官方手册](https://hfish.net/#/highinteractive)<br>



本次安装在Docker中部署，首先确认Docker已经安装

```
docker version
```

在Docker中运行新的容器`hfish`，这里使用的镜像是`threatbook/hfish-server`

```
docker run -itd --name hfish \
-v /usr/share/hfish:/usr/share/hfish \
--network host \
--privileged=true \
threatbook/hfish-server:latest
```

接下来需要配置阿里云ESC安全组的入方向设置，如下图所示

![image-20250518083717334](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505180837473.png)

然后可以登录控制台首先，来查看攻击等相关信息

```
登陆地址：https://[server]:4433/web/
初始用户名：admin
初始密码：HFish2021
```

![image-20250518083835591](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505180838755.png)



------

下面是另一种github源蜜罐

```
sudo docker pull imdevops/hfish
```

![image-20250514153440215](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505141534343.png)



```
sudo docker run -d --name hfish \
  -p 21:21 -p 2222:22 -p 23:23 -p 69:69 -p 3306:3306 -p 5900:5900 -p 6379:6379 -p 8080:8080 -p 8081:8081 -p 8989:8989 -p 9000:9000 -p 9001:9001 -p 9200:9200 -p 11211:11211 \
  -p 80:80 -p 443:443 -p 4433:4433 -p 7879:7879 \
  --restart=always imdevops/hfish:latest
```

![image-20250514153716484](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505141537566.png)

```
sudo docker ps -a
```

![image-20250514153711092](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505141537202.png)

```
sudo systemctl start firewalld
```



```
sudo firewall-cmd --zone=public --add-port=21/tcp --permanent
sudo firewall-cmd --zone=public --add-port=22/tcp --permanent
sudo firewall-cmd --zone=public --add-port=23/tcp --permanent
sudo firewall-cmd --zone=public --add-port=80/tcp --permanent
sudo firewall-cmd --zone=public --add-port=443/tcp --permanent
sudo firewall-cmd --zone=public --add-port=3306/tcp --permanent
sudo firewall-cmd --zone=public --add-port=6379/tcp --permanent
sudo firewall-cmd --zone=public --add-port=9000/tcp --permanent
sudo firewall-cmd --zone=public --add-port=9001/tcp --permanent
sudo firewall-cmd --reload
```

![image-20250514153550899](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505141535976.png)



```
sudo netstat -tuln | grep -E '21|22|23|80|443|3306|6379'
```

![image-20250514153609472](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505141536561.png)



```
sudo docker exec -it c26f73155ab6 /bin/sh
```

![image-20250514153908933](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505141539986.png)





```
cat config.ini
```

查看配置日志

![image-20250514153954719](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505141539866.png)



```
sudo docker logs c26f73155ab6
```

![image-20250514153758033](https://zyysite.oss-cn-hangzhou.aliyuncs.com/202505141537108.png)


之后就可以查看攻击日志了



## Conpot



```
sudo docker pull honeynet/conpot
```







```
sudo docker run -d -p 7070:7070 honeynet/conpot
```



或者



```
docker run -it -p 80:80 -p 102:102 -p 502:502 -p 161:161/udp --network=bridge honeynet/conpot
```

查看Conpot 的配置文件

```
cd /home/conpot/.local/lib/python3.6/site-packages/conpot-0.6.0-py3.6.egg/conpot
cat testing.cfg
```

log文件

```
/var/log/conpot/conpot.log
```

