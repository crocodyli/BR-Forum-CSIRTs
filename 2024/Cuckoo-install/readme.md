# Guia para instalação da Cuckoo Sandbox sem GUI para interação.

O presente guia tem como foco a instalação do sistema operacional para análise de malware automatizada para geração de Indicadores de Comprometimento (IOCs) que não serão compartilhados publicamente, apenas armazenados via GTI. 

Observe que ao longo da documentação, é recomendado que seja realizado comandos de **SNAPSHOT**, auxiliando desta forma a instalação e ajustes de erros durante o funcionamento. 


### Referências de instalações:

- [https://www.youtube.com/watch?v=wnMy73SlUn](https://www.youtube.com/watch?v=wnMy73SlUnc)
- https://www.youtube.com/watch?v=QlQS4gk_lFU
- https://www.youtube.com/watch?v=FsF56772ZvU
- https://cuckoo.sh/docs/installation/host/requirements.html#installing-python-libraries-on-ubuntu-debian-based-distributions
- https://hatching.io/blog/cuckoo-sandbox-setup/

### Requisitos
- Ubuntu Desktop 18.04.6 LTS *server*
- Núcleos do processador 2 a 4
- Memória: 6GB (depende)
- Armazenamento 100GB
- Conexão para realizar via SSH com outras ferramentas.

## Instalação do SO e Configuração no VIRTUALBOX

1. **Instale o Ubuntu**
2. Após a instalação é necessário **habilitar a virtualização da Máquina**, caso a opção do VirtualBox não esteja habilitada.
3. Deixe a VM instalar as suas atualizações

Na sua máquina, abra o CMD com permissão do administrador

```
CMD> SET PATH=%PATH%;C:\Program Files\Oracle\VirtualBox
CMD> vboxmanage list vms
CMD> vboxmanage modifyvm "(nome da maquina)" --nested-hw-virt on
```

Resultará em: 
![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/e24506b2-f761-426b-be05-5f9043564e63)

Ele ficará da seguinte forma no Virtual Box após habilitação.
- Sistema -> Processador -> "Habilitado VT-x/AMD-V Aninhado"
![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/cbd2758f-41b0-4674-8573-c885804ac5bc)

*O comando só irá funcionar se a VM não estiver ainda com o status de SNAPSHOT ou SALVO*


## Altere a configuração de rede da máquina para IP estático

1. Altere a placa de rede da máquina virtual para **Modo Bridge**. 
2. Após a instalação do Ubuntu

```
sudo su
sudo apt update && apt upgrade -y
ip a
```
![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/9d9ba93b-ded0-4c33-b4fa-de5b655e0891)

3. Configure o arquivo responsável por definir o endereço de IP estático. 

```
sudo nano /etc/netplan/00-installer-config.yaml
```

Mantenha o arquivo de configuração com o seguinte formato. 

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

![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/2280b11f-9a9a-4888-bec4-d689501487d2)

4. Aplique as alterações com o comando abaixo, lembrando ainda de apertar o ENTER em até 120 segundos para confirmar a alteração.

```
sudo netplan try
ENTER
ip a
sudo reboot now
```

*A dica é observar que o sistema (SO) irá solicitar a tecla ENTER assim que o comando netplan for ativado*

**TIRE O SNAPSHOT (snapshot1)**

## Inicie a Instalação da CUCKOO

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

**TIRE O SNAPSHOT (snapshot2)**

Existem situações que serão necessário criar um novo usuário, neste caso poderá utilizar o comando: 
```
sudo adduser --disabled-password --gecos "" <usuário>
```

*a opção --disabled-password é utilizada para desativar a senha para a conta de usuário. Isso é útil em situações em que a conta é utilizada de maneira automatizada. A cuckoo pode utilizar a conta para executar máquinas virtuais e realizar análises de malware de forma isolada e controlada*

Caso você não crie um usuário, é importante adicionar o seu usuário no momento nos arquivos de sudoers. 

```
sudo nano /etc/sudoers
<usuário> ALL=(ALL:ALL) ALL
```

Continue com a configuração da Sandbox. 

```
sudo groupadd pcap
sudo usermod -a -G pcap <usuário>
sudo chgrp pcap /usr/sbin/tcpdump
sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
```

*Importante, se apresentar erros, verifique se o tcpdump está rodando*
```
apt install tcpdump
readlink -f /usr/sbin/tcpdump
```
Continue a instalação, caso não apresente erros: 
```
getcap /usr/sbin/tcpdump
sudo aa-disable /usr/sbin/tcpdump
sudo apt-get install swig
sudo pip install m2crypto==0.38.0
```

**TIRE O SNAPSHOT (snapshot3)**

Caso queire, é possível instalar a versão do Volatility2

```
cd /home
sudo apt install -y python python-dev dwarfdump build-essential yara zip
sudo pip2 install pycrypto yara-python distorm3==3.4.4
sudo git clone https://github.com/volatilityfoundation/volatility.git
cd volatility/
sudo python2 setup.py install
vol.py -h <verificar se foi bem sucedido>
```

Controlador Remoto da VM
```
sudo apt install libguac-client-rdp0 libguac-client-vnc0 libguac-client-ssh0 guacd -y
```

**TIRE O SNAPSHOT (snapshot4)**

Continue a instalação de rotina da Cuckoo
```
sudo usermod -a -G vboxusers <usuário>

#Caso tenha criado um novo user, adicione uma senha para este outro usuário em um novo terminal
sudo passwd <usuario>
sudo nano /etc/sudoers

#Adicione também o user ao sudoers.
sudo su <usuário>
```

Caso não tenha criado, seguir a etapa abaixo: 

```
cd ..
sudo nano ./cuckoo-setup-virtualenv.sh
```

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
sudo -u <usuário> ./cuckoo-setup-virtualenv.sh 
source ~/.bashrc
mkvirtualenv -p python2.7 <nome env>
pip install -U pip setuptools
pip install -U cuckoo
```

**TIRE O SNAPSHOT (snapshot5)**

Para que necessite sempre retornar ao ambiente virtual criado para ajuste e continuar a configuração ou operação da cuckoo, é necessário utilizar o seguinte comando: 
```
workon <nome env> 
#neste caso o nome foi definido no comando mkvirtualenv 
```

## Download da máquina WIN 7 

A máquina será disponibilizada pelo proprietário deste repositório através de contato ou no futuro, disponibilizado através de Link de armazenamento. 

```
sudo wget https://cuckoo.sh/win7ultimate.iso
```

**TIRE O SNAPSHOT (snapshot6)**

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

**TIRE O SNAPSHOT (snapshot7)**

```
vmcloak init --verbose --win7x64 win7x64base --cpus 2 --ramsize 2048
ou
vmcloak init --verbose --win7x64 win7x64base --cpus 1 --ramsize 2048
#Deu certo com essa

#Caso o 2 cpus der erro usar o comando acima. 
#Não esquecer de remover a criada antes de executar o outro comando
```

Aqui neste caso, é possível que seja apresentado muitos erros relacionados ao desempenho da máquina virtual hospedeira, haja vista que memória e processo irá extrapolar e travar. 

**TIRE O SNAPSHOT (snapshot8)**

Agora continue com a manipulação do dispositivo e da máquina virtual

```
vmcloak clone win7x64base win7x64cuckoo
vmcloak list deps
vmcloak install win7x64cuckoo ie11
#Ele mencionou um erro no vmcloak, mas continuei

vmcloak snapshot --count 1 win7x64cuckoo 192.168.56.101
vmcloak list vms
```

![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/88baacfd-7e4f-406a-8e0d-bf923d614f64)

**TIRE O SNAPSHOT (snapshot9)**

## Teste para ver se a Cuckoo está instalada. 

```
cuckoo init
cd .cuckoo/
ls
cuckoo community
```

Em caso positivo, continue a instalação. Se apresentar erro, trate o erro. 

## Configurações das Máquinas Virtuais nas configurações da Cuckoo

```
workon <nome do ambient virtual> (cuckoo-server)
cd conf/
ls
nano routing.conf
```

Necessário alterar a interface de rede de routing para a sua interface de rede, no meu caso foi enp0s3.

![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/568f5773-c935-4962-9368-65dcb437c2e1)

```
while read -r vm ip; do cuckoo machine --add $vm $ip; done < <(vmcloak list vms)
```

Altere o arquivo virtualbox.conf para informar qual a VM utilizada para análise dos artefatos. 

```
workon <nome do ambient virtual> (cuckoo-server)
cd ~/.cuckoo/conf
nano virtualbox.conf
```
Deixe apenas o endereço de IP da máquina, não deixe com cuckoo1.

![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/142d93d8-8b01-4cbd-b875-e3dd771cf138)

Deixar ainda direto da porta 5000-5050 para o endereço de IP dentro das chaves, igual a imagem abaixo.

![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/f07b94da-f5ba-439d-bd51-7450a7095450)

Altere as configurações do Mongo-DB. 

```
sudo systemctl status mongodb
sudo systemctl start mongodb
nano reporting.conf
#Colique “yes” na parte do MongoDB
```

![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/24f11ed1-e0f0-4715-bb80-58304c5ef90f)

## Pós instalão, inicie a Cuckoo (usando 3 terminais)

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

#Forçar o desligamento do processo da cuckoo
pkill cuckoo
```

**TIRE O SNAPSHOT (snapshot10)**

E pronto, a Cuckoo estará instalada. 

![image](https://github.com/crocodyli/BR-Forum-CSIRTs/assets/113185400/4ee63f2a-8705-4d52-8448-0af4fc8863b4)




 

