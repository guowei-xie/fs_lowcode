import os
import configparser

root = os.path.dirname(__file__)


class Config:
    def __init__(self, method):
        """
        输入 test 或者是 default
        :param method:
        """
        if method != 'test' and method != "default":
            exit("please init config with test or default")
        config = configparser.ConfigParser()
        config.readfp(open("{0}/{1}.cfg".format(root, method)))
        self.method = method
        self.config = config

    def get(self, key, field):
        return self.config.get(key, field)


my_conf = Config('default')