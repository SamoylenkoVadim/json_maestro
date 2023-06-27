import core.asl_models.actions.actions as act
import core.asl_models.operators.comparators as cmp
import core.asl_models.operators.operators as op
import core.asl_models.requirements.requirements as rq
from core.model.registered import registered_factories


class ABEntityConfig:
    def __init__(self):
        self.init_requirements()
        self.init_actions()
        self.init_factories()
        self.init_operators()

    def init_requirements(self):
        rq.requirements[None] = rq.Requirement
        rq.requirements["and"] = rq.AndRequirement
        rq.requirements["or"] = rq.OrRequirement
        rq.requirements["not"] = rq.NotRequirement
        rq.requirements["external"] = rq.ExternalRequirement
        rq.requirements["true"] = rq.TrueRequirement
        rq.requirements["false"] = rq.FalseRequirement


    def init_actions(self):
        act.actions[None] = act.Action
        act.actions["external"] = act.ExternalAction
        act.actions["requirement"] = act.RequirementAction
        act.actions["choice"] = act.ChoiceAction
        act.actions["else"] = act.ElseAction
        act.actions["composite"] = act.CompositeAction
        act.actions["hello"] = act.Hello

    def init_factories(self):
        registered_factories[act.Action] = act.action_factory
        registered_factories[rq.Requirement] = rq.requirement_factory
        registered_factories[op.Operator] = op.operator_factory
        registered_factories[cmp.Comparator] = cmp.comparator_factory

    def init_operators(self):
        op.operators["more"] = op.MoreOperator
        op.operators["more_or_equal"] = op.MoreOrEqualOperator
        op.operators["equal"] = op.EqualOperator
        op.operators["not_equal"] = op.NotEqualOperator
        op.operators["less"] = op.LessOperator
        op.operators["less_or_equal"] = op.LessOrEqualOperator
        op.operators["exists"] = op.Exists
        op.operators["composite"] = op.CompositeOperator
        op.operators["any"] = op.AnyOperator
        op.operators["in"] = op.InOperator
        op.operators["endswith"] = op.EndsWithOperator
        op.operators["startswith"] = op.StartsWithOperator
