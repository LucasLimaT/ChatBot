import os
from dotenv import load_dotenv
from atendente import processar_mensagem
from fila import Fila
import telebot

load_dotenv()

bot = telebot.TeleBot(os.getenv("TOKEN_BOT_TELEGRAM"))

fila = Fila()


@bot.message_handler(commands=["sair"])
def sair(message):
    fila.salvar_fila(None)
    bot.reply_to(message, "Ok, :(")
    bot.stop_polling()


@bot.message_handler(commands=["pulseiras"])
def mostrar_pulseiras(message):
    with open("Bot/pulseiras.txt", "r", encoding="utf-8") as file:
        texto = file.read()

    bot.reply_to(message, texto, parse_mode="HTML")


@bot.message_handler(commands=["atender"])
def atendimento(message):
    aviso = fila.atender()
    bot.reply_to(message, aviso)


@bot.message_handler(commands=["fila"])
def mostrar_ordem_fila(message):
    texto = fila.mostrar_fila()
    bot.reply_to(message, texto, parse_mode="HTML")


@bot.message_handler(commands=["comandos", "ajuda", "help"])
def comandos(message):
    with open("Bot/comandos.txt", "r", encoding="utf-8") as file:
        texto = file.read()

    bot.reply_to(message, texto, parse_mode="HTML")


@bot.message_handler(func=lambda message: True)
def assistente(message):
    dados = processar_mensagem(message.text)
    resposta = dados.pop("resposta")
    status = dados.pop("pronto")

    try:
        if status:
            fila.salvar_fila(dados)
            print(f"{dados['nome']} enfileirado!")
    except Exception as error:
        print(f"error: {error}")
    bot.reply_to(message, resposta)
    print(f"Mensagem recebida do usuario: {message.text}")


# roda o TeleBot
bot.polling()
