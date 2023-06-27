
from typing import Dict, List, Any, Optional

from lazy import lazy
import core.logging_utils.logger_constants as log_const
from core.asl_models.base_asl import BaseASL
from core.asl_models.requirements.requirements import Requirement
from core.model.factory import build_factory, factory, list_factory
from core.model.registered import Registered
from core.utils.exceptions import ExperimentException


actions = Registered()
action_factory = build_factory(actions)

external_actions = dict()


class Action(BaseASL):
    def __init__(self, items: Dict[str, Any], id: Optional[str] = None):
        super().__init__(items, id)
        self.key_name_value = log_const.ACTION_RUN_VALUE

    async def run(self, message):
        log_params = self._log_params()
        raise ExperimentException("Action type is not specified")


class CommandAction(Action):
    DEFAULT_REQUEST_TYPE = "kafka"
    version: Optional[int]
    command: str
    request_type: Optional[str]
    request_data: Optional[Dict]

    async def run(self, message):
        await super(CommandAction, self).run(message)
        return None


class ExternalAction(CommandAction):
    version: Optional[int]
    command: str
    action: str

    def __init__(self, items: Dict[str, Any], id: Optional[str] = None):
        super(ExternalAction, self).__init__(items, id)
        self._action_key = items["action"]

    async def run(self, message):
        action = external_actions[self._action_key]
        return await action.run(message)


class RequirementAction(Action):
    version: Optional[int]
    requirement: Requirement
    action: Optional[Action]  # O_o
    item: Optional[Action]  # o_O

    def __init__(self, items: Dict[str, Any], id: Optional[str] = None):
        super(RequirementAction, self).__init__(items, id)
        self._requirement = items["requirement"]
        # can be used not only with actions but with every entity which implements Action interface
        # to not change statics "item" key is added
        self._item = items.get("item") or items["action"]

    @lazy
    @factory(Requirement)
    def requirement(self):
        return self._requirement

    @lazy
    @factory(Action)
    def internal_item(self):
        return self._item

    async def run(self, message):
        result = None
        if self.requirement.check(message):
            result = await self.internal_item.run(message)
        return result


class ChoiceAction(Action):
    version: Optional[int]
    requirement_items: RequirementAction  # O_o
    requirement_actions: RequirementAction  # o_O
    else_item: Action  # O_o
    else_action: Action  # o_O

    def __init__(self, items: Dict[str, Any], id: Optional[str] = None):
        super(ChoiceAction, self).__init__(items, id)
        # can be used not only with actions but with every entity which implements Action interface
        # to not change statics "*_item" keys are added
        self._requirement_items = items.get("requirement_items") or items["requirement_actions"]
        self._else_action = items.get("else_item") or items.get("else_action")

    @lazy
    @list_factory(RequirementAction)
    def items(self):
        return self._requirement_items

    @lazy
    @factory(Action)
    def else_item(self):
        return self._else_action

    async def run(self, message):
        result = None
        choice_is_made = False
        for item in self.items:
            checked = item.requirement.check(message)
            if checked:
                result = await item.internal_item.run(message)
                choice_is_made = True
                break
        if not choice_is_made and self._else_action:
            result = await self.else_item.run(message)
        return result


class ElseAction(Action):
    version: Optional[int]
    item: Requirement  # O_o
    action: Requirement  # o_O
    else_item: Action  # O_o
    else_action: Action  # o_O

    def __init__(self, items: Dict[str, Any], id: Optional[str] = None):
        super(ElseAction, self).__init__(items, id)
        self._requirement = items["requirement"]
        # can be used not only with actions but with every entity which implements Action interface
        # to not change statics "*item" keys are added
        self._item = items.get("item") or items["action"]
        self._else_item = items.get("else_action") or items.get("else_item")

    @lazy
    @factory(Requirement)
    def requirement(self):
        return self._requirement

    @lazy
    @factory(Action)
    def item(self):
        return self._item

    @lazy
    @factory(Action)
    def else_item(self):
        return self._else_item

    async def run(self, message):
        result = None
        if self.requirement.check(message):
            result = await self.item.run(message)
        elif self._else_item:
            result = await self.else_item.run(message)
        return result


class CompositeAction(Action):
    version: Optional[int]
    actions: List[Action]

    def __init__(self, items: Dict[str, Any], id: Optional[str] = None):
        super(CompositeAction, self).__init__(items, id)
        self._actions = items.get("actions") or []

    @lazy
    @list_factory(Action)
    def actions(self):
        return self._actions

    async def run(self, message):
        commands = []
        for action in self.actions:
            action_result = await action.run(message)
            if action_result:
                commands += action_result
        return commands


class Hello(Action):
    def __init__(self, items: Dict[str, Any], id: Optional[str] = None):
        super(Hello, self).__init__(items, id)

    async def run(self, message):
        print("Hello")
