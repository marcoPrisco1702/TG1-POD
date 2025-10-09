import os
import datetime
from Streaming.Musica import Musica
from Streaming.Podcast import Podcast
from Streaming.Usuario import Usuario
from Streaming.Playlist import Playlist
from Streaming.Analises import Analises

#classe menu pra gerenciar o sistema
class Menu:
    def __init__(self):
        self.usuarios = []
        self.midias = []
        self.dados_carregados = False

        self.LOG_FOLDER = "Logs"
        self.REPORT_FOLDER = "Relatorios"
        self.CONFIG_FOLDER = "config"
        self.config_path = os.path.join(self.CONFIG_FOLDER, "dados.md")

        self.setup_folders()
        self.carregar_dados()

    def setup_folders(self):
        """Cria as pastas de log, relatório e configuração se não existirem."""
        os.makedirs(self.LOG_FOLDER, exist_ok=True)
        os.makedirs(self.REPORT_FOLDER, exist_ok=True)
        os.makedirs(self.CONFIG_FOLDER, exist_ok=True)

    def log_erro(self,mensagem: str):
        """Registra uma mensagem de erro no arquivo de log."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(os.path.join(self.LOG_FOLDER, "erros.log"), "a", encoding="utf-8") as f:
            f.write(f"[{now}] ERRO: {mensagem}\n")

    def gerar_relatorio(self):
        """Gera e salva o relatório de estatísticas do sistema."""
        print("\nGerando relatório...")
        
        all_musicas = [m for m in self.midias if isinstance(m, Musica)]
        all_playlists = []
        for u in self.usuarios:
            all_playlists.extend(u.playlists)

        top_5_musicas = Analises.top_musicas_reproduzidas(all_musicas, 5)
        playlist_popular = Analises.playlist_mais_popular(all_playlists)
        user_ativo = Analises.usuario_mais_ativo(self.usuarios)
        medias_musicas = Analises.media_avaliacoes(all_musicas)
        total_reps = Analises.total_reproducoes(self.usuarios)
        
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = os.path.join(self.REPORT_FOLDER, f"relatorio_{now}.txt")

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

    def encontrar_usuario(self,nome):
        for u in self.usuarios:
            if u.nome.lower() == nome.lower():
                return u
        return None

    def encontrar_midia(self,titulo):
        for m in self.midias:
            if m.titulo.lower() == titulo.lower():
                return m
        return None


    def carregar_dados(self):
        """Carrega usuários, músicas, podcasts e playlists do arquivo Markdown em config/dados.md."""
        if self.dados_carregados:
            return  # evita recarregar se já carregado
        if not os.path.exists(self.config_path):
            print(f"[aviso] Arquivo de configuração não encontrado: {self.config_path}")
            return

        secao = None  # 'usuarios' | 'musicas' | 'podcasts' | 'playlists'
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                for raw in f:
                    linha = raw.strip()
                    if not linha:
                        continue
                    # comentários/headers
                    if linha.startswith("#"):
                        if linha.startswith("## "):
                            titulo = linha[3:].strip().lower()
                            if titulo.startswith("usuarios"):
                                secao = "usuarios"
                            elif titulo.startswith("musicas"):
                                secao = "musicas"
                            elif titulo.startswith("podcasts"):
                                secao = "podcasts"
                            elif titulo.startswith("playlists"):
                                secao = "playlists"
                            else:
                                secao = None
                        continue

                    # somente processa itens que começam com "- "
                    if not linha.startswith("- "):
                        continue
                    conteudo = linha[2:].strip()

                    if secao == "usuarios":
                        nome = conteudo
                        if not self.encontrar_usuario(nome):
                            self.usuarios.append(Usuario(nome))
                        else:
                            self.log_erro(f"Usuário duplicado no arquivo de config: '{nome}'")

                    elif secao == "musicas":
                        # titulo | artista | duracao_em_segundos | genero | reproducoes?
                        partes = [p.strip() for p in conteudo.split("|")]
                        if len(partes) < 4:
                            self.log_erro(f"Formato inválido para música: '{conteudo}'")
                            continue
                        titulo, artista, dur_str, genero = partes[:4]
                        reproducoes = 0
                        if len(partes) >= 5:
                            rep_str = partes[4]
                            try:
                                reproducoes = int(rep_str)
                                if reproducoes < 0:
                                    raise ValueError
                            except ValueError:
                                self.log_erro(f"Reproduções inválidas em música: '{conteudo}'")
                                reproducoes = 0
                        try:
                            duracao = int(dur_str)
                        except ValueError:
                            self.log_erro(f"Duração inválida em música: '{conteudo}'")
                            continue
                        self.midias.append(Musica(titulo, duracao, artista, genero, reproducoes=reproducoes))

                    elif secao == "podcasts":
                        # titulo | artista | duracao_em_segundos | temporada | episodio | host | reproducoes?
                        partes = [p.strip() for p in conteudo.split("|")]
                        if len(partes) < 6:
                            self.log_erro(f"Formato inválido para podcast: '{conteudo}'")
                            continue
                        titulo, artista, dur_str, temporada, ep_str, host = partes[:6]
                        reproducoes = 0
                        if len(partes) >= 7:
                            rep_str = partes[6]
                            try:
                                reproducoes = int(rep_str)
                                if reproducoes < 0:
                                    raise ValueError
                            except ValueError:
                                self.log_erro(f"Reproduções inválidas em podcast: '{conteudo}'")
                                reproducoes = 0
                        try:
                            duracao = int(dur_str)
                            episodio = int(ep_str)
                        except ValueError:
                            self.log_erro(f"Duração/Episódio inválidos em podcast: '{conteudo}'")
                            continue
                        self.midias.append(Podcast(titulo, duracao, artista, episodio, temporada, host, reproducoes=reproducoes))

                    elif secao == "playlists":
                        # nome_da_playlist | usuario_dono | titulos_de_midias_separados_por_ponto_e_virgula | reproducoes?
                        partes = [p.strip() for p in conteudo.split("|")]
                        if len(partes) < 3:
                            self.log_erro(f"Formato inválido para playlist: '{conteudo}'")
                            continue
                        nome_pl, dono, itens = partes[:3]
                        reproducoes = 0
                        if len(partes) >= 4:
                            rep_str = partes[3]
                            try:
                                reproducoes = int(rep_str)
                                if reproducoes < 0:
                                    raise ValueError
                            except ValueError:
                                self.log_erro(f"Reproduções inválidas em playlist: '{conteudo}'")
                                reproducoes = 0

                        usuario = self.encontrar_usuario(dono)
                        if not usuario:
                            # opção A: criar e logar
                            self.log_erro(f"Usuário '{dono}' não encontrado ao criar playlist '{nome_pl}'. Criando automaticamente.")
                            usuario = Usuario(dono)
                            self.usuarios.append(usuario)

                        pl = usuario.criar_playlist(nome_pl, reproducoes=reproducoes)
                        # títulos separados por ';'
                        titulos = [t.strip() for t in itens.split(";") if t.strip()]
                        for t in titulos:
                            midia = self.encontrar_midia(t)
                            if midia:
                                pl.adicionar_midia(midia)
                            else:
                                self.log_erro(f"Mídia '{t}' não encontrada ao montar playlist '{nome_pl}'.")
            print(f"[ok] Config carregada de {self.config_path}")
            self.dados_carregados = True
            self.salvar_dados()
        except Exception as e:
            self.log_erro(f"Falha ao ler config '{self.config_path}': {e}")
            print(f"[erro] Não foi possível ler {self.config_path}. Veja Logs/erros.log.")

    def salvar_dados(self):
        """Persiste o estado atual no arquivo de configuração Markdown."""
        if not self.dados_carregados:
            return

        os.makedirs(self.CONFIG_FOLDER, exist_ok=True)

        linhas = [
            "# Configuração do Sistema de Streaming",
            "",
            "> Preencha as seções abaixo. Uma linha por item.",
            "> Use **UTF-8** e mantenha o formato exato (campos separados por `|`).",
            "",
            "## Usuarios",
        ]

        for usuario in self.usuarios:
            linhas.append(f"- {usuario.nome}")

        linhas.append("")
        linhas.extend(
            [
                "## Musicas",
                "# Formato: titulo | artista | duracao_em_segundos | genero | reproducoes",
            ]
        )

        musicas = [m for m in self.midias if isinstance(m, Musica)]
        for musica in musicas:
            linhas.append(
                f"- {musica.titulo} | {musica.artista} | {musica.duracao} | {musica.genero} | {musica.reproducoes}"
            )

        linhas.append("")
        linhas.extend(
            [
                "## Podcasts",
                "# Formato: titulo | artista (produtor) | duracao_em_segundos | temporada | episodio | host | reproducoes",
            ]
        )

        podcasts = [p for p in self.midias if isinstance(p, Podcast)]
        for podcast in podcasts:
            linhas.append(
                f"- {podcast.titulo} | {podcast.artista} | {podcast.duracao} | {podcast.temporada} | {podcast.episodio} | {podcast.host} | {podcast.reproducoes}"
            )

        linhas.append("")
        linhas.extend(
            [
                "## Playlists",
                "# Formato: nome_da_playlist | usuario_dono | titulos_de_midias_separados_por_ponto_e_virgula | reproducoes",
            ]
        )

        playlists = []
        for usuario in self.usuarios:
            playlists.extend(usuario.playlists)

        for playlist in playlists:
            itens = "; ".join(item.titulo for item in playlist.itens)
            linhas.append(
                f"- {playlist.nome} | {playlist.usuario.nome} | {itens} | {playlist.reproducoes}"
            )

        linhas.append("")

        conteudo = "\n".join(linhas) + "\n"
        temp_path = f"{self.config_path}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as temp:
                temp.write(conteudo)
            os.replace(temp_path, self.config_path)
        except Exception as e:
            self.log_erro(f"Falha ao salvar config '{self.config_path}': {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def menu_principal(self):
        while True:
            print("\n=== MENU PRINCIPAL ===")
            print("1. Entrar como usuário existente")
            print("2. Criar novo usuário")
            print("3. Gerar relatório")
            print("4. Sair")

            escolha = input("Escolha uma opção: ")

            if escolha == "1":
                nome = input("Digite o nome do usuário: ")
                usuario = self.encontrar_usuario(nome)
                if usuario:
                    self.menu_usuario(usuario)
                else:
                    print("Usuário não encontrado.")

            elif escolha == "2":
                nome = input("Digite o nome do novo usuário: ")
                if self.encontrar_usuario(nome):
                    print("Usuário já existe.")
                else:
                    novo_usuario = Usuario(nome)
                    self.usuarios.append(novo_usuario)
                    print(f"Usuário '{nome}' criado com sucesso!")
                    self.salvar_dados()

            elif escolha == "3":
                self.gerar_relatorio()

            elif escolha == "4":
                print("Saindo do sistema...")
                self.salvar_dados()
                break

            else:
                print("Opção inválida. Tente novamente.")


    def menu_usuario(self,usuario: Usuario):
        """Exibe e gerencia o menu do usuário logado."""
        while True:
            print(f"\n--- Menu de {usuario.nome} ---")
            print("1. Reproduzir uma mídia")
            print("2. Listar mídias")
            print("3. Criar nova playlist")
            print("4. Ver minhas playlists")
            print("5. Reproduzir uma playlist")
            print("6. Avaliar uma música")
            print("7. Sair (Voltar ao menu principal)")
            
            escolha = input("Escolha uma opção: ")

            if escolha == "1":
                titulo = input("Digite o título da mídia: ")
                midia = self.encontrar_midia(titulo)
                if midia:
                    usuario.ouvir_midia(midia)
                    self.salvar_dados()
                else:
                    print("Mídia não encontrada.")

            elif escolha == "2":
                print("\n--- Todas as Mídias ---")
                for midia in self.midias:
                    print(f"- {midia}")
                
            elif escolha == "3":
                nome_playlist = input("Digite o nome da nova playlist: ")
                if any(p.nome.lower() == nome_playlist.lower() for p in usuario.playlists):
                    print("Você já possui uma playlist com esse nome.")
                else:
                    playlist = usuario.criar_playlist(nome_playlist)
                    while True:
                        titulo_midia = input("Adicione uma mídia (ou 'fim' para terminar): ")
                        if titulo_midia.lower() == 'fim':
                            break
                        midia = self.encontrar_midia(titulo_midia)
                        if midia:
                            playlist.adicionar_midia(midia)
                        else:
                            print("Mídia não encontrada.")
                    print(f"Playlist '{nome_playlist}' criada!")
                    self.salvar_dados()
            
            elif escolha == "4":
                print(f"\n--- Playlists de {usuario.nome} ---")
                if not usuario.playlists:
                    print("Você ainda não tem playlists.")
                for p in usuario.playlists:
                    print(f"- {p}")

            elif escolha == "5":
                nome_playlist = input("Digite o nome da playlist para reproduzir: ")
                playlist_encontrada = None
                for p in usuario.playlists:
                    if p.nome.lower() == nome_playlist.lower():
                        playlist_encontrada = p
                        break
                if playlist_encontrada:
                    playlist_encontrada.reproduzir()
                    self.salvar_dados()
                else:
                    print("Playlist não encontrada.")

            elif escolha == "6":
                titulo = input("Digite o título da música para avaliar: ")
                midia = self.encontrar_midia(titulo)
                if midia and isinstance(midia, Musica):
                    try:
                        nota = int(input(f"Qual sua nota para '{midia.titulo}' (0-5)? "))
                        if not midia.avaliar(nota):
                            print("Nota inválida. Deve ser entre 0 e 5.")
                            self.log_erro(f"Tentativa de avaliação inválida ({nota}) para '{midia.titulo}'.")
                        else:
                            print("Avaliação registrada!")
                    except ValueError:
                        print("Por favor, insira um número.")
                else:
                    print("Música não encontrada.")

            elif escolha == "7":
                print("Saindo do perfil...")
                self.salvar_dados()
                break
            else:
                print("Opção inválida.")        
