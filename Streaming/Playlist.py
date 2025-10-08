from __future__ import annotations
from typing import List
from .ArquivoDeMidia import ArquivoDeMidia
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Usuario import Usuario

class Playlist:
    def __init__(self, nome: str, usuario: 'Usuario'):
        self.nome = nome
        self.usuario = usuario
        self.itens: List[ArquivoDeMidia] = []
        self.reproducoes = 0

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

        for item in self.itens:
            self.usuario.ouvir_midia(item)
        self.reproducoes += 1
        print(f"--- Fim da playlist: {self.nome} ---")

    def __add__(self, other):
        if not isinstance(other, Playlist):
            return NotImplemented
        
        nova_playlist = Playlist(f"{self.nome} + {other.nome}", self.usuario)
        nova_playlist.itens = self.itens + other.itens
        nova_playlist.reproducoes = self.reproducoes + other.reproducoes
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
