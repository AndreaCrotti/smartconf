"""
Configuration is read from a default configuration file, from an
optional ini file which overrides it and optionally from a key/value
entries passed from the command line
"""

import logging

from importlib import import_module
from inspect import getmembers

from ConfigParser import ConfigParser

KEY_VAL_SEP = ':'

GLOBAL_CONF = None

logger = logging.getLogger(__name__)


def _convert_to_type(obj1, to_convert):
    """Convert the to_convert string to the type of the given object
    """
    def _report_error():
        raise TypeError("to_convert string %s can't be converted to %s" % (str(to_convert), type(obj1)))

    if isinstance(obj1, list):
        if ";" not in to_convert:
            _report_error()
        return to_convert.split(";")
    else:
        try:
            return type(obj1)(to_convert)
        except ValueError:
            _report_error()


def load_conf(conf_module, ini_conf=None, extra=None):
    """Load the configuration, first reading the default configuration
    and merging it with the given ini file
    """
    # TODO: might add caching with the global value, but then we
    # should check if the arguments given are now different
    default_conf = module_to_dict(conf_module)
    conf = Conf(ini_conf, default_conf)
    if extra:
        conf.update_from_vars(extra)

    return conf

# TODO: use this function to refactor the Conf class
def config_parser_to_dict(conf_file):
    """Take a ConfigParser object that has already parsed a file and
    return a dictionary with its values
    """
    conf_dict = {}
    conf = ConfigParser()
    conf.read(conf_file)
    for sec in conf.sections():
        if sec not in conf_dict:
            conf_dict[sec] = {}

        for k, v in conf.items(sec):
            conf_dict[sec][k] = v

    return conf_dict


class Conf:
    def __init__(self, conf_file=None, default=None):
        self.conf = ConfigParser()
        self.conf_dict = default or {}
        if conf_file is not None:
            self.conf.read(conf_file)

        self._conf_to_dict()

    def _conf_to_dict(self):
        for sec in self.conf.sections():
            if sec not in self.conf_dict:
                self.conf_dict[sec] = {}

            for k, v in self.conf.items(sec):
                if k in self.conf_dict[sec]:
                    old = self.conf_dict[sec][k]
                    logger.debug("updating key/value %s/%s" % (k, v))
                    self.conf_dict[sec][k] = _convert_to_type(old, v)
                else:
                    self.conf_dict[sec][k] = v

    def __contains__(self, attr):
        return attr in self.conf_dict

    def __setitem__(self, attr, val):
        self.conf_dict[attr] = val

    def __getitem__(self, item):
        return self.conf_dict[item]

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def to_args(self):
        return list(dict_to_args(self.conf_dict))

    def update_from_vars(self, varargs):
        # the update adds new entries if they don't exist, but
        # args_to_dict would fail if there are entries which were not
        # in the original dictionary, so using update it's safe in
        # this case
        tmp_dic = args_to_dict(varargs, self.conf_dict)
        self.conf_dict.update(tmp_dic)


def module_to_dict(conf_module):
    """Take a module and return a dictionary with all the public
    variables and their values
    """
    m = import_module(conf_module)
    return dict([x for x in getmembers(m) if not x[0].startswith('_')])


def args_to_dict(var_args, current_dict):
    """Take a list of variable settings and construct a dictionary
    [x1.x2:val] -> {'x1': {'x2': val}}
    """
    tmp = dict(current_dict)
    sub = tmp
    for v in var_args:
        key, val = v.split(KEY_VAL_SEP)
        full = key.split('.')
        for k in full[:-1]:
            sub = tmp[k]

        assert full[-1] in sub, "the settings must already contain the variable"
        sub[full[-1]] = val

    return tmp


def dict_to_args(d, prefix=()):
    """Return a list of valid arguments that can be passed, in the
    form [k1.k2:val1, k1.k3:val3, k2.k3:val2]
    Depth first visit of the dictionary yielding a value when reaching
    the leaf.
    """
    for k, v in d.iteritems():
        if isinstance(v, dict):
            for x in dict_to_args(v, prefix + (k,)):
                yield x
        else:
            yield ".".join(prefix + (k,)) + ":" + str(v)
