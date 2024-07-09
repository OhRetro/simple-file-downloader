from dotenv import dotenv_values

ENV_VAR = dotenv_values()

def get_env_var(name: str):
    return ENV_VAR.get(name, None)
