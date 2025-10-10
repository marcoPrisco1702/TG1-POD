from __future__ import annotations
from typing import List, Dict, Optional
import os
from datetime import datetime
from .Musica import Musica
from .Playlist import Playlist
from .Usuario import Usuario

class Analises:
    @staticmethod
    
    def top_musicas_reproduzidas(musicas: List[Musica], top_n: int) -> List[Musica]:
        if not musicas or top_n <= 0:
            return []
        ordenadas = sorted(musicas, reverse=True, key=lambda musica: musica.reproducoes) # ordena musicas por reproducoes descrescente
        return ordenadas[:top_n]

    @staticmethod
    def playlist_mais_popular(playlists: List[Playlist]):
        if not playlists:
            return None
        return max(playlists, key=lambda playlist: playlist.reproducoes)

    @staticmethod
    def usuario_mais_ativo(usuarios: List[Usuario]):
        if not usuarios:
            return None
        return max(
            usuarios,
            key=lambda usuario: getattr(usuario, "total_midias_ouvidas", len(usuario.historico)),
        ) # usuario com mais midias ouvidas

    @staticmethod
    def media_avaliacoes(musicas: List[Musica]) -> Dict[str, float]:
        medias: Dict[str, float] = {}
        for musica in musicas or []:
            if getattr(musica, "avaliacoes", None):
                medias[musica.titulo] = sum(musica.avaliacoes) / len(musica.avaliacoes)
        return medias

    @staticmethod
    def total_reproducoes(usuarios: List[Usuario]):
        if not usuarios:
            return 0
        return sum(getattr(u, "total_midias_ouvidas", len(u.historico)) for u in usuarios)

    @staticmethod
    def gerar_relatorio(usuarios: List[Usuario],playlists: List[Playlist],musicas: List[Musica],caminho_pasta_relat: str = os.path.join("relatorios"),nome_arquivo: str = "relatorio.txt",top_n: int = 5,):
        os.makedirs(caminho_pasta_relat, exist_ok=True)
        destino = os.path.join(caminho_pasta_relat, nome_arquivo)

        
        total_execucoes = Analises.total_reproducoes(usuarios)
        mais_ouvida = Analises.playlist_mais_popular(playlists)
        medias = Analises.media_avaliacoes(musicas)
        top = Analises.top_musicas_reproduzidas(musicas, top_n)
        mais_ativo = Analises.usuario_mais_ativo(usuarios)

        
        linhas: List[str] = []
        linhas.append("=" * 70)
        linhas.append(f"RELATÓRIO DO SISTEMA DE STREAMING — {datetime.now():%Y-%m-%d %H:%M:%S}") # a data e hora atuais
        linhas.append("=" * 70)
        linhas.append("")

        linhas.append(f"Total de usuários: {len(usuarios)}")
        linhas.append(f"Total de playlists: {len(playlists)}")
        linhas.append(f"Total de músicas cadastradas: {len(musicas)}")
        linhas.append(f"Total de reproduções (usuários): {total_execucoes}")
        linhas.append("")

        linhas.append("Top músicas por reproduções:")
        if top:
            for i, m in enumerate(top, start=1):
                linhas.append(f"  {i}. {m.titulo} — {m.artista}  ({m.reproducoes}x)")
        else:
            linhas.append("  (nenhuma música ou sem reproduções)")
        linhas.append("")

        linhas.append("Playlist mais popular:")
        if mais_ouvida is not None:
            linhas.append(
                f"  {mais_ouvida.nome} (de {mais_ouvida.usuario.nome}) — {mais_ouvida.reproducoes} execuções"
            )
        else:
            linhas.append("  (nenhuma playlist disponível)")
        linhas.append("")

        linhas.append("Usuário mais ativo:")
        if mais_ativo is not None:
            linhas.append(
                f"  {mais_ativo.nome} — {getattr(mais_ativo, 'total_midias_ouvidas', len(mais_ativo.historico))} mídias ouvidas"
            )
        else:
            linhas.append("  (nenhum usuário disponível)")
        linhas.append("")

        linhas.append("Médias de avaliação por música:")
        if medias:
            for titulo, media in sorted(medias.items(), key=lambda kv: kv[0].casefold()):
                linhas.append(f"  {titulo}: {media:.2f}")
        else:
            linhas.append("  (não há avaliações registradas)")
        linhas.append("")

        conteudo = "\n".join(linhas) + "\n"

        with open(destino, "w", encoding="utf-8") as f:
            f.write(conteudo)

        return destino
