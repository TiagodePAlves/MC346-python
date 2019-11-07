from main import main, time


# seletor de modo de execução
TIMING = False

if __name__ == "__main__":
    if TIMING:
        # dependendo do grafo
        time(input_file='test.txt')
    else:
        main()
