import asyncio

import core.asl_models.actions.actions as actions
import core.asl_models.requirements.requirements as requirements
from core.asl_models.actions.actions import Action
from core.asl_models.requirements.requirements import Requirement
from core.configs.ab_entity_config import ABEntityConfig
from core.configs.configs import configs, experiments_raw, external_actions_raw, external_requirements_raw
from core.model.factory import dict_factory
from core.model.message import Message


class FLModel:
    def __init__(self):
        print("FLModel.__init__ started.")
        ABEntityConfig()
        self.build_data()
        print("FLModel.__init__ finished.")

    @dict_factory(Action)
    def build_external_actions(self):
        return external_actions_raw

    @dict_factory(Requirement)
    def build_external_requirements(self):
        return external_requirements_raw

    @dict_factory(Action)
    def build_experiments(self):
        return experiments_raw

    def build_data(self):
        actions.external_actions = self.build_external_actions()
        requirements.external_requirements = self.build_external_requirements()
        self._experiments = self.build_experiments()

    async def run(self, message: Message):
        for exp_name, exp_value in self._experiments.items():
            await self.run_one(exp_value, message)

    async def run_one(self, experiment, message):
        try:
            await experiment.run(message)
        except Exception as e:
            print(e)


async def main():
    a = FLModel()
    msg = Message("hello")
    await a.run(msg)

if __name__ == "__main__":
    asyncio.run(main())
