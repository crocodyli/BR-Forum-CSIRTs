# Arquivo de orientação para configuração da Cuckoo com a integração e interação do MISP

O Cuckoo vem com módulos prontos para uso para interagir com a API REST do MISP por meio do módulo PyMISP Python, com ele você pode realizar o processamento, ou seja, pesquisar IoCs existentes no MISP e um módulo de relatórios, utilizado para criar um novo evento no MISP. 

É válido salientar que a configuração é realizada em 2 arquivos:
- reporting.conf
- processing.conf

## reporting.conf
```
reporting.conf-logname = syslog.log
reporting.conf-
reporting.conf:[misp]
reporting.conf-enabled = yes
reporting.conf:url = URL DO MISP
reporting.conf-apikey = SUA APYKEY DO MISP
```

## processing.conf
```
processing.conf-enabled = yes
processing.conf-
processing.conf:[misp]
processing.conf-enabled = yes
processing.conf:url = URL DO MISP
processing.conf-apikey = SUA APYKEY DO MISP
maxioc = 100
```

É valido mencionar que existem outras configurações para serem usadas na análise da cuckoo. 
