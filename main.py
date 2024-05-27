import requests
import json
from datetime import datetime

### DEFINICAO DE CONSTANTES DE LOGIN
###-----------------------------------------------------------------------------------####
# CONFIGURACOES DE LOGIN DA PAGINA DE CHAMADOS
EMAIL_LOGIN_CHAMADOS = ""
SENHA_LOGIN_CHAMADOS = ""
#TIPO_DE_LOGIN = 2

## LOGIN EMAIL PARA ENVIO DE NOTIFICACOES
EMAIL = ""
SENHA_EMAIL = ""
PORTA_SMTP = 0


###-----------------------------------------------------------------------------------####


####---------#### DEFINICOES DE DATAS
DATA_ATUAL = datetime.now()
ANO_ATUAL = DATA_ATUAL.year
DIA_ATUAL = DATA_ATUAL.day
MES_ATUAL = DATA_ATUAL.month

QUANTIDADE_DIAS_CHECAR = 7
####---------####

## Definindo User-agent para evitar block do CLoudFlare
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

###---------------------------------------------------#####

# Recebendo Token da API de Autenticacao
def gerar_api_token(email,senha) -> dict:

    #Encodando login usuario para url encoding https://www.w3schools.com/tags/ref_urlencode.ASP
    email_encoded = requests.utils.quote(email)
    senha_encoded = requests.utils.quote(senha)

    # Mover para topo pagina configuracao
    url_api_auth = "https://liveops-api-americas.seidor.com/v2/auth"

    # Gerando data para realizar login na API
    data = f"grant_type=password&username={email_encoded}&password={senha_encoded}&language=br&loginType=2" # 

    dados_request = requests.post(url_api_auth,headers=HEADERS, allow_redirects=True,data=data)
    
    # Transformando JSON recebido em um dict 
    dados_dict = dict(json.loads(dados_request.text))
    
    
    return dados_dict 



## Apenas chamados do modulo
def get_chamados_abertos(api_token,tipo_token) -> dict:
    
    ## Validando chamandos de 1 semana(7 dias)
    data_inicial = f"{ANO_ATUAL}/{MES_ATUAL}/{DIA_ATUAL - QUANTIDADE_DIAS_CHECAR}"
    data_final = f"{ANO_ATUAL}/{MES_ATUAL}/{DIA_ATUAL}"
    url = f"https://liveops-api-americas.seidor.com/area/45/dashboard?StartDate={data_inicial}&EndDate={data_final}"
    

    ## ADICIONANDO PARAMENTRO TOKEN GERADO DO USUARIO NO HEADER
    HEADERS["Authorization"] = f"{tipo_token} {api_token}"

    dados_request = requests.get(url,headers=HEADERS, allow_redirects=True)



    dados_em_json = json.loads(dados_request.text)
    chamados = dict(dados_em_json)
    
    total_atentimentos = chamados['Total']
    # Juntando 2 listas em um dicionario
    tipo_atendimento_e_quantidade = dict(zip(chamados['Labels'], chamados['Quantities']))


    #Adicionando numero total de chamados ao dicionario
    tipo_atendimento_e_quantidade['Total'] = total_atentimentos
    
    return tipo_atendimento_e_quantidade



def main() -> None:
    token = gerar_api_token(EMAIL_LOGIN_CHAMADOS,SENHA_LOGIN_CHAMADOS)
    chamados = get_chamados_abertos(token['access_token'],token['token_type'])

    print(chamados)

if __name__ == "__main__":
    main()
