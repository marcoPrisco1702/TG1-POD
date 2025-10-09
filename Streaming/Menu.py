import os
import datetime
from typing import Optional, Set
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

    def _obter_playlists_disponiveis(self, excluir=None):
        playlists = []
        for usuario in self.usuarios:
            for playlist in usuario.playlists:
                if excluir and playlist is excluir:
                    continue
                playlists.append((playlist, usuario))
        return playlists

    def _adicionar_midias_manual(self, playlist: Playlist):
        while True:
            titulo_midia = input("Digite o título da mídia para adicionar (ou '0' para finalizar): ").strip()
            if titulo_midia == "0":
                break
            midia = self.encontrar_midia(titulo_midia)
            if midia:
                playlist.adicionar_midia(midia)
                self.salvar_dados()
            else:
                print("Mídia não encontrada.")

    def _concatenar_playlist(self, playlist_destino: Playlist):
        playlists_disponiveis = self._obter_playlists_disponiveis(excluir=playlist_destino)
        if not playlists_disponiveis:
            print("Não há outras playlists disponíveis para concatenar.")
            return

        print("\n--- Playlists disponíveis para concatenar ---")
        print("0. Cancelar")
        for idx, (plist, dono) in enumerate(playlists_disponiveis, start=1):
            print(f"{idx}. {plist.nome} (de {dono.nome}) - {len(plist.itens)} itens")

        escolha = input("Digite o número ou nome da playlist: ").strip()
        if escolha == "0":
            return

        playlist_origem = None
        if escolha.isdigit():
            indice = int(escolha)
            if 1 <= indice <= len(playlists_disponiveis):
                playlist_origem = playlists_disponiveis[indice - 1][0]
        else:
            for pl, _ in playlists_disponiveis:
                if pl.nome.lower() == escolha.lower():
                    playlist_origem = pl
                    break

        if not playlist_origem:
            print("Playlist não encontrada para concatenação.")
            return

        if not playlist_origem.itens:
            print("Playlist de origem está vazia.")
            return

        for item in playlist_origem.itens:
            playlist_destino.adicionar_midia(item)
        print(f"Playlist '{playlist_origem.nome}' concatenada em '{playlist_destino.nome}'.")
        self.salvar_dados()

    def _menu_edicao_playlist(self, playlist: Playlist):
        while True:
            print(f"\n--- Gerenciar playlist '{playlist.nome}' ---")
            print("1. Adicionar mídia individualmente")
            print("2. Concatenar outra playlist")
            print("0. Finalizar edição")
            escolha = input("Escolha uma opção: ").strip()

            if escolha == "0":
                break
            elif escolha == "1":
                self._adicionar_midias_manual(playlist)
            elif escolha == "2":
                self._concatenar_playlist(playlist)
            else:
                print("Opção inválida.")

    def _solicitar_acao(self, mensagem: str, opcoes: Set[str], padrao: Optional[str] = None) -> str:
        while True:
            escolha = input(mensagem).strip()
            if not escolha and padrao is not None:
                return padrao
            if escolha in opcoes:
                return escolha
            print("Opção inválida.")

    def _reproduzir_playlist_interativo(self, playlist: Playlist, inicio: int = 0):
        if not playlist.itens:
            print("Playlist está vazia.")
            return

        if inicio < 0 or inicio >= len(playlist.itens):
            print("Índice inicial inválido para a playlist.")
            return

        indice = inicio
        total_itens = len(playlist.itens)
        concluida = True

        while 0 <= indice < total_itens:
            midia_atual = playlist.itens[indice]
            finalizou, acao = playlist.usuario.ouvir_midia(
                midia_atual,
                mostrar_opcao_voltar=True,
            )
            self.salvar_dados()
            if not finalizou:
                if acao == "0" or acao is None:
                    concluida = False
                    break
                if acao == "1":
                    if indice < total_itens - 1:
                        indice += 1
                        continue
                    print("Fim da playlist.")
                    break
                if acao == "2":
                    if indice > 0:
                        indice -= 1
                        continue
                    print("Essa já é a primeira mídia da playlist.")
                    concluida = False
                    break

            # reprodução foi até o fim sem ação imediata; pedir próximo passo
            if total_itens == 1:
                print("0. Voltar")
                proxima = self._solicitar_acao("Selecione uma opção: ", {"0"}, padrao="0")
                if proxima == "0":
                    concluida = False
                break

            while True:
                padrao = "1" if indice < total_itens - 1 else "0"
                print("0. Voltar")
                print("1. Próxima")
                print("2. Anterior")
                proxima = self._solicitar_acao(
                    "Selecione uma opção: ",
                    {"0", "1", "2"},
                    padrao=padrao,
                )

                if proxima == "0":
                    concluida = False
                    indice = total_itens
                    break
                if proxima == "1":
                    if indice < total_itens - 1:
                        indice += 1
                        break
                    print("Fim da playlist.")
                    indice = total_itens
                    break
                if proxima == "2":
                    if indice > 0:
                        indice -= 1
                        break
                    print("Essa já é a primeira mídia da playlist.")

            if indice >= total_itens or not concluida:
                break

        if concluida:
            playlist.reproducoes += 1
            print(f"--- Fim da reprodução da playlist: {playlist.nome} ---")

    def menu_principal(self):
        while True:
            print("\n=== MENU PRINCIPAL ===")
            print("0. Sair")
            print("1. Entrar como usuário existente")
            print("2. Criar novo usuário")
            print("3. Listar usuários existentes")
            print("4. Gerar relatório")

            escolha = input("Escolha uma opção: ")

            if escolha == "0":
                print("Saindo do sistema...")
                self.salvar_dados()
                break

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
                if not self.usuarios:
                    print("Nenhum usuário cadastrado.")
                else:
                    print("\n--- Usuários cadastrados ---")
                    for idx, usuario in enumerate(self.usuarios, start=1):
                        print(f"{idx}. {usuario.nome}")

            elif escolha == "4":
                self.gerar_relatorio()

            else:
                print("Opção inválida. Tente novamente.")


    def menu_usuario(self,usuario: Usuario):
        """Exibe e gerencia o menu do usuário logado."""
        while True:
            print(f"\n--- Menu de {usuario.nome} ---")
            print("0. Voltar ao menu principal")
            print("1. Reproduzir uma mídia")
            print("2. Listar mídias")
            print("3. Criar nova playlist")
            print("4. Ver minhas playlists")
            print("5. Reproduzir uma playlist")
            print("6. Adicionar mídia a uma playlist")
            print("7. Avaliar uma música")
            
            escolha = input("Escolha uma opção: ")

            if escolha == "0":
                print("Saindo do perfil...")
                self.salvar_dados()
                break

            if escolha == "1":
                while True:
                    print("\n--- Selecionar tipo de mídia ---")
                    print("1. Música")
                    print("2. Podcast")
                    print("0. Voltar")
                    tipo = input("Escolha uma opção: ").strip()

                    if tipo == "0":
                        break
                    elif tipo == "1":
                        midias_filtradas = [m for m in self.midias if isinstance(m, Musica)]
                        etiqueta = "Músicas"
                    elif tipo == "2":
                        midias_filtradas = [p for p in self.midias if isinstance(p, Podcast)]
                        etiqueta = "Podcasts"
                    else:
                        print("Opção inválida.")
                        continue

                    if not midias_filtradas:
                        print(f"Não há {etiqueta.lower()} cadastrados.")
                        continue

                    print(f"\n--- {etiqueta} disponíveis ---")
                    for idx, mid in enumerate(midias_filtradas, start=1):
                        if isinstance(mid, Musica):
                            info = f"{mid.titulo} — {mid.artista} ({mid.genero})"
                        else:
                            info = f"{mid.titulo} — {mid.host}"
                        print(f"{idx}. {info} [{mid.reproducoes} reproduções]")

                    escolha_midia = input("Digite o número ou nome da mídia (ou 0 para voltar): ").strip()
                    if escolha_midia == "0":
                        continue

                    midia = None
                    if escolha_midia.isdigit():
                        indice = int(escolha_midia)
                        if 1 <= indice <= len(midias_filtradas):
                            midia = midias_filtradas[indice - 1]
                    else:
                        for mid in midias_filtradas:
                            if mid.titulo.lower() == escolha_midia.lower():
                                midia = mid
                                break

                    if midia:
                        finalizou, _ = usuario.ouvir_midia(midia)
                        self.salvar_dados()
                        if finalizou:
                            self._solicitar_acao("Selecione uma opção: ", {"0"}, padrao="0")
                        break
                    else:
                        print("Mídia não encontrada.")

            elif escolha == "2":
                print("\n--- Listagem de Mídias ---")
                print("0. Voltar")
                print("1. Listar músicas")
                print("2. Listar podcasts")
                print("3. Listar todas")
                sub_escolha = input("Escolha uma opção: ").strip()

                if sub_escolha == "0":
                    continue
                if sub_escolha == "1":
                    musicas = [m for m in self.midias if isinstance(m, Musica)]
                    if musicas:
                        print("\n--- Músicas ---")
                        for musica in musicas:
                            print(f"- {musica} ({musica.reproducoes} reproduções)")
                    else:
                        print("Nenhuma música cadastrada.")
                elif sub_escolha == "2":
                    podcasts = [p for p in self.midias if isinstance(p, Podcast)]
                    if podcasts:
                        print("\n--- Podcasts ---")
                        for podcast in podcasts:
                            print(f"- {podcast.titulo} — {podcast.host} ({podcast.reproducoes} reproduções)")
                    else:
                        print("Nenhum podcast cadastrado.")
                elif sub_escolha == "3":
                    if not self.midias:
                        print("Nenhuma mídia cadastrada.")
                    else:
                        print("\n--- Todas as Mídias ---")
                        for midia in self.midias:
                            etiqueta = "Música" if isinstance(midia, Musica) else "Podcast"
                            print(f"- [{etiqueta}] {midia}")
                else:
                    print("Opção inválida.")
                
            elif escolha == "3":
                nome_playlist = input("Digite o nome da nova playlist (ou '0' para cancelar): ").strip()
                if nome_playlist == "0":
                    continue
                if any(p.nome.lower() == nome_playlist.lower() for p in usuario.playlists):
                    print("Você já possui uma playlist com esse nome.")
                else:
                    playlist = usuario.criar_playlist(nome_playlist)
                    print(f"Playlist '{nome_playlist}' criada!")
                    self._menu_edicao_playlist(playlist)
                    self.salvar_dados()
            
            elif escolha == "4":
                if not usuario.playlists:
                    print("Você ainda não tem playlists.")
                    continue

                while True:
                    print(f"\n--- Playlists de {usuario.nome} ---")
                    print("0. Voltar")
                    for idx, pl in enumerate(usuario.playlists, start=1):
                        print(f"{idx}. {pl}")

                    escolha_playlist = input("Selecione uma playlist: ").strip()
                    if escolha_playlist == "0":
                        break

                    playlist_selecionada = None
                    if escolha_playlist.isdigit():
                        indice = int(escolha_playlist)
                        if 1 <= indice <= len(usuario.playlists):
                            playlist_selecionada = usuario.playlists[indice - 1]
                    else:
                        for pl in usuario.playlists:
                            if pl.nome.lower() == escolha_playlist.lower():
                                playlist_selecionada = pl
                                break

                    if not playlist_selecionada:
                        print("Playlist não encontrada.")
                        continue

                    if not playlist_selecionada.itens:
                        print("Playlist está vazia.")
                        continue

                    while True:
                        print(f"\n--- Itens de '{playlist_selecionada.nome}' ---")
                        print("0. Voltar")
                        for idx, mid in enumerate(playlist_selecionada.itens, start=1):
                            tipo = "Música" if isinstance(mid, Musica) else "Podcast"
                            print(f"{idx}. [{tipo}] {mid}")

                        escolha_item = input("Escolha por onde iniciar a reprodução: ").strip()
                        if escolha_item == "0":
                            break

                        indice_inicial = None
                        if escolha_item.isdigit():
                            idx_item = int(escolha_item)
                            if 1 <= idx_item <= len(playlist_selecionada.itens):
                                indice_inicial = idx_item - 1
                        else:
                            for idx_m, mid in enumerate(playlist_selecionada.itens):
                                if mid.titulo.lower() == escolha_item.lower():
                                    indice_inicial = idx_m
                                    break

                        if indice_inicial is None:
                            print("Mídia não encontrada na playlist.")
                            continue

                        self._reproduzir_playlist_interativo(playlist_selecionada, indice_inicial)
                        self.salvar_dados()
                        break
            
            elif escolha == "5":
                todas_playlists = self._obter_playlists_disponiveis()

                if not todas_playlists:
                    print("Nenhuma playlist cadastrada no sistema.")
                    continue

                print("\n--- Playlists disponíveis ---")
                print("0. Voltar")
                for idx, (pl, dono) in enumerate(todas_playlists, start=1):
                    print(f"{idx}. {pl.nome} (de {dono.nome}) - {len(pl.itens)} itens, {pl.reproducoes} reproduções")

                escolha_playlist = input("Digite o número ou nome da playlist para reproduzir ela (ou 0 pra voltar) ").strip()
                if escolha_playlist == "0":
                    continue
                playlist_encontrada = None

                if escolha_playlist.isdigit():
                    indice = int(escolha_playlist)
                    if 1 <= indice <= len(todas_playlists):
                        playlist_encontrada = todas_playlists[indice - 1][0]
                else:
                    for pl, _ in todas_playlists:
                        if pl.nome.lower() == escolha_playlist.lower():
                            playlist_encontrada = pl
                            break

                if playlist_encontrada:
                    if not playlist_encontrada.itens:
                        print("Playlist está vazia.")
                        continue
                    self._reproduzir_playlist_interativo(playlist_encontrada, 0)
                    self.salvar_dados()
                else:
                    print("Playlist não encontrada.")

            elif escolha == "6":
                nome_playlist = input("Digite o nome da playlist para adicionar mídia: ")
                playlist_encontrada = None
                for p in usuario.playlists:
                    if p.nome.lower() == nome_playlist.lower():
                        playlist_encontrada = p
                        break
                if not playlist_encontrada:
                    print("Playlist não encontrada.")
                    continue
                self._menu_edicao_playlist(playlist_encontrada)
                self.salvar_dados()

            elif escolha == "7":
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

            else:
                print("Opção inválida.")        
