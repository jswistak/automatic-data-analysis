# Python with ssh server
FROM python:3.10-bullseye

RUN apt-get update && apt-get install -y openssh-server

ARG SSH_PASSWORD
ARG SSH_USERNAME
RUN useradd -rm -d /home/remoteuser -s /bin/bash -g root -G sudo -u 1000 $SSH_USERNAME
RUN echo "remoteuser:$SSH_PASSWORD" | chpasswd

RUN service ssh start

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]