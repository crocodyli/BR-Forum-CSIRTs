# Instalando a Cuckoo

Para auxiliar na instalação da Cuckoo, coletei alguns erros comuns e compilei neste guia para subir o serviço da Cuckoo em um ambiente local, o foco é apresentar diretamente a sua operação. 

Sistema operacional utilizado para o laboratório:

- Ubuntu Desktop 18.04.6 LTS *server*
- Núcleos do processador 2 a 4
- Memória: 6GB (depende)
- Armazenamento 100GB
- Conexão para realizar via SSH com outras ferramentas.


## Instalação do SO e configuração no VirtualBox

1. **Instale o Ubuntu**
2. Após a instalação é necessário **habilitar a virtualização da Máquina**, caso a opção do VirtualBox não esteja habilitada.
3. Deixe a VM instalar as suas atualizações

Na sua máquina, abra o CMD com permissão de administrador. 

```
CMD> SET PATH=%PATH%;C:\Program Files\Oracle\VirtualBox
CMD> vboxmanage list vms
CMD> vboxmanage modifyvm "(nome da maquina)" --nested-hw-virt on
```

Resultará em:

![1](https://github.com/user-attachments/assets/e105d9f4-8405-4178-ba6e-d347cf014689)

Ele ficará da seguinte forma no Virtual Box após a habilitação

**Sistema -> Processador -> “Habilitado VT-x/AMD-V Aninhado”.**

![image](https://github.com/user-attachments/assets/6a457312-c90f-430a-8538-e2530a1e7a27)

*Obs: o comando só irá funcionar se a VM não estiver ainda com o status de salvo, ou seja, com SNAPSHOT.* 

## Altere a configuração de rede da máquina para IP estático

1. Altere a placa de rede da máquina virtual para **Modo Bridge**. 
2. Após a instalação do Ubuntu

```
sudo su
sudo apt update && apt upgrade -y
```

3. Descubra o endereço e nome da sua interface.

![image](https://github.com/user-attachments/assets/ac7b70ed-0ed1-4739-bb7b-4b5f96508eba)

4. Configure o arquivo responsável por definir o endereço de IP estático.

```
sudo nano /etc/netplan/00-installer-config.yaml
```

Mantenha o arquivo de configuração com o seguinte formato .

```
#This is the network config written by 'subiquity'
network:
	version: 2
	ethernets:
		enp0s3:
		dhcp4: false
		addresses: [192.168.2.180/24]
		gateway4: 192.168.2.1
		optional: true
		nameservers:
			addresses: [8.8.8.8, 1.1.1.1]
```


![image](https://github.com/user-attachments/assets/58781062-8d57-4793-8c8b-78f878a241e4)

5. Aplique as alterações com o comando abaixo, lembrando ainda de apertar o ENTER em até 120 segundos para confirmar a alteração.

```
sudo netplan try
ENTER
ip a
sudo reboot now
```


6. Atualize o Ubuntu e comece a instalar as dependências do SO.

```
sudo apt update && sudo apt upgrade -y
sudo apt install python2.7 python-pip -y
sudo apt-get install python python-pip python-dev libffi-dev libssl-dev -y
sudo apt-get install python-virtualenv python-setuptools -y
sudo apt-get install libjpeg-dev zlib1g-dev swig -y
sudo apt-get install mongodb -y
sudo apt-get install postgresql libpq-dev -y
sudo apt install virtualbox -y
sudo apt-get install tcpdump apparmor-utils -y
```

Existem situações que serão necessário criar um novo usuário, neste caso poderá utilizar o comando: 

```
sudo adduser --disabled-password --gecos "" <usuário>
```
*a opção --disabled-password é utilizada para desativar a senha para a conta de usuário. Isso é útil em situações em que a conta é utilizada de maneira automatizada. A cuckoo pode utilizar a conta para executar máquinas virtuais e realizar análises de malware de forma isolada e controlada.*

6.1. Caso você não crie um usuário, é importante adicionar o seu usuário no momento nos arquivos de sudoers.

```
sudo nano /etc/sudoers
user       ALL=(ALL:ALL) ALL
``` 

7. Continue com a configuração da Sandbox. 

```
sudo groupadd pcap
sudo usermod -a -G pcap <usuário>
sudo chgrp pcap /usr/sbin/tcpdump
sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
```

*#Util para quando o usuário da cuckoo automatizado precisa de permissões para realizar a captura de pacotes de rede etc.*

*Importante, se apresentar erros, verifique se o tcpdump está rodando.*

```
apt install tcpdump
readlink -f /usr/sbin/tcpdump
```

8. Continue a instalação, caso não apresente erros: 

```
getcap /usr/sbin/tcpdump
sudo aa-disable /usr/sbin/tcpdump
```

9. Instale ainda outras bibliotecas necessárias para a Cuckoo

```
sudo apt-get install swig
sudo pip install m2crypto==0.38.0
```

## Opção da instalação do Volatility2

```
#Instalação do Volatility2
cd /home
sudo apt install -y python python-dev dwarfdump build-essential yara zip
sudo pip2 install pycrypto yara-python distorm3==3.4.4
sudo git clone https://github.com/volatilityfoundation/volatility.git
cd volatility/
sudo python2 setup.py install
vol.py -h <verificar se foi bem sucedido>
```` 

## Controlador Remoto da VM 
sudo apt install libguac-client-rdp0 libguac-client-vnc0 libguac-client-ssh0 guacd -y

*A imagem utilizada para subir a Cuckoo não possuí interface gráfica, com isto pode ocorrer erros, porém, caso utilize uma imagem gráfica do Windows, poderá rodar sem problemas*. 

10. Continue a instalação de rotina da Cuckoo

```
sudo usermod -a -G vboxusers <usuário>

#Caso tenha criado um novo user, adicione uma senha para este outro usuário em um novo terminal:

sudo passwd <usuario>
sudo nano /etc/sudoers

#Adicione também o user ao sudoers.
sudo su <usuário>

#Caso não tenha criado, seguir a etapa a seguir: 
```

```
cd ..
sudo nano ./cuckoo-setup-virtualenv.sh
````

```
#!/usr/bin/env bash
# NOTES: Run this   script as: sudo -u <USERNAME> cuckoo-setup-virtualenv.sh
# install virtualenv
sudo apt-get update   && sudo apt-get -y install virtualenv
# install   virtualenvwrapper
sudo apt-get -y   install virtualenvwrapper
echo "source   /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc
# install pip for   python3
sudo apt-get -y   install python3 
sudo apt-get -y   install python3-pip
# turn on bash   auto-complete for pip
pip3 completion   --bash >> ~/.bashrc
# avoid installing   with root
pip3 install --user   virtualenvwrapper
echo "export   VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
echo "source   ~/.local/bin/virtualenvwrapper.sh" >> ~/.bashrc
export   WORKON_HOME=~/.virtualenvs
echo "export   WORKON_HOME=~/.virtualenvs" >> ~/.bashrc
echo "export   PIP_VIRTUALENV_BASE=~/.virtualenvs" >> ~/.bashrc
```

```
sudo chmod +x cuckoo-setup-virtualenv.sh
sudo -u <USERNAME> ./cuckoo-setup-virtualenv.sh 
source ~/.bashrc
mkvirtualenv -p python2.7 cuckoo-server
pip install -U pip setuptools
pip install -U cuckoo
````

*Para que necessite sempre retornar ao ambiente virtual criado para ajuste e continuar a configuração ou operação da cuckoo, é necessário utilizar o seguinte comando:*

```
workon cuckoo-server 
#neste caso o nome foi definido no comando mkvirtualenv
```


## Download da Máquina Win7 

```
sudo wget https://cuckoo.sh/win7ultimate.iso

#Se não funcionar, virtualize o server e use a sua .iso

sudo wget http://<IP>:PORTA/win7ultimate.iso
```

Lembrando que caso você não tenha a imagem ou esteja disponível para download, é necessário realizar a busca da ISO utilizada pela Cuckoo. 

11. Configure a referida máquina virtual

```
sudo mv win7ultimate.iso /home/<user>
sudo mkdir /mnt/win7
sudo chown <user>:<user> /mnt/win7/
cd /home/<use>
sudo mount -o ro,loop win7ultimate.iso /mnt/win7
sudo apt-get -y install build-essential libssl-dev libffi-dev python-dev genisoimage
sudo apt-get -y install zlib1g-dev libjpeg-dev
sudo apt-get -y install python-pip python-virtualenv python-setuptools swig
pip install -U vmcloak
vmcloak-vboxnet0
```

### Atenção sobre o desempenho:

Nesta etapa é bem importante entender os recursos utilizados pela máquina virtual. 

```
vmcloak init --verbose --win7x64 win7x64base --cpus 2 --ramsize 2048

#ou

vmcloak init --verbose --win7x64 win7x64base --cpus 1 --ramsize 2048

#Caso o 2 cpus der erro usar o comando acima. 
#Não esquecer de remover a criada antes de executar o outro comando
```

12. Continue com a manipulação do dispositivo e da máquina virtual:

```
vmcloak clone win7x64base win7x64cuckoo
vmcloak list deps
vmcloak install win7x64cuckoo ie11
vmcloak snapshot --count 1 win7x64cuckoo 192.168.56.101
vmcloak list vms
```` 

13. Teste para ver se a cuckoo está instalada:

```
cuckoo init
cd .cuckoo/
ls
cuckoo community
```

### Configuração da rede após a instalação: 

```
sudo sysctl -w net.ipv4.conf.vboxnet0.forwarding=1
sudo sysctl -w net.ipv4.conf.enp0s3.forwarding=1
sudo iptables -t nat -A POSTROUTING -o enp0s3 -s 192.168.56.0/24 -j MASQUERADE
sudo iptables -P FORWARD DROP
sudo iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -s 192.168.56.0/24 -j ACCEPT
```

### Configurações das Máquinas Virtuais nas configurações da Cuckoo

```
workon <nome do ambient virtual> (cuckoo-server)
cd conf/
ls
nano routing.conf
```

*Necessário alterar a interface de rede de routing para a sua interface de rede, no meu caso foi a enp0s3.*


![image](https://github.com/user-attachments/assets/be8461f4-07fa-4da5-8ce9-b4f1e7b722cf)


```
while read -r vm ip; do cuckoo machine --add $vm $ip; done < <(vmcloak list vms)
```

Altere o arquivo virtualbox.conf para informar qual a VM utilizada para análise dos artefatos. 

```
workon <nome do ambient virtual> (cuckoo-server)
cd ~/.cuckoo/conf
nano virtualbox.conf
```


![image](https://github.com/user-attachments/assets/1e0b2804-2a2c-4322-9d7b-cb39f57adad6)


Deixar ainda direto da porta 5000-5050 para o endereçod e IP dentro das chaves, igual a imagem abaixo. 


![image](https://github.com/user-attachments/assets/e39d29f3-db74-4e17-9a6d-6de5c0670e59)

Altere as configurações do MongoDB. 


```
sudo systemctl status mongodb
sudo systemctl start mongodb
nano reporting.conf
#Colique “yes” na parte do MongoDB
```


![image](https://github.com/user-attachments/assets/26ce9c0d-02c1-4bfb-acca-73472e5c1791)


Pronto, você concluíu a instalação da Cuckoo, agora precisa apenas iniciar o serviço com 3 terminais. 

```
#Duplique a aba em um novo terminal
workon cuckoo-server
cuckoo rooter --sudo --group sudo

#Duplique a aba em um novo terminal
workon cuckoo-server
cuckoo web --host 192.168.2.180 --port 8080

#Duplique a aba em um novo terminal
workon cuckoo-server
cuckoo -d

#Forçar o desligamento do processo da cuckoo caso esteja com problemas no processo. 
pkill cuckoo
```

A cuckoo irá apresentar a seguinte tela: 


![2 pn](https://github.com/user-attachments/assets/90c077bf-25b1-4111-9f1b-54db9d3988a7)




