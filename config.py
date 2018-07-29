import argparse
import os


class ConfigOption:

    cli = ""
    env_variable = ""
    mandatory = None
    prompt = None

    def __init__(self, variable, cli_option, mandatory=True, prompt=True):
        self.variable = variable
        self.cli_option = cli_option
        self.mandatory = mandatory
        self.prompt = prompt


class Config:

    def __init__(self, options):
        self.options = options

    def get(self):
        parser = argparse.ArgumentParser()
        for option in self.options:
            parser.add_argument(option.cli_option, dest=option.variable, nargs=1)
        args = parser.parse_args()

        config = {}
        missing = []

        for option in self.options:
            if vars(args)[option.variable] is not None:
                config[option.variable] = vars(args)[option.variable][0]
            else:
                if option.variable in os.environ.keys():
                    config[option.variable] = os.environ[option.variable]
                elif option.mandatory:
                    if option.prompt:
                        config[option.variable] = input(option.variable + ': ')
                    else:
                        missing.append(option.variable)
                else:
                    config[option.variable] = None

        if len(missing) > 0:
            raise Exception("The following variables are missing: " + ', '.join(missing))

        return config
