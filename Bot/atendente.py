import json
import os
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

cliente_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# cliente_groq = Groq(api_key='CHAVE DA API DO GROK AQUI!')


with open("Bot/script.txt", "r", encoding="utf-8") as arquivo:
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
