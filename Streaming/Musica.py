from .ArquivoDeMidia import ArquivoDeMidia

class Musica(ArquivoDeMidia):
    def __init__(self, titulo: str, duracao: int, artista: str, genero: str):
        super().__init__(titulo, duracao, artista) # chama o construtor da classe mae
        self.genero = genero
        self.avaliacoes = []

    def reproduzir(self):
        super().reproduzir()
        print(f"Duração: {self._fmt_duracao()} min")
        print(f"Gênero: {self.genero}")

    def avaliar(self, nota: int):
        if 0 <= nota <= 5:
            self.avaliacoes.append(nota)
            return True
        return False

    def __repr__(self):
        return f"Musica(titulo='{self.titulo}', artista='{self.artista}', duracao={self.duracao}, genero='{self.genero}')"
