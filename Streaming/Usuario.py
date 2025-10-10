from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional, Tuple
import sys
import time
import math
from .ArquivoDeMidia import ArquivoDeMidia
from typing import TYPE_CHECKING

try:
    import termios
    import tty
    import select
    HAS_TERMIOS = True
except ImportError: 
    termios = tty = select = None
    HAS_TERMIOS = False
if TYPE_CHECKING:
    from .Playlist import Playlist

class Usuario:
    """
    Representa um usuário do sistema de streaming.

    Cada usuário possui um nome, uma lista de playlists e um histórico
    de mídias ouvidas.

    Attributes:
        nome (str): O nome do usuário.
        playlists (List[Playlist]): A lista de playlists criadas pelo usuário.
        historico (List[ArquivoDeMidia]): A lista de mídias que o usuário ouviu.
        qntd_instancias (int): Atributo de classe que conta o número total de
                               usuários criados.
    """
    qntd_instancias = 0

    def __init__(self, nome: str, total_midias_ouvidas: int = 0):
        self.nome = nome
        self.playlists: List['Playlist'] = []
        self.historico: List['ArquivoDeMidia'] = []
        try:
            total = int(total_midias_ouvidas)
        except (TypeError, ValueError):
            total = 0
        self.total_midias_ouvidas = max(total, 0)
        Usuario.qntd_instancias += 1

    def ouvir_midia(self, midia: 'ArquivoDeMidia', aguardar: bool = True, mostrar_opcao_voltar: bool = True):
        print(f"\n{self.nome} está ouvindo:")
        midia.reproduzir()
        resultado = True
        acao = None
        if aguardar:
            resultado, acao = self._executar_temporizador(
                midia.duracao,
                mostrar_opcao_voltar,
                mostrar_controles_playlist=mostrar_opcao_voltar,
            )
            if resultado:
                print()
        self.historico.append(midia)
        self.total_midias_ouvidas += 1
        return resultado, acao

    def _executar_temporizador(self, duracao: int, mostrar_opcao_voltar: bool, mostrar_controles_playlist: bool = False):
        if duracao <= 0:
            print("Tempo restante:    0s")
            if mostrar_opcao_voltar:
                if mostrar_controles_playlist:
                    print("0. Voltar")
                    print("1. Próxima")
                    print("2. Anterior")
                else:
                    print("0. Voltar")
            return True, None

        if HAS_TERMIOS and sys.stdin.isatty():
            return self._temporizador_interativo(
                duracao,
                mostrar_opcao_voltar,
                mostrar_controles_playlist,
            )

        for restantes in range(duracao, 0, -1):
            print(f"Tempo restante: {restantes:>4}s")
            time.sleep(1)
        print("Tempo restante:    0s")
        if mostrar_opcao_voltar:
            if mostrar_controles_playlist:
                print("0. Voltar")
                print("1. Próxima")
                print("2. Anterior")
            else:
                print("0. Voltar")
        return True, None

    def _temporizador_interativo(self, duracao: int, mostrar_opcao: bool, mostrar_controles_playlist: bool):
        fd = sys.stdin.fileno()
        try:
            old_settings = termios.tcgetattr(fd)
        except termios.error:  # pragma: no cover
            return self._executar_temporizador(
                duracao,
                mostrar_opcao,
                mostrar_controles_playlist,
            )

        interrompido = False
        acao = None
        try:
            tty.setcbreak(fd)
            new_settings = termios.tcgetattr(fd)
            new_settings[3] &= ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)

            sys.stdout.write("Tempo restante: %4ds" % duracao)
            if mostrar_opcao:
                sys.stdout.write("\n0. Voltar")
                if mostrar_controles_playlist:
                    sys.stdout.write("\n1. Próxima")
                    sys.stdout.write("\n2. Anterior")
            sys.stdout.write("\n\0337")
            sys.stdout.flush()

            fim = time.monotonic() + duracao
            ultimo_restante = duracao

            while True:
                agora = time.monotonic()
                restante = max(0, math.ceil(fim - agora))

                if restante != ultimo_restante:
                    self._atualizar_display(
                        restante,
                        mostrar_opcao,
                        mostrar_controles_playlist,
                    )
                    ultimo_restante = restante

                if restante <= 0:
                    break

                timeout = max(0.05, min(0.5, fim - agora))

                if mostrar_opcao:
                    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                    if rlist:
                        tecla = sys.stdin.read(1)
                        if tecla in {"0", "1", "2"}:
                            acao = tecla
                            if tecla == "0":
                                interrompido = True
                            break
                else:
                    time.sleep(timeout)

            if acao is not None:
                self._limpar_linha_temporizador(
                    mostrar_opcao,
                    mostrar_controles_playlist,
                )
                if acao == "0":
                    print("Reprodução interrompida.")
                return False, acao

            self._atualizar_display(0, mostrar_opcao, mostrar_controles_playlist)
            return True, None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    @staticmethod
    def _atualizar_display(restantes: int, mostrar_opcao: bool, mostrar_controles_playlist: bool):
        linhas = 2 if mostrar_opcao else 1
        if mostrar_opcao and mostrar_controles_playlist:
            linhas = 4
        sys.stdout.write("\0338")          # restaura cursor salvo
        sys.stdout.write("\0337")          # salva novamente posição base
        sys.stdout.write("\033[%dA" % (linhas + 0))  # sobe até o início do bloco
        sys.stdout.write("\033[K")
        sys.stdout.write(f"Tempo restante: {restantes:>4}s\n")
        if mostrar_opcao:
            sys.stdout.write("\033[K")
            sys.stdout.write("0. Voltar\n")
            if mostrar_controles_playlist:
                sys.stdout.write("\033[K")
                sys.stdout.write("1. Próxima\n")
                sys.stdout.write("\033[K")
                sys.stdout.write("2. Anterior\n")
        sys.stdout.write("\033[K")
        sys.stdout.write("\033[%dB" % (linhas))  # volta ao ponto de entrada
        sys.stdout.flush()

    @staticmethod
    def _limpar_linha_temporizador(mostrar_opcao: bool, mostrar_controles_playlist: bool):
        linhas = 2 if mostrar_opcao else 1
        if mostrar_opcao and mostrar_controles_playlist:
            linhas = 4
        sys.stdout.write("\0338")  # restaura posição base
        sys.stdout.write("\0337")  # salva novamente
        sys.stdout.write("\033[%dA" % linhas)
        sys.stdout.write("\033[K\n")
        if mostrar_opcao:
            sys.stdout.write("\033[K\n")
            if mostrar_controles_playlist:
                sys.stdout.write("\033[K\n")
                sys.stdout.write("\033[K\n")
        sys.stdout.write("\033[K")
        sys.stdout.write("\033[%dB" % linhas)
        sys.stdout.flush()

    def criar_playlist(self, nome_playlist: str, reproducoes: int = 0):
        from .Playlist import Playlist
        nova_playlist = Playlist(nome_playlist, self, reproducoes=reproducoes)
        self.playlists.append(nova_playlist)
        return nova_playlist

    def __str__(self):
        return f"Usuário: {self.nome}"

    def __repr__(self):
        return f"Usuario(nome='{self.nome}')"
