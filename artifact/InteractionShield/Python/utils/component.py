import json

from Python.utils.constant import (
    VALUE_NORMALIZE_D,
    DEVICE_CLUSTER_D,
    MEDIUM_RISK_SCORE_D,
    HIGH_RISK_SCORE_D,
    LOW,
    MEDIUM,
    HIGH,
    SAFETY,
    PRIVACY,
    CONVENIENCE,
    DEVICE_SPECIFIC_DEFAULTS_D
)
from Python.utils.enums import (
    MethodTypeEnum,
    TcaEnum,
)


class InputClass:
    """
    Inputs include name, type, title and section
    """

    def __init__(self, name_s: str, type_s: str, device_s: str):
        """
        Initialize name, type, title, section from the raw input


        Args:
            name_s (str): the name of the input

        """
        self.name: str = name_s
        self.type: str = type_s
        self.device: str = device_s


class MethodCallClass:
    """
    The detail of a Method Call node, include receiver, method, and arguments
    """

    def __init__(
        self,
        text_s: str,
        device_s: str,
        receiver_s: str,
        name_s: str,
        arguments_l: list,
        type_u: MethodTypeEnum,
    ):
        """
        Initialize the method call class


        Args:
            text_s (str):
            receiver_s (str):
            name_s (str):
            arguments_l (list):


        """
        self.text: str = text_s
        self.device: str = device_s
        self.receiver: str = receiver_s
        self.name: str = name_s
        self.arguments: list = arguments_l
        self.type: MethodTypeEnum = type_u


class TcaClass:
    def __init__(
        self,
        category_s: str,
        varname_s: str,
        device_s: str,
        attribute_s: str,
        operator_s: str,
        value_s: str,
        arguments_l: list,
        type_u: TcaEnum,
        appname_s: str,
        
    ):
        """
        : to be defined.
        """

        self.category = category_s.lower()
        self.varname = varname_s.lower()
        self.device = device_s.lower()
        self.attribute = attribute_s.lower()
        self.operator = operator_s.lower()
        self.value = value_s.lower()
        self.arguments = ", ".join(list(map(str.lower, arguments_l)))
        self.type = type_u
        self.appname = appname_s
        self.pos_x = 0
        self.pos_y = 0
        self.dev_params = DEVICE_SPECIFIC_DEFAULTS_D.get(self.device, {})
        self.rule_connects = set()
        self.chain_connects = set()
        self.action_risk = self.get_action_risk()

        self.conflicts_connects = set()
        self.chains_violations = set()
        self.action_violations = 0
    
    def update_parameters(self, app_params_l, dev_params_d):
        if not app_params_l:
            return
        self.device, self.pos_x, self.pos_y = app_params_l
        if dev_params_d:
            self.dev_params = dev_params_d
        self.action_risk = self.get_action_risk()

    def get_action_risk(self):
        cluster_s = DEVICE_CLUSTER_D.get(self.device, self.device)
        value_s = VALUE_NORMALIZE_D.get(self.value, self.value)
        high_cluster_l = HIGH_RISK_SCORE_D.get(cluster_s, {}).get(value_s, [])
        medium_cluster_l = MEDIUM_RISK_SCORE_D.get(cluster_s, {}).get(value_s, [])
        scores_d = {SAFETY: LOW, PRIVACY: LOW, CONVENIENCE: LOW}
        for category_s in high_cluster_l:
            scores_d[category_s] = HIGH
        for category_s in medium_cluster_l:
            scores_d[category_s] = MEDIUM
        score_i = max(scores_d.values())
        if SAFETY in self.category:
            score_i = scores_d[SAFETY]
        elif CONVENIENCE in self.category:
            score_i = scores_d[CONVENIENCE]
        return score_i

    def clear(self):
        self.conflicts_connects = set()
        self.chains_violations = set()
        self.action_violations = 0

    def add_conflicts(self, conflict_u):
        # add conflict with current tca
        self.conflicts_connects.add(conflict_u)

    def add_violations(self, chain_u):
        # add chain end with current tca
        self.chains_violations.add(chain_u)
        self.action_violations += 1
        # for conflict_u in self.conflicts_connects:
        #     conflict_u.calculate_penalty()

    def get_total_risk(self):
        return self.action_risk + self.action_violations

    def get_repr(self):
        repr_s = f"{self.device}"
        if self.operator != "==":
            repr_s += f"{self.operator}"
        else:
            repr_s += f"."
        if self.value != "":
            repr_s += f"{self.value}"
        return repr_s

    def __repr__(self):
        repr_s = f"{self.device}.{self.value}({self.arguments})"
        if self.operator != "==":
            repr_s = f"{self.device}{self.operator}{self.value}({self.arguments})"
        # repr_s += str(self.type.value)
        return repr_s

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        if self.appname != other.appname:
            return False
        if (self.type in [TcaEnum.SINK_MSG, TcaEnum.SINK_HTTP, TcaEnum.SINK_API]) and (
            other.type in [TcaEnum.SINK_MSG, TcaEnum.SINK_HTTP, TcaEnum.SINK_API]
        ):
            return True
        if self.type != other.type:
            return False
        return hash(self) == hash(other)

    def __lt__(self, other):
        if self.appname != other.appname:
            return self.appname < other.appname

        if (self.type in [TcaEnum.SINK_MSG, TcaEnum.SINK_HTTP, TcaEnum.SINK_API]) and (
            other.type in [TcaEnum.SINK_MSG, TcaEnum.SINK_HTTP, TcaEnum.SINK_API]
        ):
            return len(self.value + self.arguments) < len(other.value + other.arguments)

        if self.type != other.type:
            return self.type < other.type

        return (
            self.device + self.attribute + self.operator + self.value + self.arguments
        ) < (
            other.device
            + other.attribute
            + other.operator
            + other.value
            + other.arguments
        )

    def __le__(self, other) -> bool:
        return self < other or self == other

    def __hash__(self):
        hash_obj = hash(
            (
                self.device,
                self.attribute,
                self.operator,
                self.value,
                self.type,
                self.arguments,
                self.appname,
            )
        )
        if self.type in [TcaEnum.SINK_MSG, TcaEnum.SINK_HTTP, TcaEnum.SINK_API]:
            hash_obj = hash((self.device,))
        return hash_obj


class RuleClass:
    def __init__(
        self,
        category_s: str,
        trigger_u,
        conditions_l,
        action_u: TcaClass,
        appname_s: str,
    ):
        self.category = category_s
        self.triggers = self.get_combined_triggers(trigger_u, conditions_l)
        self.action = action_u
        self.appname = appname_s
        self.number = 1
        self.connections = {}
        self.update_rule_connect()
    
    def update_parameters(self, app_params_d, dev_params_d ):
        for trigger_u in self.triggers:
            trigger_u.update_parameters(app_params_d.get(trigger_u.varname, []), dev_params_d.get(trigger_u.varname, {}))
        self.action.update_parameters(app_params_d.get(self.action.varname, []), dev_params_d.get(self.action.varname, {}))

    def get_combined_triggers(self, trigger_u, condition_l):
        triggers_l = [trigger_u]
        triggers_l.extend(condition_l)
        triggers_l.sort()
        return triggers_l

    def update_rule_connect(self):
        for trigger_u in self.triggers:
            self.action.rule_connects.add(trigger_u)

    def add_number(self, number_i=1):
        self.number += number_i

    def __repr__(self):
        triggers_l = [repr(trigger_u) for trigger_u in self.triggers]
        triggers_s = "[Triggers: " + ", ".join(triggers_l) + "]"
        action_s = "Action: " + repr(self.action)

        return f"{self.appname} ## {triggers_s} -> {action_s}"

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        # return self.trigger == other.trigger and self.action == other.action
        return repr(self) == repr(other)
        # return (
        #     self.trigger == other.trigger
        #     and self.action == other.action
        # )

    def __lt__(self, other):
        return repr(self) < repr(other)
        # if self.action == other.action:
        #     if self.trigger < other.trigger:
        #         return True
        #     elif self.trigger > other.trigger:
        #         return False
        # return self.action < other.action

    def __le__(self, other) -> bool:
        # return self < other or self == other
        return repr(self) <= repr(other)

    def __hash__(self):
        return hash(repr(self))
        # hash_l = []
        # hash_l.append(hash(self.trigger))
        # hash_l.append(hash(self.action))
        # return hash(tuple(hash_l))

    def clear(self):
        self.connections = {}
        self.trigger.chain_connects = set()
        self.action.chain_connects = set()
        # self.risk = self.score


class ChainClass:
    def __init__(self, rule_ul, is_loop_b=False):
        self.rules = rule_ul
        self.is_loop = is_loop_b

    def __repr__(self):

        rules_str = [str(rule_u) for rule_u in self.rules]
        return f"ChainClass(" f"rules={rules_str}, " f"loop={self.is_loop})"

    def __str__(self):
        return repr(self)
