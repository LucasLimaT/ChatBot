import json


class Fila:
    def __init__(self):
        self.fila = self.iniciar_fila()

    @staticmethod
    def iniciar_fila():
        try:
            with open("fila.json", "r", encoding="utf-8") as file:
                dados = json.load(file)
                return dados
        except Exception as ex:
            print(f"Fila ainda não existe ou houve um erro: {ex}")
            return {}

    def ordenar(self):
        try:
            preferencias = {
                "vermelho": 1,
                "laranja": 2,
                "amarelo": 3,
                "verde": 4,
                "azul": 5,
            }

            self.fila = dict(
                sorted(
                    self.fila.items(),
                    key=lambda item: preferencias[item[1]["urgencia"]],
                )
            )
        except Exception as ex:
            print(f"Erro ao ordenar paciente: {ex}")

    def salvar_fila(self, dados: dict = None) -> None:
        if dados is not None:
            try:
                self.fila[dados["cpf"]] = dados
                self.ordenar()
            except Exception as ex:
                print(f"Erro ao inserir paciente: {ex}")

        try:
            with open("fila.json", "w", encoding="utf-8") as file:
                json.dump(self.fila, file, indent=4)
        except Exception as ex:
            print(f"Erro ao salvar fila: {ex}")

    def remover_da_fila(self):
        for cpf, paciente in self.fila.items():
            self.fila.pop(cpf)
            return paciente, cpf
        return None, None

    def fila_vazia(self) -> bool:
        return len(self.fila) == 0

    def atender(self) -> str:
        if self.fila_vazia():
            return "fila vazia ninguém para ser atendido no momento"
        else:
            paciente, cpf = self.remover_da_fila()
            if paciente is None:
                return "Erro ao remover paciente da fila"
            aviso = f"proximo paciente: {paciente['nome']}\ncpf: {cpf}\nurgencia: {paciente['urgencia']}"
            print(f"{paciente['nome']} foi atendido")
            return aviso

    def mostrar_fila(self) -> str:
        if self.fila_vazia():
            return "não tem ninguém esperando ser atendido"

        emojis = {
            "vermelho": "🔴",
            "laranja": "🟠",
            "amarelo": "🟡",
            "verde": "🟢",
            "azul": "🔵",
        }

        self.ordenar()
        mensagem = "🏥 <b>Ordem de Atendimento</b> 📋\n\n"
        for pos, (cpf, paciente) in enumerate(self.fila.items(), 1):
            mensagem += (
                f"{pos}️⃣ <b>{paciente['nome']}</b>\n"
                f"⏱ Urgência: {emojis[paciente['urgencia']]} {paciente['urgencia'].capitalize()}\n\n"
            )

        return mensagem
