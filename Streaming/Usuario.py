from typing import List, TYPE_CHECKING

from .Playlist import Playlist
from .ArquivoDeMidia import ArquivoDeMidia

class Usuario:
    """
    Representa um usuário do sistema de streaming.

    Attributes:
        nome (str): O nome do usuário.
        playlists (list[Playlist]): Lista de playlists criadas pelo usuário.
        historico (list[ArquivoDeMidia]): Histórico de mídias ouvidas pelo usuário.
    """
    qntd_instancias = 0

    def __init__(self, nome: str):
        self.nome = nome
        self.playlists: List['Playlist'] = []
        self.historico: List['ArquivoDeMidia'] = []
        Usuario.qntd_instancias += 1

    def ouvir_midia(self, midia: 'ArquivoDeMidia'):
        print(f"\n{self.nome} está ouvindo:")
        midia.reproduzir()
        self.historico.append(midia)

    def criar_playlist(self, nome_playlist: str) -> 'Playlist':
        from .Playlist import Playlist
        nova_playlist = Playlist(nome_playlist, self)
        self.playlists.append(nova_playlist)
        return nova_playlist

    def __str__(self):
        return f"Usuário: {self.nome}"

    def __repr__(self):
        return f"Usuario(nome='{self.nome}')"
