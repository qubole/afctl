class BaseDeploymentConfig():

    CONFIG_PARSER_USAGE = ""
    DEPLOY_PARSER_USAGE = ""

    @classmethod
    def generate_dirs(cls, main_dir):
        pass

    @classmethod
    def validate_config(cls, args):
        pass

    @classmethod
    def deploy_project(cls, args, configs):
        pass