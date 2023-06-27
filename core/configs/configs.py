import os
from core.configs.statics import StaticsJson, StaticsYaml

static_path = os.path.normpath(os.environ["STATIC_PATH"])
external_path = os.path.join(static_path, "external")
configs_path = os.path.normpath(os.environ["CONFIG_PATH"])

configs = StaticsYaml(configs_path)

experiments_raw = StaticsJson(static_path, json_type="all")
external_actions_raw = StaticsJson(external_path, json_type="actions")
external_requirements_raw = StaticsJson(external_path, json_type="requirements")
