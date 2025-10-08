from abc import ABC, abstractmethod

class ArquivoDeMidia(ABC):
    # classe abstrata que representa um arquivo de mídia genérico
    def __init__(self, titulo: str, duracao: int, artista: str):
        #checagens pra validacao dos atributos
        if not isinstance(duracao, int) or duracao < 0:
            raise ValueError("duracao deve ser um inteiro >= 0")
        if not titulo or not titulo.strip():
            raise ValueError("titulo é obrigatório")
        if not artista or not artista.strip():
            raise ValueError("artista é obrigatório")

        self.titulo = titulo
        self.duracao = duracao
        self.artista = artista
        self.reproducoes = 0

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