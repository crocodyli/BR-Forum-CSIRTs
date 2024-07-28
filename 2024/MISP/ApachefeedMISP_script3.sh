#!/bin/bash
misp_md5="https://URL_MISP/attributes/restSearch/returnFormat:text/publish_timestamp:15d/to_ids:1||0/tags:CSIRT/type:md5"
misp_sha256="https://URL_MISP/attributes/restSearch/returnFormat:text/publish_timestamp:15d/to_ids:1||0/tags:CSIRT/type:sha256"
misp_sha1="https://URL_MISP/attributes/restSearch/returnFormat:text/publish_timestamp:15d/to_ids:1||0/tags:CSIRT/type:sha1"
misp_key="APYKEY"
#
curl -s -k -H "Authorization: $misp_key" -X GET "$misp_md5" -o /var/www/html/feed/blocklist_md5.txt
curl -s -k -H "Authorization: $misp_key" -X GET "$misp_sha1" -o /var/www/html/feed/blocklist_sha1.txt
curl -s -k -H "Authorization: $misp_key" -X GET "$misp_sha256" -o /var/www/html/feed/blocklist_sha256.txt

#sudo chmod 777 /var/www/html/feed
#sudo chmod 777 <script>
#sudo nano /etc/apache2/port.conf
#alterar para a porta desejada, exemplo 155, 8080;
#service apache2 restart 
#execute o script
