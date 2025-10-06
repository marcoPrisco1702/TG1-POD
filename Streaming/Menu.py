import os
import datetime
from Streaming.musica import Musica
from Streaming.podcast import Podcast
from Streaming.usuario import Usuario
from Streaming.playlist import Playlist
from Streaming.analises import Analises

class Menu:
    def __init__(self):
        self.usuarios = []
        self.midias = []

        self.LOG_FOLDER = "logs"
        self.REPORT_FOLDER = "relatorios"
        self.CONFIG_FOLDER = "config"

        self.setup_folders()
        self.carregar_dados()

    def setup_folders():
        """Cria as pastas de log, relatório e configuração se não existirem."""
        os.makedirs(LOG_FOLDER, exist_ok=True)
        os.makedirs(REPORT_FOLDER, exist_ok=True)
        os.makedirs(CONFIG_FOLDER, exist_ok=True)

    def log_erro(mensagem: str):
        """Registra uma mensagem de erro no arquivo de log."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(os.path.join(LOG_FOLDER, "erros.log"), "a", encoding="utf-8") as f:
            f.write(f"[{now}] ERRO: {mensagem}\n")

    def gerar_relatorio():
        """Gera e salva o relatório de estatísticas do sistema."""
        print("\nGerando relatório...")
        
        all_musicas = [m for m in midias if isinstance(m, Musica)]
        all_playlists = []
        for u in usuarios:
            all_playlists.extend(u.playlists)

        top_5_musicas = Analises.top_musicas_reproduzidas(all_musicas, 5)
        playlist_popular = Analises.playlist_mais_popular(all_playlists)
        user_ativo = Analises.usuario_mais_ativo(usuarios)
        medias_musicas = Analises.media_avaliacoes(all_musicas)
        total_reps = Analises.total_reproducoes(usuarios)
        
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = os.path.join(REPORT_FOLDER, f"relatorio_{now}.txt")

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("--- Relatório de Estatísticas do Streaming ---\n")
            f.write(f"Gerado em: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("--- Top 5 Músicas Mais Reproduzidas ---\n")
            for i, m in enumerate(top_5_musicas):
                f.write(f"{i+1}. {m.titulo} - {m.artista} ({m.reproducoes} reps)\n")
            f.write("\n")

            f.write("--- Playlist Mais Popular ---\n")
            if playlist_popular:
                f.write(f"'{playlist_popular.nome}' de {playlist_popular.usuario.nome} ({playlist_popular.reproducoes} reps)\n\n")
            else:
                f.write("Nenhuma playlist encontrada.\n\n")

            f.write("--- Usuário Mais Ativo ---\n")
            if user_ativo:
                f.write(f"{user_ativo.nome} com {len(user_ativo.historico)} mídias ouvidas.\n\n")
            else:
                f.write("Nenhum usuário ativo.\n\n")

            f.write("--- Média de Avaliação das Músicas ---\n")
            for titulo, media in medias_musicas.items():
                f.write(f"- {titulo}: {media:.2f}/5.0\n")
            f.write("\n")

            f.write("--- Total de Reproduções no Sistema ---\n")
            f.write(f"{total_reps} reproduções.\n")

        print(f"Relatório salvo em: {report_path}")

    # --- Funções Auxiliares ---
    def encontrar_usuario(nome):
        for u in usuarios:
            if u.nome.lower() == nome.lower():
                return u
        return None

    def encontrar_midia(titulo):
        for m in midias:
            if m.titulo.lower() == titulo.lower():
                return m
        return None


    def carregar_dados():
        """Carrega usuários, mídias e playlists do arquivo de configuração."""
        config_path = os.path.join(CONFIG_FOLDER, "dados.md")
        if not os.path.exists(config_path):
            print("Arquivo de configuração não encontrado. Iniciando com dados vazios.")
            return

        with open(config_path, "r", encoding="utf-8") as f:
            modo = None
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("<!--"):
                    continue
                
                if linha.startswith("## "):
                    modo = linha.replace("## ", "").strip().lower()
                    continue
                
                if modo == "usuarios":
                    if encontrar_usuario(linha):
                        log_erro(f"Usuário duplicado no arquivo de config: '{linha}'")
                    else:
                        usuarios.append(Usuario(linha))

                elif modo == "musicas":
                    try:
                        titulo, artista, duracao, genero = [x.strip() for x in linha.split(",")]
                        midias.append(Musica(titulo, int(duracao), artista, genero))
                    except ValueError:
                        log_erro(f"Formato inválido para música: '{linha}'")
                
                elif modo == "podcasts":
                    try:
                        titulo, artista, duracao, host, temporada, episodio = [x.strip() for x in linha.split(",")]
                        midias.append(Podcast(titulo, int(duracao), artista, int(episodio), temporada, host))
                    except ValueError:
                        log_erro(f"Formato inválido para podcast: '{linha}'")

                elif modo == "playlists":
                    try:
                        nome_usuario, nome_playlist, titulos_midias = [x.strip() for x in linha.split(":")]
                        usuario = encontrar_usuario(nome_usuario)
                        if not usuario:
                            log_erro(f"Usuário '{nome_usuario}' da playlist '{nome_playlist}' não encontrado.")
                            continue
                        
                        playlist = usuario.criar_playlist(nome_playlist)
                        for titulo_midia in titulos_midias.split(","):
                            midia = encontrar_midia(titulo_midia.strip())
                            if midia:
                                playlist.adicionar_midia(midia)
                            else:
                                log_erro(f"Mídia '{titulo_midia.strip()}' da playlist '{nome_playlist}' não encontrada.")
                    except ValueError:
                        log_erro(f"Formato inválido para playlist: '{linha}'")

            





