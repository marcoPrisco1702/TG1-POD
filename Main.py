from Streaming.Menu import Menu

def main():
    print("=== SISTEMA DE STREAMING ===\n")
    menu = Menu()
    print("carregando dados...")

    # Carrega dados iniciais (se tiver)
    try:
        menu.carregar_dados()
    except Exception as e:
        menu.log_erro(f"Erro ao carregar dados iniciais: {e}")
        print("Falha ao carregar dados iniciais. Veja logs/erros.log.")

    print("dados carregados; entrando no menu...")
    # Inicia o menu interativo
    try:
        menu.menu_principal()
    except KeyboardInterrupt:
        print("\nEncerrando o programa...")
    except Exception as e:
        menu.log_erro(f"Erro durante execução do menu: {e}")
        print("Ocorreu um erro. Verifique o arquivo logs/erros.log.")


if __name__ == "__main__":
    main()