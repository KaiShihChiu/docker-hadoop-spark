FROM bde2020/hadoop-base:2.0.0-hadoop3.2.1-java8

MAINTAINER Ivan Ermilov <ivan.s.ermilov@gmail.com>

HEALTHCHECK CMD curl -f http://localhost:9870/ || exit 1

ENV HDFS_CONF_dfs_namenode_name_dir=file:///hadoop/dfs/name
RUN mkdir -p /hadoop/dfs/name
VOLUME /hadoop/dfs/name

# 创建新用户 hadoop 并设置密码
RUN useradd -ms /bin/bash hadoop && echo "hadoop:password" | chpasswd

# 赋予 hadoop 用户 sudo 权限
RUN usermod -aG sudo hadoop

# 创建 /hadoop-data 目录并设置权限
RUN mkdir -p /hadoop-data && chown hadoop:hadoop /hadoop-data && chmod 777 /hadoop-data


ADD run.sh /run.sh
RUN chmod a+x /run.sh

EXPOSE 9870

CMD ["/run.sh"]
