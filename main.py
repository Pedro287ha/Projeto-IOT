import requests
import json
from datetime import datetime, timedelta
import smtplib, ssl
import email
from time import sleep

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
# CONFIGURACOES USUARIO
DIAS_NOTIFICAR = 3
ID_USUARIO = 116
HORARIO_LEMBRETE_HORAS = 18
email_aviso_enviado = False
###------------------###
## Definindo User-agent para evitar block do CLoudFlare
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

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
    
    # Tratando possiveis erros de conexao
    try:
        dados_request = requests.post(url_api_auth,headers=headers, allow_redirects=True,data=data)
    
    except requests.ConnectionError:
        print("Ocorreu um erro de CONEXAO.. Verfique sua CONEXAO com o server!")
        return {}
    except Exception as err:
        print(f"ERRO desconhecido: {err}")
        return {}
        
    # Transformando JSON recebido em um dict 
    dados_dict = dict(json.loads(dados_request.text))


    # API respondeu com algum erro ?
    if dados_dict.get("error") is not None:
        for erro in dados_dict.values():
            
            if erro == "invalid_grant": # Abrindo possibilidade de mais erros da API
                #print(erro)
                print("Login ou senha INVALIDOS!!")

                return {}
    
    return dados_dict 


def receber_chamados(api_token,tipo_token) -> list:
    
    lista_chamados = []
    url_api_chamados = "https://liveops-api-americas.seidor.com/v2/orbit/ticket/listwithcount"
    
    # Alterando Headers da requisicao para enviar request
    headers["Authorization"] = f"{tipo_token} {api_token}"
    headers['Content-Type'] = "application/json"
    
    # Json para a API para requisitar chamados
    data_em_dict = {
        "TechnicalResourceGroupFilter": [ID_USUARIO],
        "Pager": {
            "PageSize": 100,
            "PageNumber": 1,
            "SortByField": "updateDate",
            "SortDirection": "desc"
            }
    }

    ## Convertendo data_dicionario para json
    data = json.dumps(data_em_dict)

    dados_request = requests.post(url_api_chamados,headers=headers, allow_redirects=True,data=data)
    
    # Transformando JSON recebido em um dict 
    dados_dict = dict(json.loads(dados_request.text))
    
    # Apenas filtrando por tipos de status abaixo
    status_importantes = ["Encaminhado para atendente", "Em atendimento"]
    
    #d = datetime.today() - timedelta(days=QUANTIDADE_DIAS_CHECAR)
    
    
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
            if total_dias_entre_datas >= DIAS_NOTIFICAR:

                lista_chamados.append({
                    "id" : ticket["TicketId"],
                    "corpo_email" : f'<p></p><p><b>ATENÇÃO</b> CHAMADO COM ID <b style="color:purple;">{ticket["TicketId"]}</b> está há <b style="color:red;">{total_dias_entre_datas} dias aberto</b> Link: <a href=https://liveops-americas.seidor.com/#/ticket/{ticket["TicketId"]}>Link Ticket</a></p><img src="https://www.python.org/static/community_logos/python-powered-w-70x28.png"> - Projeto IOT - Email Automático<img><hr>'
                })
    return lista_chamados


def enviar_email(email_remetente,senha,email_destinatario,corpo_email):

    # Criando email de envio
    msg = email.message.Message()
    msg['Subject'] = "CHAMADO ABERTO" #ASSUNTO DO E-MAIL#
    msg['From'] = email_remetente #E-MAIL QUE VAI ENVIAR O E-MAIL#
    msg['To'] = email_destinatario#E-MAIL QUE VAI RECEBER
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    context = ssl.create_default_context() # criando um handshake com o servidor 

    with smtplib.SMTP(SERVIDOR_SMTP, PORTA) as server:
        server.starttls(context=context)
        server.login(email_remetente, senha)
        server.sendmail(email_remetente, email_destinatario, msg.as_string().encode('utf-8'))

def main() -> int:

    ## Usuario informou login e senha de chamados ?
    
    if EMAIL_LOGIN_CHAMADOS and SENHA_LOGIN_CHAMADOS:

        token = gerar_api_token(EMAIL_LOGIN_CHAMADOS,SENHA_LOGIN_CHAMADOS)
        
        # Executa apenas se token for existente
        if token:
            #Receber todos os chamados abertos e fazer verificacao 
            chamados = receber_chamados(token['access_token'],token['token_type'])
            print(len(chamados), chamados)

            for chamado in chamados:
                enviar = enviar_email(EMAIL_REMETENTE,SENHA_EMAIL_REMETENTE, EMAIL_DESTINATARIO, chamado["corpo_email"])
                    

        
        ## Loop quando programa estiver rodando

        horario_atual = datetime.now().hour
        if horario_atual >= HORARIO_LEMBRETE_HORAS and horario_atual <= 23:
            print("Lembrar de fechar horas!!")

    else:
        print("Login ou senha NÃO informado!!")
        return 1

if __name__ == "__main__":
    main()


