import os
from dotenv import load_dotenv
from fila import Fila
from groq import Groq
import json
import telebot
import requests

load_dotenv()
# ------------------------------------------------------------------------------

bot = telebot.TeleBot(os.getenv("TOKEN_BOT_TELEGRAM"))
cliente_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# bot = telebot.TeleBot("Seu token do telegram")
# cliente_groq = Groq(api_key='CHAVE DA API DO GROK AQUI!')


with open("script.txt", "r", encoding="utf-8") as arquivo:
    script = arquivo.read()

historico_mensagens = [{"role": "system", "content": script}]


def processar_mensagem(mensagem):
    historico_mensagens.append({"role": "user", "content": mensagem})

    try:
        completion = cliente_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico_mensagens,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
            response_format={"type": "json_object"},
        )
    except Exception as ex:
        historico_mensagens.pop()
        return {"intencao": 0, "resposta": f"Erro ao conectar com o Groq: {ex}"}

    resposta_json = completion.choices[0].message.content
    resposta_dados = json.loads(resposta_json)
    historico_mensagens.append(completion.choices[0].message)

    """
    O retorno é um dicionário nesse formato: 
    {
        "urgencia": <cor>, 
        "nome": <nome>, 
        "cpf": <cpf>, 
        "pronto": <status>, 
        "resposta": <texto>
    }
    """
    return resposta_dados

def iniciar_fila():
    fila = {}
    try:
        with open("fila.json", "r", encoding="utf-8") as file:
            dados = json.load(file)
            for cpf, pessoas in dados.items():
                fila[cpf] = pessoas
    except Exception as ex:
        fila = {}
        print(f"Fila ainda não existe ou houve um erro: {ex}")
    return fila


fila = iniciar_fila()

def salvar_fila(dados=None):
    global fila
    try:
        preferencias = {"vermelho": 1, "laranja": 2, "amarelo": 3, "verde": 4, "azul": 5}

        fila[dados['cpf']] = dados
        fila = dict(sorted(fila.items(), key=lambda item: preferencias[item[1]["urgencia"]]))
    except:
        pass

    with open("fila.json", "w", encoding="utf-8") as file:
        json.dump(fila, file, indent=4)






# ------------------------------------------------------------------------------


@bot.message_handler(commands=["sair"])
def sair(message):
    salvar_fila()
    bot.reply_to(message, "Ok, :(")
    bot.stop_polling()


@bot.message_handler(commands=['pulseiras'])
def mostrar_pulseiras(message):
    with open('pulseiras.txt', 'r', encoding='utf-8') as file:
        texto = file.read()

    bot.reply_to(message, texto, parse_mode="HTML")

@bot.message_handler(commands=['atender'])
def atendimento(message):
    if len(fila) == 0:
        aviso = 'fila vazia ninguém para ser atendido no momento'
        print(aviso)
    
    else:
        for cpf, paciente in fila.items():
            fila.pop(cpf)
            break

        aviso = f'proximo paciente: {paciente['nome']}\ncpf: {cpf}\nurgencia: {paciente['urgencia']}'
        print(f'{paciente['nome']} foi atendido')

    salvar_fila()
    bot.reply_to(message, aviso)


@bot.message_handler(func=lambda message: True)
def assistente(message):
    dados = processar_mensagem(message.text)
    resposta = dados.pop("resposta")
    status = dados.pop("pronto")

    try:
        if status:
            salvar_fila(dados)
            print(f"{dados['nome']} enfileirado!")
    except Exception as error:
        print(f'error: {error}')
    bot.reply_to(message, resposta)
    print(f"Recebido do usuario: {message.text}")


# roda o TeleBot
bot.polling()
