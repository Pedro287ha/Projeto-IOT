import requests
import json
from datetime import datetime, timedelta
import smtplib, ssl


### DEFINICAO DE CONSTANTES DE LOGIN
###-----------------------------------------------------------------------------------####
# CONFIGURACOES DE LOGIN DA PAGINA DE CHAMADOS
EMAIL_LOGIN_CHAMADOS = ""
SENHA_LOGIN_CHAMADOS = ""
#TIPO_DE_LOGIN = 2


###------------------###
#   CONFIGURACAO DE CREDENCIAIS 

EMAIL_REMETENTE = ""
SENHA_EMAIL_REMETENTE = ""
EMAIL_DESTINATARIO = ""
###------------------###


###------------------###
#  CONFIGURACOES DO SERVIDOR SMTP
PORTA = 587  #STARTTLS outlook # 
SERVIDOR_SMTP = "smtp-mail.outlook.com"

###------------------###


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


def receber_chamados(api_token,tipo_token) -> list:
    
    lista_chamados = []
    url_api_auth = "https://liveops-api-americas.seidor.com/v2/orbit/ticket/listwithcount"
    
    # Alterando Headers da requisicao para enviar request
    HEADERS["Authorization"] = f"{tipo_token} {api_token}"
    HEADERS['Content-Type'] = "application/json"
    
    # Json de requisicao usando ID 116 de funcionario
    data = '''{"TicketExternalIds":null,"InternalTicketNumber":null,"CustomerIds":null,"BusinessIds":null,"ProjectId":null,"AreaId":null,"ProjectTypeIds":null,"TechnicalResourceGroupFilter":[116],"TicketsOpenedByGroupFilter":null,"FilterTicketStatus":null,"MyTicket":false,"FilterDateType":null,"StartDate":null,"EndDate":null,"Term":null,"TicketFilterTermTypes":null,"CustomerUserId":null,"IsOrderByPriority":false,"SquadIds":null,"SquadId":null,"ProjectTypeCodes":null,"ProjectIdsFilter":null,"TicketStatusIdList":null,"DataAnalise":null,"Culture":"br","IsDateTypeAdditionalField":null,"Pager":{"PageSize":100,"PageNumber":1,"SortByField":"updateDate","SortDirection":"desc"}}'''

    dados_request = requests.post(url_api_auth,headers=HEADERS, allow_redirects=True,data=data)
    
    # Transformando JSON recebido em um dict 
    dados_dict = dict(json.loads(dados_request.text))
    
    # Apenas filtrando por status especificos
    status_importantes = ["Encaminhado para atendente", "Em atendimento"]
    
    
    for ticket in dados_dict["TicketGrid"]:
        status_ticket = ticket["TicketStatusName"]
        
        if status_ticket in status_importantes:
            # Formatando data para poder gerar datetime type
            data_ticket_formatada = ticket["UpdateDate"].split("T")[0]
            
            # gerando um datatype datetime para comparacao de datas
            data_ticket = datetime.strptime(data_ticket_formatada,"%Y-%m-%d")

            # Quantidade de dias desde da ultima atualizacao do chamado
            total_dias_entre_datas = int((datetime.now() - data_ticket).days) # Transformando datetime em int

            # Chamado esta sem movimento a mais de 3 dias ?
            if total_dias_entre_datas >= 3:


                lista_chamados.append({
                    "id" : ticket["TicketId"],
                    "Mensagem" : f'ATENCAO o chamado de ID "{ticket["TicketId"]}" esta a {total_dias_entre_datas} dias sem ATUALIZACAO Link: https://liveops-americas.seidor.com/#/ticket/{ticket["TicketId"]} Email: {ticket["TicketAssigneeName"]}',
                })
    return lista_chamados

def enviar_email(email_remetente,senha,email_destinatario,mensagem):

    # modelo pradrao da documentacao do SMTPlib

    mensagem =  f'Subject: CHAMADO ABERTO\n\n{mensagem}\n'

    context = ssl.create_default_context() # criando um handshake com o servidor 
    with smtplib.SMTP(SERVIDOR_SMTP, PORTA) as server:
        server.starttls(context=context)
        server.login(email_remetente, senha)
        server.sendmail(email_remetente, email_destinatario, mensagem)

def main() -> None:
    token = gerar_api_token(EMAIL_LOGIN_CHAMADOS,SENHA_LOGIN_CHAMADOS)
    #chamados = get_chamados_abertos(token['access_token'],token['token_type'])

    # Receber todos os chamados abertos e fazer verificacao 
    chamados = receber_chamados(token['access_token'],token['token_type'])
    print(len(chamados), chamados)
    for chamado in chamados:
        enviar_email(EMAIL_REMETENTE,SENHA_EMAIL_REMETENTE, EMAIL_DESTINATARIO, chamado["Mensagem"].encode('utf8'))

if __name__ == "__main__":
    main()
