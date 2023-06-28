from typing import List, Optional, Dict, Any
from lazy import lazy
import core.logging_utils.logger_constants as log_const
from core.basic_entities.base_entity import BaseEntity
from core.model.factory import build_factory, list_factory, factory
from core.model.message import Message
from core.model.registered import Registered
from core.utils.exceptions import ActionException


requirements = Registered()

requirement_factory = build_factory(requirements)

external_requirements = dict()


class Requirement(BaseEntity):
    def __init__(self, items: Dict[str, Any], id: Optional[str] = None) -> None:
        super().__init__(items, id)
        self.items = items or {}
        self.key_name_value = log_const.REQUIREMENT_CHECK_VALUE

    def check(self, message: Message):
        log_params = self._log_params()
        raise ActionException("Requirement type is not specified")


class ExternalRequirement(Requirement):
    requirement: str

    def __init__(self, items: Dict[str, Any], id: Optional[str] = None) -> None:
        super(ExternalRequirement, self).__init__(items, id)
        self.requirement = items["requirement"]

    def check(self, message):
        requirement = external_requirements[self.requirement]
        return requirement.check(message)


class CompositeRequirement(Requirement):
    requirements: List[Requirement]

    def __init__(self, items: Dict[str, Any], id: Optional[str] = None) -> None:
        super(CompositeRequirement, self).__init__(items, id)
        self._requirements = items["requirements"]

    @lazy
    @list_factory(Requirement)
    def requirements(self):
        return self._requirements


class AndRequirement(CompositeRequirement):

    def check(self, message) -> bool:
        return all(requirement.check(message)
                   for requirement in self.requirements)


class OrRequirement(CompositeRequirement):

    def check(self, message) -> bool:
        return any(requirement.check(message)
                   for requirement in self.requirements)


class NotRequirement(Requirement):
    requirement: Requirement

    def __init__(self, items: Dict[str, Any], id: Optional[str] = None) -> None:
        super(NotRequirement, self).__init__(items, id)
        self._requirement = items["requirement"]

    @lazy
    @factory(Requirement)
    def requirement(self):
        return self._requirement

    def check(self, message) -> bool:
        return not self.requirement.check(message)


class TrueRequirement(Requirement):
    def check(self, message) -> bool:
        return True


class FalseRequirement(Requirement):
    def check(self, message) -> bool:
        return False


