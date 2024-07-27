import coleta
import limpeza
import logging


def main():
    """Função principal para executar as tarefas de coleta e limpeza."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        logging.info('Iniciando a coleta de dados.')
        coleta.coleta()
        logging.info('Coleta de dados concluída.')

        logging.info('Iniciando a gravação no banco de dados.')
        limpeza.grava_bd()
        logging.info('Gravação no banco de dados concluída.')

    except Exception as e:
        logging.error(f'Ocorreu um erro: {e}')
        raise


if __name__ == '__main__':
    main()
