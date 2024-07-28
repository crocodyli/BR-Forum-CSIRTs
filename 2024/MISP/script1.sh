#Este script foi escrito para realizar a extração dos dados do MISP de eventos não publicados e types de atributos específicos. 
#
#!/bin/bash

# Defina a URL e a chave API do MISP
misp_url="URL do MISP"
misp_key="APYKey"

# Defina o JSON para a consulta
json_query='{
    "returnFormat": "text",
    "to_ids": "1||0",
    "published": false,
    "tags": "Cuckoo",
    "type": "filename|sha256||filename|md5||filename|sha1"
}'

# Realize a consulta utilizando curl
response=$(curl -s -k -H "Authorization: $misp_key" -H "Content-Type: application/json" -X POST -d "$json_query" "$misp_url")

# Verifique se houve um erro na consulta
if [[ $? -ne 0 ]]; then
    echo "Erro na consulta ao MISP"
    exit 1
fi

# Salve o resultado em um arquivo temporário
temp_result_file=$(mktemp)
echo "$response" > "$temp_result_file"

# Verifique se o arquivo temporário contém dados
if [[ ! -s "$temp_result_file" ]]; then
    echo "Nenhum resultado encontrado."
    rm -f "$temp_result_file"
    exit 1
fi

# Analise o arquivo temporário em busca de hashes, remova duplicatas e sobrescreva o arquivo hashes.txt
grep -Eo "\b([a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64})\b" "$temp_result_file" | sort -u > /home/misp/feed/hashes.txt

# Verifique se o arquivo hashes.txt contém dados
if [[ ! -s <local de salvamento>/hashes.txt ]]; then
    echo "Nenhum hash encontrado."
    rm -f "$temp_result_file"
    exit 1
fi

echo "Hashes únicos encontrados foram salvos em <local de salvar os arquivos>"

# Remova o arquivo temporário
rm -f "$temp_result_file"
