from os import path
from smartconf.conf import load_conf

INI_FILE = path.join(path.dirname(__file__), 'sample.ini')
CONF_FILE = path.join(path.dirname(__file__), 'defaults')


def main():
    conf = load_conf('example.defaults', INI_FILE)


if __name__ == '__main__':
    main()
