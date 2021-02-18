
# 注意事项

1. MAC系统中不能设置`--network=host`，此命令在mac下无效。
2. 若通过指定端口号的形式来保证镜像之间互相访问，则会存在网络互通的问题。

综上，不建议在MAC环境下使用`FastDFS`。

3. 若IP地址发送了变化，注意修改`docker`启动时命令中对应的IP地址 和 `client.conf` 中对应的IP地址。
4. `python`第三方模块包的安装建议使用此目录下的`fdfs_client-py-master.zip`，其他方式安装可能内容安装不全。
