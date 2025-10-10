from abc import ABC, abstractmethod

class ArquivoDeMidia(ABC):
    """
    Classe base abstrata que representa um item de mídia ficticio.

    Define os atributos e comportamentos de todos os tipos de mídia,
    como músicas e podcasts, incluindo título, duração, artista e número
    de reproduções.

    Atributos:
        titulo (str): O título da mídia.
        duracao (int): A duração da mídia em segundos.
        artista (str): O nome do artista, banda ou produtor.
        reproducoes (int): O número de vezes que a mídia foi reproduzida.
    """
    # classe abstrata que representa um arquivo de mídia genérico
    def __init__(self, titulo: str, duracao: int, artista: str, reproducoes: int = 0):
        #checagens pra validacao dos atributos
        if not isinstance(duracao, int) or duracao < 0:
            raise ValueError("duracao deve ser um inteiro >= 0")
        if not titulo or not titulo.strip():
            raise ValueError("titulo é obrigatório")
        if not artista or not artista.strip():
            raise ValueError("artista é obrigatório")
        if not isinstance(reproducoes, int) or reproducoes < 0:
            raise ValueError("reproducoes deve ser um inteiro >= 0")

        self.titulo = titulo
        self.duracao = duracao
        self.artista = artista
        self.reproducoes = reproducoes

    @abstractmethod
    def reproduzir(self):
        self.reproducoes += 1
        print(f"Reproduzindo: {self.titulo} - {self.artista} ({self.duracao}s)")

    def __eq__(self, other):
        if not isinstance(other, ArquivoDeMidia):
            return NotImplemented
        return self.titulo.casefold() == other.titulo.casefold() and self.artista.casefold() == other.artista.casefold()

    def __str__(self):
        return f"{self.titulo} por {self.artista}"

    def __repr__(self):
        return f"{self.__class__.__name__}(titulo='{self.titulo}', artista='{self.artista}', duracao={self.duracao} s)"

    def _fmt_duracao(self):
        minutos = self.duracao // 60
        segundos = self.duracao % 60
        return f"{minutos}:{segundos:02d}"
