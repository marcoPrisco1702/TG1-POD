# TG1-POD
Trabalho em grupo 1 de Programacao Orientada a Dados


Ordem pra fazer as classes pelo gpt só pra termos uma ideia:

1.	Fundação (modelos base)

	•	arquivo_de_midia.py → classe abstrata ArquivoDeMidia com titulo, duracao, artista, reproducoes, reproduzir() e __eq__() (título+artista).  ￼

	2.	Mídias concretas

	•	musica.py (genero, avaliacoes, avaliar(nota) 0–5; implementa reproduzir).
	•	podcast.py (episodio, temporada, host; implementa reproduzir).  ￼

	3.	Usuário e Playlists

	•	usuario.py (qntd_instancias, nome, playlists, historico; ouvir_midia, criar_playlist).
	•	playlist.py (nome, usuario, itens, reproducoes; adicionar_midia, remover_midia, reproduzir incrementando contadores; operadores __add__, __len__, __getitem__, __eq__).  ￼

	4.	Análises/relatórios

	•	analises.py (métodos estáticos: top_musicas_reproduzidas, playlist_mais_popular, usuario_mais_ativo, media_avaliacoes, total_reproducoes).  ￼
	•	Salvar relatório em relatorios/ e erros em logs/.  ￼

	5.	Interface/Execução

	•	menu.py (opções do menu e, ao entrar como usuário, ações listadas no enunciado).  ￼
	•	main.py (ponto de entrada que exibe o menu).  ￼

	6.	Empacotamento e organização

	•	Estrutura de pacote Streaming/ com __init__.py e todos os módulos acima; pastas logs/, relatorios/, config/.  ￼
	•	Todas as classes com __str__ e __repr__, docstrings e boas práticas.

	7.	Inovação (+1 ponto extra se for a mais votada)
