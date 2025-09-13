from enum import Enum


class AppTypeEnum(Enum):
    SMARTTHINGS = "SmartThings"
    IFTTT = "IFTTT"
    OPENHAB = "OpenHAB"

    def __repr__(self):
        return self.value

    def __str__(self):
        return repr(self)


class MethodTypeEnum(Enum):
    SUBSCRIBE = 0
    SCHEDULE = 1
    RUN = 2
    ACTUATOR = 3
    SINK_MSG = 4
    SINK_HTTP = 5
    SINK_API = 6
    OTHERS = 7


class TcaEnum(Enum):
    TRIGGER = 0
    CONDITION = 1
    ACTUATOR = 2
    SINK_MSG = 3
    SINK_HTTP = 4
    SINK_API = 5

    def __eq__(self, other) -> bool:
        return self.value == other.value

    def __lt__(self, other) -> bool:
        return self.value < other.value

    def __le__(self, other) -> bool:
        return self < other or self == other

    def __hash__(self) -> int:
        return hash(self.value)


class ConflictEnum(Enum):
    DUPLICATION = "Duplication Action"
    CONTRADICTORY = "Contradictory Action"
    ACCUMULATION = "Accumulation Impact"
    REDUCTION = "Reduction Impact"
    FORCE = "Force Action"
    BLOCK = "Block Action"
    DISORDER = "Disorder Action"
    ENABLE = "Chain Enable"
    LOOP = "Chain Loop"
    DISABLE = "Chain Disable"

    def __repr__(self):
        return self.value

    def __str__(self):
        return repr(self)


class TriggerInterEnum(Enum):
    TRIGGER_EQUAL = "Trigger Equal"
    TRIGGER_CONTAIN = "Trigger Contain"
    TRIGGER_INTERSECTION = "Trigger Intersection"
    TRIGGER_DISJOINT = "Trigger Disjoint"
    TRIGGER_UNIVERSAL = "Trigger Universal"
    TRIGGER_INDEPENDENT = "Trigger Independent"

    def __repr__(self):
        return self.value

    def __str__(self):
        return repr(self)


class ActionInterEnum(Enum):
    ACTION_EQUAL = "Action Equal"
    ACTION_MUTEX = "Action Mutex"
    ACTION_OPPOSITE = "Action Opposite"
    ACTION_ACCUMULATE = "Action Accumulate"
    ACTION_REDUCE = "Action Reduce"
    ACTION_FORCE = "Action Force"
    ACTION_BLOCK = "Action Block"
    ACTION_DISORDER = "Action Disorder"

    def __repr__(self):
        return self.value

    def __str__(self):
        return repr(self)


class ChainInterEnum(Enum):
    CYBER_ENABLE = "Cyber Enable"
    CYBER_DISABLE = "Cyber Disable"
    PHYSICAL_ENABLE = "Physical Enable"
    PHYSICAL_DISABLE = "Physical Disable"

    def __repr__(self):
        return self.value

    def __str__(self):
        return repr(self)


class LogicalRelEnum(Enum):
    LOGICAL_EQUAL = "Logical Equal"
    LOGICAL_CONTAIN = "Logical Contain"
    LOGICAL_INTERSECTION = "Logical Intersection"
    LOGICAL_DISJOINT = "Logical Disjoint"
    LOGICAL_UNIVERSAL = "Logical Universal"
    LOGICAL_INDEPENDENT = "Logical Independent"

    def __repr__(self):
        return self.value

    def __str__(self):
        return repr(self)


class TemporalRelEnum(Enum):
    TIME_PRECEDE = "Time Precede"
    TIME_MEET = "Time Meet"
    TIME_OVERLAP = "Time Overlap"
    TIME_CONTAIN = "Time Contain"
    TIME_START = "Time Start"
    TIME_FINISH = "Time Finish"
    TIME_EQUAL = "Time Equal"

    def __repr__(self):
        return self.value

    def __str__(self):
        return repr(self)


class CausalRelEnum(Enum):
    CAUSAL_CAUSE = "Causal Cause"
    CAUSAL_PRECONDITION = "Causal Precondition"

    def __repr__(self):
        return self.value

    def __str__(self):
        return repr(self)


class CoreferRelEnum(Enum):
    COREFER_SAME = "Corefer Same"
    COREFER_OPPOSITE = "Corefer Opposite"

    def __repr__(self):
        return self.value

    def __str__(self):
        return repr(self)
