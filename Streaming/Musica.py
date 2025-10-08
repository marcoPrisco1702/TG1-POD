from .ArquivoDeMidia import ArquivoDeMidia
import logging

class Musica(ArquivoDeMidia):
    def __init__(self, titulo: str, duracao: int, artista: str, genero: str):
        super().__init__(titulo, duracao, artista)
        if not genero or not genero.strip():
            raise ValueError("genero é obrigatório")
        self.genero: str = genero
        self.avaliacoes: list[int] = []

    def reproduzir(self) -> None:
        # imprime título, artista e duração (mm:ss) e incrementa reproduções
        super().reproduzir()
        # só complementa com info específica de música
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