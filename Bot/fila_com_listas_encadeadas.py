class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Fila:
    def __init__(self):
        self.first = None
        self.last = None
        self._size = 0

    def __len__(self):
        return self._size

    def insere_paciente_na_fila(self, paciente):
        prioridades = {"vermelho": 1, "laranja": 2, "amarelo": 3, "verde": 4, "azul": 5}
        novo_node = Node(paciente)

        if self.first is None:
            self.first = novo_node
            self.last = novo_node
        else:
            if (
                prioridades[paciente["urgencia"]]
                < prioridades[self.first.data["urgencia"]]
            ):
                novo_node.next = self.first
                self.first = novo_node
            else:
                atual = self.first
                while (
                    atual.next is not None
                    and prioridades[atual.next.data["urgencia"]]
                    <= prioridades[paciente["urgencia"]]
                ):
                    atual = atual.next
                novo_node.next = atual.next
                atual.next = novo_node
                if novo_node.next is None:
                    self.last = novo_node
        self._size += 1

    def __repr__(self):
        if self.empty():
            return "Fila Vazia"

        string = ""
        ponteiro = self.first
        while ponteiro:
            string += str(ponteiro.data)
            if ponteiro.next:
                string += " -> "
            ponteiro = ponteiro.next
        return string

    def pega(self):
        if self.empty:
            return "Fila vazia"
        return self.first.data

    def pop(self):
        if self.empty:
            return " Fila vazia"
        paciente = self.first.data
        self.first = self.first.next

        if self.first is None:
            self.last = None

        self._size -= 1
        return paciente

    def top(self):
        if not self.empty:
            return self.first.data

    def empty(self) -> bool:
        return len(self) == 0
