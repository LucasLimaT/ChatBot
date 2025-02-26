import os
from dotenv import load_dotenv
from fila import Fila
from groq import Groq
import json
import telebot

load_dotenv()
# ------------------------------------------------------------------------------

bot = telebot.TeleBot(os.getenv("TOKEN_BOT_TELEGRAM"))
cliente_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# bot = telebot.TeleBot("Seu token do telegram")
# cliente_groq = Groq(api_key='CHAVE DA API DO GROK AQUI!')

fila = Fila()


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
    print(resposta_dados)
    return resposta_dados


def salvar_fila(fila_objeto):
    dados = []
    atual = fila_objeto.first
    while atual:
        dados.append(atual.data)
        atual = atual.next
    with open("fila.json", "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4)


def iniciar_fila():
    nova_fila = Fila()
    try:
        with open("fila.json", "r", encoding="utf-8") as file:
            dados = json.load(file)
            for item in dados:
                nova_fila.insere_paciente_na_fila(item)
    except Exception as ex:
        print(f"Fila ainda não existe ou houve um erro: {ex}")
    return nova_fila


fila = iniciar_fila()


def inserir_na_fila_prioritaria(dado):
    fila.insere_paciente_na_fila(dado)
    salvar_fila(fila)


mensagem_usuario = "exemplo de mensagem do paciente"
resultado = processar_mensagem(mensagem_usuario)
inserir_na_fila_prioritaria(resultado)
print("Fila atual:", fila)


# ------------------------------------------------------------------------------

# Esse comando é desnecessarios
"""@bot.message_handler(commands=["start"])  # , 'help'])
def mensagem_inicial(message):
    global fila
    fila = iniciar_fila()
    dict_nome = bot.get_my_name()
    nome = dict_nome.name
    bot.reply_to(message, f"Ola! Sou seu bot {nome}")"""


@bot.message_handler(commands=["sair"])
def sair(message):
    salvar_fila(fila)
    bot.reply_to(message, "Ok, :(")
    bot.stop_polling()


# Esses comandos são desnecessarios
"""@bot.message_handler(commands=["criar_arquivo"])
def criar_arquivo(message):
    with open("novo_arquivo.txt", "w") as arq:
        arq.write("Teste arquivo\n")


@bot.message_handler(commands=["foto"])
def enviar_foto(message):
    with open("emoji-joinha.jpeg", "rb") as arq_foto:
        bot.send_photo(message.chat.id, arq_foto)"""


@bot.message_handler(func=lambda message: True)
def assistente(message):
    dados = processar_mensagem(message.text)

    if dados["pronto"]:
        inserir_na_fila_prioritaria(dados)
        print(f"{dados['nome']} enfileirado!")

    print(f"\n{fila}\n")

    bot.reply_to(message, dados["resposta"])
    print(f"Recebido do usuario: {message.text}")


# roda o TeleBot
bot.polling()
