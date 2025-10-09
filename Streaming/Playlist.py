from __future__ import annotations
from typing import List
from .ArquivoDeMidia import ArquivoDeMidia
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Usuario import Usuario

class Playlist:
    def __init__(self, nome: str, usuario: 'Usuario', reproducoes: int = 0):
        self.nome = nome
        self.usuario = usuario
        self.itens: List[ArquivoDeMidia] = []
        self.reproducoes = max(int(reproducoes), 0)

    def adicionar_midia(self, midia: ArquivoDeMidia):
        if midia not in self.itens:
            self.itens.append(midia)
            print(f"'{midia.titulo}' adicionado(a) à playlist '{self.nome}'.")
        else:
            print(f"'{midia.titulo}' já está na playlist '{self.nome}'.")

    def remover_midia(self, midia: ArquivoDeMidia):
        if midia in self.itens:
            self.itens.remove(midia)
            print(f"'{midia.titulo}' removido(a) da playlist '{self.nome}'.")
        else:
            print(f"'{midia.titulo}' não encontrado(a) na playlist '{self.nome}'.")

    def reproduzir(self):
        print(f"\n--- Reproduzindo playlist: {self.nome} ---")
        if not self.itens:
            print("Playlist está vazia.")
            return

        indice = 0
        total = len(self.itens)
        while 0 <= indice < total:
            midia = self.itens[indice]
            finalizou, acao = self.usuario.ouvir_midia(midia, mostrar_opcao_voltar=True)
            if not finalizou:
                if acao == "0" or acao is None:
                    print(f"--- Reprodução interrompida na playlist: {self.nome} ---")
                    return
                if acao == "1":
                    if indice < total - 1:
                        indice += 1
                        continue
                    print("Fim da playlist.")
                    indice = total
                    break
                if acao == "2":
                    if indice > 0:
                        indice -= 1
                        continue
                    print("Essa já é a primeira mídia da playlist.")
                    return
            else:
                indice += 1

        if indice >= total:
            self.reproducoes += 1
            print(f"--- Fim da playlist: {self.nome} ---")

    def __add__(self, other):
        if not isinstance(other, Playlist):
            return NotImplemented
        
        nova_playlist = Playlist(
            f"{self.nome} + {other.nome}",
            self.usuario,
            reproducoes=self.reproducoes + other.reproducoes,
        )
        nova_playlist.itens = self.itens + other.itens
        return nova_playlist

    def __len__(self):
        return len(self.itens)

    def __getitem__(self, index):
        return self.itens[index]

    def __eq__(self, other):
        if not isinstance(other, Playlist):
            return NotImplemented
        return (self.nome == other.nome and
                self.usuario == other.usuario and
                self.itens == other.itens)

    def __str__(self):
        return f"Playlist '{self.nome}' de {self.usuario.nome} ({len(self.itens)} itens)"

    def __repr__(self):
        return f"Playlist(nome='{self.nome}', usuario={repr(self.usuario)})"
