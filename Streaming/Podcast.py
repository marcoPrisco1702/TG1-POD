from __future__ import annotations
from .ArquivoDeMidia import ArquivoDeMidia


class Podcast(ArquivoDeMidia):

    def __init__(self,titulo: str, duracao: int, artista: str, episodio: int, temporada: str, host: str, reproducoes: int = 0,):
        super().__init__(titulo, duracao, artista, reproducoes=reproducoes)

        # checagens pra validacao de atributos
        if not isinstance(episodio, int) or episodio < 1:
            raise ValueError("episodio deve ser um inteiro >= 1")
        if not temporada or not str(temporada).strip():
            raise ValueError("temporada é obrigatória")
        if not host or not host.strip():
            raise ValueError("host é obrigatório")

        self.episodio = episodio
        self.temporada = temporada
        self.host = host

    def reproduzir(self) -> None:
        super().reproduzir()
        print(f"Temporada: {self.temporada} | Episódio: {self.episodio} | Host: {self.host}")

    
    
    def __str__(self):
        return (f"Podcast('{self.titulo}' — {self.artista}, T{self.temporada}E{self.episodio}, "
            f"{self._fmt_duracao()}, {self.reproducoes}x)")

    def __repr__(self):
        cls = self.__class__.__name__
        return (f"{cls}(titulo={self.titulo!r}, duracao={self.duracao!r}, artista={self.artista!r}, "
                  f"episodio={self.episodio!r}, temporada={self.temporada!r}, host={self.host!r})")
