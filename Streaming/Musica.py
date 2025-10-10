from typing import Iterable, Optional
from .ArquivoDeMidia import ArquivoDeMidia
import logging

class Musica(ArquivoDeMidia):
    def __init__(
        self,
        titulo: str,
        duracao: int,
        artista: str,
        genero: str,
        reproducoes: int = 0,
        avaliacoes: Optional[Iterable[int]] = None,
    ):
        super().__init__(titulo, duracao, artista, reproducoes=reproducoes)
        if not genero or not genero.strip():
            raise ValueError("genero é obrigatório")
        self.genero: str = genero
        self.avaliacoes: list[int] = []
        if avaliacoes is not None:
            for nota in avaliacoes:
                try:
                    nota_int = int(nota)
                except (TypeError, ValueError):
                    logging.error(f"Nota inválida ({nota}) carregada para {self.titulo} - {self.artista}")
                    continue
                if 0 <= nota_int <= 5:
                    self.avaliacoes.append(nota_int)
                else:
                    logging.error(f"Nota fora do intervalo ({nota_int}) carregada para {self.titulo} - {self.artista}")

    def reproduzir(self) -> None:
        super().reproduzir()
        print(f"Gênero: {self.genero}")

    def avaliar(self, nota: int) -> bool:
        if 0 <= nota <= 5:
            self.avaliacoes.append(nota)
            return True
        logging.error(f"Nota inválida ({nota}) para {self.titulo} - {self.artista}")
        print("Nota inválida. Deve ser entre 0 e 5.")
        return False

    def __str__(self) -> str:
        return f"{self.titulo} — {self.artista} [{self.genero}]"

    def __repr__(self) -> str:
        return (f"Musica(titulo='{self.titulo}', artista='{self.artista}', "
                f"duracao={self.duracao}, genero='{self.genero}')")
