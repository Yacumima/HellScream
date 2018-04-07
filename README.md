# HellScream
局域网ssh服务地址自动发现

适用于局域网内自动发现并登录ssh服务主机。

示例:（Ubuntu Server）在 /etc/rc.local中加入 "/<you_path>/HellScream.py -s ", 也可以指定监听端口: "/<you_path>/HellScream.py -s -p 6688 ", 这样，服务器会有一个广播监听， 然后客户端就可以执行:"/<you_path>/HellScream.py -c"来发送广播获取ssh服务地址，也可以执行:"/<you_path>/HellScream.py -s -l userName@hostName"直接唤起ssh登陆.
