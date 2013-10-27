import unittest
import sys

from os import remove, path

from smartconf import conf, TempFile

CUR_DIR = path.dirname(__file__)


SAMPLE_CONF = """
[dbconnection]
host = host
user = user
passwd = realpwd
port = 3306
"""

# this is written on a python module that will be used as configuration
SAMPLE_DEFAULTS = """
dbconnection = {
 'host': 'host',
 'user': 'user',
 'port': 3306,
 'passwd' : "passwd",
}

logging = {
  'simplelist': [],
}

_HIDDEN = 'not found'
"""

SAMPLE_CONF_WRONG_TYPE = """
[logging]
simplelist = string
"""

TMP_SAMPLE_DEFAULTS = None
SAMPLE_DEFAULTS_MODULE = 'temp_defaults'


def setUpModule():
    global TMP_SAMPLE_DEFAULTS
    TMP_SAMPLE_DEFAULTS = path.join(CUR_DIR, 'temp_defaults.py')
    sys.path.insert(0, CUR_DIR)
    with open(TMP_SAMPLE_DEFAULTS, 'w') as wr:
        wr.write(SAMPLE_DEFAULTS)


def tearDownModule():
    remove(TMP_SAMPLE_DEFAULTS)
    sys.path.remove(sys.path[0])


class TestConfiguration(unittest.TestCase):
    def test_configuration_items(self):
        with TempFile(content=SAMPLE_CONF) as fname:
             cfg = conf.Conf(fname, {})
             desired = {'host': 'host', 'passwd': 'realpwd', 'port': '3306', 'user': 'user'}
             self.assertEqual(cfg['dbconnection'], desired)
             self.assertEqual(cfg.dbconnection, desired)

    def test_conversion(self):
        obj1 = ['one', 'two']
        self.assertEqual(conf._convert_to_type(obj1, 'one;two'), obj1)
        with self.assertRaises(TypeError):
            conf._convert_to_type(obj1, '100')

        with self.assertRaises(TypeError):
            conf._convert_to_type(100, 'string')

    def test_configuration_with_defaults(self):
        with TempFile(content=SAMPLE_CONF) as fname:
            defaults = {'sub' : {'x1': 1, 'x2': 2}}
            cfg = conf.Conf(fname, defaults)
            self.assertEqual(cfg['sub'], {'x1': 1, 'x2': 2})

    def test_load_conf(self):
        cfg = conf.load_conf(SAMPLE_DEFAULTS_MODULE, SAMPLE_CONF)
        self.assertEqual(cfg.dbconnection['port'], 3306)

    def test_args_to_dict_replace_arguments(self):
        settings = ["x1.x2:val", "x2.x3:val2"]
        cur_dic = {'x1': {'x2': 'orig'}, 'x2': {'x3': 'orig2'}}
        desired = {
            'x1': {'x2': 'val'},
            'x2': {'x3': 'val2'}
        }
        self.assertEqual(conf.args_to_dict(settings, cur_dic), desired)

    def test_args_to_dict_single_value(self):
        settings = ["x1:val"]
        cur = {"x1": "orig"}
        self.assertEqual(conf.args_to_dict(settings, cur), {"x1": "val"})

    def test_args_to_dict_no_side_effect(self):
        settings = ["x1:val"]
        cur = {"x1": "orig"}
        conf.args_to_dict(settings, cur)
        self.assertEqual(cur, {"x1": "orig"})

    def test_args_not_exist_fails(self):
        settings = ["x1:val"]
        with self.assertRaises(AssertionError):
            conf.args_to_dict(settings, {})

    def test_dic_to_args(self):
        dic = {"x1": {"x2": "val1"}, "x2": "val3"}
        des = ["x1.x2:val1", "x2:val3"]
        self.assertEqual(sorted(conf.dict_to_args(dic)), des)

    def test_skip_hidden_elements(self):
        with TempFile(content=SAMPLE_DEFAULTS):
            cfg = conf.load_conf(conf_module=SAMPLE_DEFAULTS_MODULE)
            self.assertTrue('_HIDDEN' not in cfg)

    def test_type_checking(self):
        """Check that passing arguments with a different type of the
        default makes it fail, optional
        """
        with TempFile(content=SAMPLE_CONF_WRONG_TYPE) as fname:
            with self.assertRaises(TypeError):
                conf.load_conf(conf_module=SAMPLE_DEFAULTS_MODULE, ini_conf=fname)

    def test_type_conversion(self):
        ls = "one;two;three"
        self.assertEqual(conf._convert_to_type([1, 2, 3], ls), ["one", "two", "three"])
        self.assertEqual(conf._convert_to_type(230, "100"), 100)

    def test_config_parser_to_dict(self):
        with TempFile(content=SAMPLE_CONF) as fname:
            res = conf.config_parser_to_dict(fname)

            desired = {'dbconnection': {'host': 'host',
                                        'passwd': 'realpwd',
                                        'port': '3306',
                                        'user': 'user'}}

            self.assertEqual(res, desired)
