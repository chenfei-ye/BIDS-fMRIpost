## Docker本地安装

以下分别提供Ubuntu系统和Centos系统的docker 安装方式

### Ubuntu OS
1. 更换国内软件源，推荐中国科技大学的源，稳定速度快（可选）
```
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak 
sudo sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list 
sudo apt update
```
2. 安装需要的包
```
sudo apt install apt-transport-https ca-certificates software-properties-common curl
```
3. 添加 GPG 密钥，并添加 Docker-ce 软件源，这里还是以中国科技大学的 Docker-ce 源为例
```
curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg | sudo apt-key add - 
sudo add-apt-repository "deb [arch=amd64] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu \ 
$(lsb_release -cs) stable"
```
4. 添加成功后更新软件包缓存
```
sudo apt update
```
5. 安装 Docker-ce
```
sudo apt install docker-ce
```
6. 设置开机自启动并启动 Docker-ce（安装成功后默认已设置并启动，可忽略）
```
sudo systemctl enable docker 
sudo systemctl start docker
```
7. 测试运行
```
sudo docker run hello-world
```
8. 添加当前用户到 docker 用户组，可以不用 sudo 运行 docker（可选）
```
sudo groupadd docker 
sudo usermod -aG docker $USER
```
9. 测试添加用户组（可选）
``` 
docker run hello-world
```


### Centos OS
```
sudo yum remove docker  docker-common docker-selinux docker-engine
yum -y install yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce-17.12.0.ce
sudo systemctl start docker
sudo systemctl enable docker
docker version
```



