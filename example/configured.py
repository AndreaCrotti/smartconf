import argparse

from os import path
from smartconf.conf import load_conf, dict_to_args, args_to_dict

INI_FILE = path.join(path.dirname(__file__), 'sample.ini')
CONF_FILE = path.join(path.dirname(__file__), 'defaults')


def main():
    conf = load_conf('example.defaults', INI_FILE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing')
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('settings', nargs='*')

    ns = parser.parse_args()
    conf = load_conf('example.defaults', INI_FILE)

    if ns.list:
        print('\n'.join(conf.to_args()))

    conf.update_from_vars(ns.settings)
    print(conf)
