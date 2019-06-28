import yaml
import os


class Config:
    """
    load configuration files
    """
    def __init__(self, path_to_config='../conf.yml'):
        self.path_to_config = path_to_config
        self.cfg = self.load_config()

    def load_config(self):
        try:
            with open(self.path_to_config, 'r') as config:
                return yaml.load(config)
        except IOError as e:
            print(e)

    @staticmethod
    def load_env_conf(dm_conf):
        variables = dm_conf['env_variables']
        for var in variables:
            if var in os.environ:
                try:
                    dm_conf[var.lower()] = os.getenv(var)
                except KeyError as e:
                    print(e)
        return dm_conf
