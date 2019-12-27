class BaseDeploymentConfig():

    PARSER_USAGE = ""

    @classmethod
    def validate_config(cls, args):
        return {}