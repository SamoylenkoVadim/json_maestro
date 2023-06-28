import asyncio
import core.basic_entities.actions.actions as actions
import core.basic_entities.requirements.requirements as requirements
from core.basic_entities.actions.actions import Action
from core.basic_entities.requirements.requirements import Requirement
from core.configs.entity_config import EntityConfig
from core.configs.configs import actions_raw, external_actions_raw, external_requirements_raw
from core.model.factory import dict_factory
from core.model.message import Message


class MaestroModel:
    def __init__(self):
        print("MaestroModel.__init__ started.")
        self._actions = None
        EntityConfig()
        self.build_data()
        print("MaestroModel.__init__ finished.")

    @dict_factory(Action)
    def _build_external_actions(self):
        return external_actions_raw

    @dict_factory(Requirement)
    def _build_external_requirements(self):
        return external_requirements_raw

    @dict_factory(Action)
    def _build_actions(self):
        return actions_raw

    def build_data(self):
        actions.external_actions = self._build_external_actions()
        requirements.external_requirements = self._build_external_requirements()
        self._actions = self._build_actions()

    async def run(self, message: Message):
        for action_name, action in self._actions.items():
            await self.run_one(action, message)

    @staticmethod
    async def run_one(action, message):
        try:
            await action.run(message)
        except Exception as e:
            print(e)


async def main():
    a = MaestroModel()
    msg = Message("hello")
    await a.run(msg)

if __name__ == "__main__":
    asyncio.run(main())
