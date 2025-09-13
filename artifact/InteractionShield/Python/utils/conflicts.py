import random
import json

from sympy import Interval, Intersection, Symbol, Union, S
from sympy.sets import EmptySet

from Python.utils.constant import (
    CONFLICTS_RANKING_D,
    DETERMINISTIC,
    CONDITIONAL,
    LOW,
    MEDIUM,
    HIGH,
    CONFLICTS_ID_D,
    CONFLICTS_D,
)
from Python.utils.enums import (
    AppTypeEnum,
    ConflictEnum,
    ActionInterEnum,
    TcaEnum,
    TriggerInterEnum,
    ChainInterEnum,
    LogicalRelEnum,
    TemporalRelEnum,
    CausalRelEnum,
    CoreferRelEnum,
)


class EventConflictsClass:
    def __init__(self, rules_l, interference_ul, type_u):
        self.rules = rules_l
        self.interferences = interference_ul
        self.type = type_u
        self.ranking = self.get_ranking()
        self.possible = self.get_possible()
        self.update_actions()

    def update_actions(self):
        for rule_u in self.rules:
            rule_u.action.add_conflicts(self)

    def clear_actions(self):
        for rule_u in self.rules:
            rule_u.action.clear()

    def get_possible(self):
        possible_i = DETERMINISTIC
        if self.interferences[1] is not None:
            possible_i = CONDITIONAL
        return possible_i

    def get_interferences(self):
        if self.interferences[2] is not None:
            return self.interferences[2]
        return self.interferences[3]

    def get_ranking(self):
        return CONFLICTS_RANKING_D.get(self.type, LOW)

    def calculate_penalty(self):
        risk_score = self.rules[-1].action.get_total_risk()
        if self.type not in [ConflictEnum.ENABLE, ConflictEnum.DISABLE]:
            sum_f = 0
            for rule_u in self.rules:
                sum_f += rule_u.action.get_total_risk()
            risk_score = sum_f / len(self.rules)
        penalty = risk_score * self.ranking
        weighted_penalty = penalty
        if self.possible == CONDITIONAL:
            weighted_penalty = 0.5 * penalty
        return penalty, weighted_penalty

    def __repr__(self):
        rules_str = [str(rule) for rule in self.rules]
        possible_s = "d" if self.possible == 1 else "c"
        penalty, weighted_penalty = self.calculate_penalty()
        return (
            f"EventConflictsClass(\n"
            f"rules={rules_str}, \n"
            f"interferences={self.get_interferences()}, \n"
            f"type={self.type} (C.{CONFLICTS_ID_D[self.type]}{possible_s}), \n"
            f"possible={self.possible}, \n"
            f"ranking={self.ranking}, \n"
            f"penalty={penalty:.2f}\n)"
        )

    def __str__(self):
        return repr(self)


class EventInterferenceClass:
    def __init__(self, tcas_l, relations_l, type_u):
        self.tcas = tcas_l
        self.logic = relations_l[0]
        self.temporal = relations_l[1]
        self.causal = relations_l[2]
        self.corefer = relations_l[3]
        self.type = type_u

    def __repr__(self):
        tcas_str = [str(tca_u) for tca_u in self.tcas]
        return (
            f"EventInterferenceClass("
            f"tcas={tcas_str}, "
            f"logic={self.logic}, "
            f"temporal={self.temporal}, "
            f"causal={self.causal}, "
            f"corefer={self.corefer}, "
            f"type={self.type})"
        )

    def __str__(self):
        return repr(self)


class EventRelationClass:
    def __init__(self, tcas_l, types_l):
        self.tcas = tcas_l
        self.type = types_l

    def __repr__(self):
        tcas_str = [str(tca_u) for tca_u in self.tcas]
        return f"EventRelationClass(" f"tcas={tcas_str}, " f"type={self.type})"

    def __str__(self):
        return repr(self)
