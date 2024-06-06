# PROJETO IOT
Este é um projeto simples que monitora chamados sem interação por mais de 3 dias (podendo ser configurado pelo usuário a quantidade de dias) e avisa o funcionário sobre eles. Além disso, notifica os usuários sobre o fechamento de horas no final do dia. Todas as notificações são enviadas por e-mail, deixando assim o funcionário atualizado sobre qualquer chamado dentro do prazo determinado.

## Funcionalidades

- **Monitoramento de Chamados:** O sistema verifica ao inicializar se existem chamados abertos há 3 dias ou mais, por padrao, e envia um e-mail de aviso ao funcionário caso existem algum chamado sem interação.
  
- **Notificação de Fechamento de Horas:** O sistema envia um e-mail caso a hora de fechamento informada pelo usuário seja maior ou igual a ela, levando em consideração que esta hora seja menor que 23 horas.

## Como Usar

2. **Configuração das Credenciais:**
   - No arquivo `main.py`, insira suas credenciais do sistema, email para permitir com que o programa posso ser utilizado
![](https://i.imgur.com/sZHzDGn.gif)


## Funcionamento
![](https://i.imgur.com/CQLro5h.gif)

![](https://img.shields.io/github/stars/Pedro287ha/Projeto-IOT)
![](https://img.shields.io/github/forks/Pedro287ha/Projeto-IOT)
