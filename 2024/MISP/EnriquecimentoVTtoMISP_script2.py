#O foco do script é consumir de um local um arquivo de hashes (SHA1, MD5 e SHA256), consultar no Vírus Total e enriquecer um evento no MISP. 
import requests
import json
import datetime
import time
from virus_total_apis import PublicApi as VirusTotalPublicApi
from pymisp import MISPEvent, ExpandedPyMISP, MISPAttribute, PyMISPError

# Configurações
vt_api_key = 'APYKEY VT'
misp_url = 'URL MISP'
misp_api_key = 'APYKEY MISP'
misp_verifycert = False
hashes_file_path = '<local de leitura dos arquivos de hash>'
#Define quais scans a serem utilizados para análise e enriquecimento
scanners_of_interest = ['Sophos', 'TrendMicro', 'Kaspersky', 'Microsoft', 'Symantec']
request_interval = 15  # Intervalo de tempo entre requisições em segundos

# Suprimir avisos de verificação de certificado SSL
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Função para criar evento no MISP
def create_event(misp):
    event = MISPEvent()
    event.info = f"Feed do Cuckoo - CSIRT Forum - {datetime.date.today()}"
    event.analysis = 2  # Ongoing analysis
    event.distribution = 0  # Your Organisation Only
    event.threat_level_id = 2  # Medium
    event.add_tag('tlp:amber+strict')
    event.add_tag('feed_cuckoo')
    event.add_tag('CSIRT')
    created_event = misp.add_event(event)
    return created_event

# Função para consultar hash no VirusTotal
def query_virustotal(filehash):
    vt = VirusTotalPublicApi(vt_api_key)
    response = vt.get_file_report(filehash)
    return response

# Função para adicionar tags a um objeto
def add_tags_to_object(misp, object_uuid, tags):
    for tag in tags:
        try:
            misp.tag(object_uuid, tag)
            print(f"Tag {tag} adicionada ao objeto {object_uuid}")
        except PyMISPError as e:
            print(f"Erro ao adicionar tag {tag} ao objeto {object_uuid}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta completa do servidor: {e.response.text}")
            else:
                print("Nenhuma resposta detalhada do servidor disponível.")
        except Exception as e:
            print(f"Erro inesperado ao adicionar tag {tag} ao objeto {object_uuid}: {e}")

# Função para adicionar hashes ao evento
def add_hash_attributes(misp, event_id, vt_data, scanners):
    hash_types = ['md5', 'sha1', 'sha256']
    added_any = False
    for hash_type in hash_types:
        if hash_type in vt_data:
            attribute = MISPAttribute()
            attribute.type = hash_type
            attribute.value = vt_data[hash_type]
            attribute.to_ids = True
            attribute.category = "Payload delivery"
            attribute.comment = f"Consulta no Virus Total: {vt_data['positives']}/{vt_data['total']}"
            try:
                attribute = misp.add_attribute(event_id, attribute)
                if 'Attribute' in attribute:
                    print(f"Atributo {hash_type} adicionado ao evento com ID: {attribute['Attribute']['id']}")
                    add_tags_to_object(misp, attribute['Attribute']['uuid'], scanners)
                    added_any = True
            except PyMISPError as e:
                if 'errors' in e.response.json() and 'value' in e.response.json()['errors'] and 'A similar attribute already exists for this event.' in e.response.json()['errors']['value']:
                    print(f"Erro ao adicionar atributo {hash_type} no MISP: Atributo já existente.")
                else:
                    print(f"Erro ao adicionar atributo {hash_type} no MISP: {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"Resposta completa do servidor: {e.response.text}")
                    else:
                        print("Nenhuma resposta detalhada do servidor disponível.")
            except Exception as e:
                print(f"Erro inesperado ao adicionar atributo {hash_type} no MISP: {e}")
    return added_any

# Função principal
def main():
    try:
        misp = ExpandedPyMISP(misp_url, misp_api_key, misp_verifycert)
        created_event = create_event(misp)
        event_id = created_event['Event']['id']
        hashes_added = False
        
        with open(hashes_file_path, 'r') as file:
            for line in file:
                filehash = line.strip()
                vt_response = query_virustotal(filehash)
                json_doc = json.dumps(vt_response, sort_keys=False, indent=1)
                try:
                    vt_data = json.loads(json_doc)['results']
                    positives = vt_data['positives']
                    if positives > 0:
                        scanners = [scanner for scanner, result in vt_data['scans'].items() if result['result'] and scanner in scanners_of_interest]
                        if scanners:
                            print(f"Processando hash: {filehash}, Scanners: {scanners}")
                            if add_hash_attributes(misp, event_id, vt_data, scanners):
                                hashes_added = True
                    # Espera antes de fazer a próxima requisição
                    time.sleep(request_interval)
                except KeyError:
                    print('Não tem resultado do VT')

        # Publicar o evento após adicionar atributos, se houver atributos adicionados
        if hashes_added:
            misp.publish(event_id)
            print(f"Evento criado e publicado com sucesso: {event_id}")
        else:
            print("Nenhum hash positivo encontrado. Evento não publicado.")
    except Exception as e:
        print(f'Erro: {e}')

if __name__ == '__main__':
    main()
