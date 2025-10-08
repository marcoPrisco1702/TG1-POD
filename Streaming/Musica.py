from .ArquivoDeMidia import ArquivoDeMidia

class Musica(ArquivoDeMidia):
    """
    Representa uma música, uma subclasse de ArquivoDeMidia.

    Attributes:
        genero (str): O gênero da música.
        avaliacoes (list[int]): Uma lista de avaliações (notas de 0 a 5).
    """
    def __init__(self, titulo: str, duracao: int, artista: str, genero: str):
        super().__init__(titulo, duracao, artista)
        self.genero = genero
        self.avaliacoes = []

    def reproduzir(self):
        """
        Simula a reprodução da música e incrementa o contador de reproduções.
        """
        super().reproduzir()
        print(f"Gênero: {self.genero}")

    def avaliar(self, nota: int):
        """
        Adiciona uma avaliação à música, se a nota for válida (0-5).

        Args:
            nota (int): A nota de avaliação.

        Returns:
            bool: True se a nota foi adicionada, False caso contrário.
        """
        if 0 <= nota <= 5:
            self.avaliacoes.append(nota)
            return True
        return False

    def __repr__(self):
        return f"Musica(titulo='{self.titulo}', artista='{self.artista}', duracao={self.duracao}, genero='{self.genero}')"
