import os
from dotenv import load_dotenv
load_dotenv() 
#------------------------------------------------------------------------------
from groq import Groq
import json
import telebot

bot = telebot.TeleBot(os.getenv('TOKEN_BOT_TELEGRAM'))
cliente_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# bot = telebot.TeleBot("Seu token do telegram")
# cliente_groq = Groq(api_key='CHAVE DA API DO GROK AQUI!')

fila = []

with open('script.txt', 'r', encoding='utf-8') as arquivo:
    script = arquivo.read()


historico_mensagens = [
    {
        "role": "system",
        "content": script
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
    print(resposta_dados)
    return resposta_dados

def salvar(lista):
    with open('fila.json', 'w', encoding='utf-8') as file:
        json.dump(lista, file, indent=4)

def iniciar_lista():
    try: 
        with open('fila.json', 'r') as file:
            fila = json.load(file)
    except:
        fila = []
        
#------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])#, 'help'])
def mensagem_inicial(message):
    iniciar_lista()
    dict_nome = bot.get_my_name()
    nome = dict_nome.name
    bot.reply_to(message, f'Ola! Sou seu bot {nome}')

@bot.message_handler(commands=['sair'])
def sair(message):
    salvar(fila)
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

    if dados['pronto']:
        fila.append(dados)
        print(f'{dados['nome']} enfileirado!')
    
    print(f'\n{fila}\n')

    bot.reply_to(message, dados['resposta'])
    print(f'Recebido do usuario: {message.text}')


# roda o TeleBot
bot.polling()
