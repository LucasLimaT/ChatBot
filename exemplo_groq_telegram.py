import os
from dotenv import load_dotenv
load_dotenv() 
#------------------------------------------------------------------------------
from groq import Groq
import json
import telebot

# bot = telebot.TeleBot(os.getenv('TOKEN_BOT_TELEGRAM'))
# cliente_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

bot = telebot.TeleBot("Seu token do telegram")
cliente_groq = Groq(api_key='CHAVE DA API DO GROK AQUI!')

historico_mensagens = [
    {
        "role": "system",
        "content": '''
            Analise a mensagem do usuário para identificar qual é a sua 
            intenção, e responda com um json no seguinte formato: 
            {\"intencao\": <numero>, \"resposta\": <texto>}. 
            No atributo \"intencao\" do JSON, deve haver o número da 
            intenção, e no atributo \"resposta\", deve haver uma resposta educada para enviar ao usuário. 
            Caso a intenção seja ligar o ar-condicionado, o número da intenção é 1. 
            Caso a intenção seja desligar o ar-condicionado, o número da intenção é 2. 
            Caso o usuário tenha outra intenção, o número é 0. Não dê respostas fora desse formato.
        '''
    }
]

def processar_mensagem(mensagem):
    historico_mensagens.append({
            "role": "user",
            "content": mensagem
    })

    try:
        completion = cliente_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico_mensagens,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
            response_format={'type': 'json_object'}
        )
    except:
        historico_mensagens.pop()
        return {'intencao': 0, 'resposta': 'Erro servidor Groq'}

    resposta_json = completion.choices[0].message.content
    resposta_dados = json.loads(resposta_json)

    historico_mensagens.append(completion.choices[0].message)

    """
    O retorno é um dicionário nesse formato: 
    {
        "intencao": <numero>, 
        "resposta": <texto>
    }
    """
    return resposta_dados

#------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])#, 'help'])
def mensagem_inicial(message):
    dict_nome = bot.get_my_name()
    nome = dict_nome.name
    bot.reply_to(message, f'Ola! Sou seu bot {nome}')

@bot.message_handler(commands=['sair'])
def sair(message):
    bot.reply_to(message, 'Ok, :(')
    bot.stop_polling()

@bot.message_handler(commands=['criar_arquivo'])
def criar_arquivo(message):
    with open('novo_arquivo.txt', 'w') as arq:
        arq.write('Teste arquivo\n')

@bot.message_handler(commands=['foto'])
def enviar_foto(message):
    with open('emoji-joinha.jpeg', 'rb') as arq_foto:
        bot.send_photo(message.chat.id, arq_foto)
    
@bot.message_handler(func=lambda message: True)
def assistente(message):
    dados = processar_mensagem(message.text)

    resposta = ""
    if dados['intencao'] == 1:
        resposta = f'Ligando o ar, {dados['resposta']}'
    elif dados['intencao'] == 2:
        resposta = f'Desligando o ar, {dados['resposta']}'
    else:
        resposta = f'Comando fora de contexto, {dados['resposta']}'

    bot.reply_to(message, resposta)
    print(f'Recebido do usuario: {message.text}')


# roda o TeleBot
bot.polling()
