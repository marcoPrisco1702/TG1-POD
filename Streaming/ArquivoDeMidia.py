from abc import ABC, abstractmethod

class ArquivoDeMidia(ABC):
    #classe abstrata que representa um arquivo de mídia genérico
    def __init__(self, titulo: str, duracao: int, artista: str):
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
        return self.titulo.lower() == other.titulo.lower() and self.artista.lower() == other.artista.lower()

    def __str__(self):
        return f"{self.titulo} por {self.artista}"

    def __repr__(self):
        return f"{self.__class__.__name__}(titulo='{self.titulo}', artista='{self.artista}', duracao={self.duracao})"