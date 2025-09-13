import random
from collections import deque, defaultdict
from itertools import combinations, chain
from scipy.special import erfc
import numpy as np

from sympy import Interval, Intersection, Symbol, Union, S
from sympy.sets import EmptySet

from Python.utils.constant import (
    CHAIN_INTER_D,
    TRIGGER_INTER_D,
    ACTION_INTER_D,
    VALUE_NORMALIZE_D,
    CONFLICTS_D,
    CONFLICTS_L,
    CONFLICTS_INDEX_D,
    PHYSICAL_DEVICES_D,
    DEPENDENCY_DEPENDENT_D,
    DIFFERENT_TYPE_DEVICES_D,
    MEDIUM,
    LOW,
    ROOM_PARAMETERS_D,
)

from Python.utils.conflicts import (
    EventConflictsClass,
    EventInterferenceClass,
    EventRelationClass,
)

from Python.utils.component import ChainClass

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


class ConflictDetectorClass:
    def __init__(
        self,
        rules_l: list,
        properties_l: list = [],
        risk_level_i: int = MEDIUM,
        room_parameters_d: dict = ROOM_PARAMETERS_D,
    ):
        self.rules = rules_l
        self.properties = properties_l
        self.risk_level = risk_level_i
        self.room_parameters = room_parameters_d
        self.connections = defaultdict(set)
        self.pair_connections = {}
        self.action_trigger = {}
        self.action_rules = self.group_rules_by_action()
        self.conflicts = self.get_most_conflicts()

        self.interaction_graph = self.get_interaction_graph()

        self.get_other_conflicts()
        self.update_violations()

        self.penalty = self.get_conflicts_penalty()
        self.stats = self.get_conflicts_statistics()

    def clear(self):
        for conflict_u in self.conflicts:
            conflict_u.clear_actions()
        self.conflicts = []
        self.connections = defaultdict(set)
        self.pair_connections = {}
        self.action_trigger = {}
        self.action_rules = {}
        self.conflicts = []
        self.interaction_graph = []

    def group_rules_by_action(self):
        action_rules_d = defaultdict(list)

        for rule_u in self.rules:
            action_rules_d[rule_u.action].append(rule_u)

        return action_rules_d

    def update_violations(self):
        for property_l in self.properties:
            action_s, trigger_s = property_l

            trigger_dev_s, trigger_val_s = (
                trigger_s.split(".")[0],
                trigger_s.split(".")[1],
            )
            action_dev_s, action_val_s = action_s.split(".")[0], action_s.split(".")[1]

            for chain_u in self.interaction_graph:
                rules_l = chain_u.rules
                num_rules_i = len(rules_l)
                for i in range(num_rules_i):
                    rule1_u = rules_l[i]
                    for trigger1_u in rule1_u.triggers:
                        if (
                            trigger1_u.device != trigger_dev_s
                            or trigger1_u.value != trigger_val_s
                        ):
                            continue
                        action_index_l = range(i, num_rules_i)
                        if chain_u.is_loop:
                            action_index_l = chain(range(i, num_rules_i), range(i))
                        for j in action_index_l:
                            rule2_u = rules_l[j]
                            if (
                                rule2_u.action.device != action_dev_s
                                or rule2_u.action.value != action_val_s
                            ):
                                continue
                            violation_rules_l = rules_l[i : j + 1]
                            rule2_u.action.add_violations(
                                ChainClass(violation_rules_l, False)
                            )
                            return

    def get_interaction_graph(self):
        all_maximal_paths = []

        def is_subpath(path1, path2):
            if len(path1) >= len(path2):
                return False

            path1_str = "->".join(map(str, path1))
            path2_str = "->".join(map(str, path2))
            return path1_str in path2_str

        def dfs_maximal_path(start_node, current_node, path, visited_in_path, depth):
            if depth > 3:
                return

            maximal_extensions = []
            found_cycle = False

            for neighbor in self.connections.get(current_node, []):
                if neighbor == start_node:
                    cycle_path = path + [start_node]
                    all_maximal_paths.append(ChainClass(cycle_path, True))
                    found_cycle = True
                elif neighbor not in visited_in_path:
                    maximal_extensions.append(neighbor)

            if found_cycle:
                return

            if not maximal_extensions:
                all_maximal_paths.append(ChainClass(path, False))
                return

            for neighbor in maximal_extensions:
                dfs_maximal_path(
                    start_node,
                    neighbor,
                    path + [neighbor],
                    visited_in_path | {neighbor},
                    depth + 1, 
                )

        for start_node in self.connections:
            dfs_maximal_path(start_node, start_node, [start_node], {start_node}, 1)

        unique_paths = []
        seen_cycles = set()

        for path_info in all_maximal_paths:
            path = path_info.rules

            if path_info.is_loop:
                cycle_nodes = path[:-1]
                min_idx = cycle_nodes.index(min(cycle_nodes))
                normalized_cycle = tuple(cycle_nodes[min_idx:] + cycle_nodes[:min_idx])

                reverse_cycle = tuple(
                    [normalized_cycle[0]] + list(reversed(normalized_cycle[1:]))
                )

                if (
                    normalized_cycle not in seen_cycles
                    and reverse_cycle not in seen_cycles
                ):
                    seen_cycles.add(normalized_cycle)
                    complete_path = list(normalized_cycle)

                    unique_paths.append(ChainClass(complete_path, True))
            else:
                is_maximal = True
                for other_info in all_maximal_paths:
                    if other_info != path_info and not other_info.is_loop:
                        other_path = other_info.rules
                        if is_subpath(path, other_path):
                            is_maximal = False
                            break

                if is_maximal:
                    if not any(existing.rules == path for existing in unique_paths):
                        unique_paths.append(path_info)

        return unique_paths

    def get_most_conflicts(self):
        conflicts_l = []
        num_rules_i = len(self.rules)
        for i in range(num_rules_i):
            for j in range(i + 1, num_rules_i):
                rule1_u = self.rules[i]
                rule2_u = self.rules[j]
                each_conflicts_l = self.get_rule_conflicts([rule1_u, rule2_u])
                for conflicts_u in each_conflicts_l:
                    if rule1_u.appname == rule2_u.appname:
                        if conflicts_u.type in [ConflictEnum.LOOP]:
                            conflicts_l.append(conflicts_u)
                    else:
                        conflicts_l.append(conflicts_u)
        return conflicts_l

    def get_other_conflicts(self):
        for action_u, rules_l in self.action_rules.items():
            if len(rules_l) <= 2:
                continue
            conflicts_ul = self.get_duplicate_conflicts(rules_l)
            for conflict_u in conflicts_ul:
                if conflicts_u is not None:
                    self.conflicts.append(conflicts_u)
        for chain_u in self.interaction_graph:
            if chain_u.is_loop:
                conflicts_u = self.get_loop_conflicts(chain_u)
                if conflicts_u is not None:
                    self.conflicts.append(conflicts_u)

    def get_loop_conflicts(self, chain_u):

        num_rules_i = len(chain_u.rules)
        triggers_l, connects_l = [], []
        num_connects_i, num_deter_i = 0, 0
        for i in range(num_rules_i - 1):
            num_connects_i += 1

            rule1_u, rule2_u = chain_u.rules[i], chain_u.rules[i + 1]
            at_inter_u = self.action_trigger.get((rule1_u, rule2_u), None)
            connects_l.append(at_inter_u)
            inter_u = self.pair_connections.get(
                (rule1_u, rule2_u), [None, None, None, None]
            )
            if (inter_u[0] is not None) or (
                (inter_u[-1] is not None)
                and (inter_u[-1].type == ChainInterEnum.PHYSICAL_ENABLE)
            ):
                num_deter_i += 1
                triggers_l.append(inter_u[0])
            else:
                triggers_l.append(inter_u[1])

        if num_connects_i == num_deter_i:
            return EventConflictsClass(
                chain_u.rules,
                (
                    triggers_l,
                    None,
                    None,
                    connects_l,
                ),
                ConflictEnum.LOOP,
            )

        return EventConflictsClass(
            chain_u.rules,
            (
                None,
                triggers_l,
                None,
                connects_l,
            ),
            ConflictEnum.LOOP,
        )

    def get_conflicts_penalty(self):
        penalty_f = 0
        for conflict_u in self.conflicts:
            orig_penalty_f, weighted_penalty_f = conflict_u.calculate_penalty()
            penalty_f += weighted_penalty_f
        return penalty_f

    def get_duplicate_conflicts(self, rules_l):

        def convert_to_number(value_s):
            try:
                return float(value_s)
            except:
                return value_s

        def generate_relation_pairs(x, y, low=-1000, high=1000):
            def satisfies(a, b, rel):
                if rel == "<":
                    return a < b
                if rel == ">":
                    return a > b
                return a == b

            result = []

            is_x_str = isinstance(x, str)
            is_y_str = isinstance(y, str)

            if not is_x_str and not is_y_str:
                return [(x, y)]

            elif is_x_str ^ is_y_str:
                known = y if not is_y_str else x
                unknown_is_x = is_x_str
                for rel in ["<", "==", ">"]:
                    while True:
                        val = random.randint(low, high)
                        if unknown_is_x and satisfies(val, known, rel):
                            result.append((val, known))
                            break
                        elif not unknown_is_x and satisfies(known, val, rel):
                            result.append((known, val))
                            break

            elif is_x_str and is_y_str:
                for rel in ["<", "==", ">"]:
                    while True:
                        a = random.randint(low, high)
                        b = random.randint(low, high)
                        if satisfies(a, b, rel):
                            result.append((a, b))
                            break

            return result

        def parse_condition(op, val):

            if op == ">":
                return Interval.open(val, float("inf"))
            elif op == ">=":
                return Interval(val, float("inf"))
            elif op == "<":
                return Interval.open(float("-inf"), val)
            elif op == "<=":
                return Interval(float("-inf"), val)
            return Interval(val, val)

        def check_universal(triggers_l):
            types_l = [tca_u.type for tca_u in triggers_l]
            if len(set(types_l)) != 1:
                return False
            devices_l = [tca_u.device for tca_u in triggers_l]
            if len(set(devices_l)) != 1:
                return False

            values_fl = [
                convert_to_number(VALUE_NORMALIZE_D.get(tca_u.value, tca_u.value))
                for tca_u in triggers_l
            ]
            if not all(isinstance(v, (int, float)) for v in values_fl):
                return False
            intervals_l = [
                parse_condition(tca_u.operator, values_f)
                for tca_u, values_f in zip(triggers_l, values_fl)
            ]
            result_u = Union(*intervals_l)
            return result_u == S.Reals

        num_rules_i = len(rules_l)
        univeral_duplicate_l = []
        if num_rules_i <= 2:
            return univeral_duplicate_l

        devices_tcas_d = defaultdict(list)
        tcas_rules_d = {}
        for rule_u in rules_l:
            for trigger_u in rule_u.triggers:
                devices_tcas_d[trigger_u.device].append(trigger_u)
                tcas_rules_d[trigger_u] = rule_u

        for device_s, triggers_l in devices_tcas_d.items():
            if len(triggers_l) <= 2:
                continue
            num_triggers_i = len(triggers_l)
            for n_i in range(num_triggers_i, 2, -1):
                n_level_i = 0
                for triggers_comb_l in combinations(triggers_l, n_i):
                    is_universal_b = check_universal(triggers_comb_l)
                    rules_comb_l = [
                        tcas_rules_d[trigger_u] for trig_u in triggers_comb_l
                    ]
                    actions_comb_l = [rule_u.action for rule_u in rules_comb_l]
                    if is_universal_b:
                        n_level_i += 1
                        univeral_duplicate_l.append(
                            EventConflictsClass(
                                rules_comb_l,
                                (
                                    EventInterferenceClass(
                                        triggers_comb_l,
                                        [],
                                        TriggerInterEnum.TRIGGER_UNIVERSAL,
                                    ),
                                    None,
                                    None,
                                    EventInterferenceClass(
                                        actions_comb_l, [], ActionInterEnum.ACTION_EQUAL
                                    ),
                                ),
                                ConflictEnum.DUPLICATION,
                            )
                        )
                if n_level_i == 0:
                    break

        return univeral_duplicate_l

    def is_physical_connect(self, tca1_u, tca2_u, channel_s):
        def temperature_diffusion(x, t=1800, T0=70, Ts=150, alpha=2.2e-5):
            """T(x,t) = T0 + (Ts - T0) * erfc( x / (2*sqrt(alpha*t)) )"""

            TsK = (Ts + 459.67) * 5 / 9
            T0K = (T0 + 459.67) * 5 / 9
            t = max(t, 1e-12)
            z = x / (2.0 * np.sqrt(alpha * t))
            return T0K + (TsK - T0K) * erfc(z)

        def temperature_hvac(t=1800, q=1, T0=70, Td=0.6):
            """dT/dt = T_delta * q  =>  T(t) = T0 + (T_delta*q)*t"""
            T0K = (T0 + 459.67) * 5 / 9
            TdK = (T0 + 459.67) * 5 / 9
            return T0K + (Tdk * q) * t

        def rh_percent(w_gm3, T_F=70):
            """
            Relative humidity in percent: RH% = 100 * w / ws(T)

            - w_gm3  : g/m^3 (actual water vapor concentration)
            - ws(T)  : g/m^3 (from ws_from_temperature_F)

            w_gm3 : float, Actual water vapor concentration [g/m^3]

            RH : float, Relative humidity in [%], clipped to [0, 100]
            """
            ws = 2.6055 * np.exp(0.0262 * T_F)  # g/m^3
            RH = 100.0 * w_gm3 / np.maximum(ws, 1e-12)
            return np.clip(RH, 0.0, 100.0)

        def integrate_water_content(v_m3, q=1, t=1800, w0_gm3=11.9, g_min=10):
            """
            Integrate water vapor content (well-mixed room) using mass rate in g/min:
                w(t) = w0 + ( (g_min / 60) / V ) * q * t

            Units:
            - w0_gm3        : g/m^3 (initial)
            - g_min         : g/min  (humidifier/dehumidifier output; use negative for dehumidify)
            - v_m3     : m^3
            - t             : s
            - q             : actuation (e.g., 1=on, 0=off; or any scalar multiplier)

            Returns
            -------
            w_t : float
                Water vapor concentration at time t [g/m^3]
            """
            g_s = g_min / 60.0  # g/s
            k_w = g_s / v_m3  # g/m^3 per s
            return w0_gm3 + k_w * q * t

        def smoke_concentration(
            v_m3, q, t=1800, S0_ODpm=0, mg_min=40, lam=3e-3, mgm3_to_OD=0.02 / 13.0
        ):
            """
            Smoke concentration S(t) in OD/m with a mass source (mg/min) and clearance:
                dS/dt = k_s*q - lam*S
                S(t)  = S0*exp(-lam*t) + (k_s*q/lam)*(1 - exp(-lam*t))

            Convert mass rate to OD/m/s via room volume and a mg/m^3 → OD/m factor:
                mg_s = mg_min / 60
                rate_mgm3_s    = mg_s / V           [mg/m^3/s]
                k_s            = rate_mgm3_s * mgm3_to_OD     [OD/m/s]
            (Empirical: 0.02 OD/m ≈ 13 mg/m^3  → mgm3_to_OD = 0.02/13)

            t : float, Time [s]
            S0_ODpm : float, Initial smoke concentration [OD/m]
            mg_min : float, Smoke mass generation rate [mg/min]
            v_m3 : float, Room volume [m^3]
            q : float, Actuation (0=off, 1=on, or any scalar intensity)
            lam : float, Clearance rate [1/s]
            mgm3_to_OD : float, default 0.02/13, Conversion factor from mg/m^3 to OD/m

            S_t : float, Smoke concentration at time t [OD/m]
            """
            mg_s = mg_min / 60.0  # mg/s
            rate_mgm3_s = mg_s / v_m3  # mg/m^3/s
            k_s = rate_mgm3_s * mgm3_to_OD  # OD/m/s

            expf = np.exp(-lam * t)
            return S0_ODpm * expf + (k_s * q) / lam * (1.0 - expf)

        def illuminance_inverse_square(x, Is=815):
            """Ix = Is / (4*pi*x^2)"""
            x = max(float(x), 1e-12)
            return Is / (4.0 * np.pi * x**2)

        def sound_spl_at_distance(x2, x1=1, SPL1_dB=65):
            """SPL2 = SPL1 + 20*log10(x1/x2)"""
            x1 = max(float(x1), 1e-12)
            x2 = max(float(x2), 1e-12)
            return SPL1_dB + 20.0 * np.log10(x1 / x2)

        def pir_motion_detected(distance, R=1):
            return distance <= R

        def power_overload(power_input, rated_power=3000):
            return power_input > rated_power

        def is_temperature_diffusion_detected(
            x, t=1800, T0=70, Ts=150, alpha=2.2e-5, threshold_f=1.8
        ):
            Tdiff = temperature_diffusion(x, t, T0, Ts, alpha) - T0
            return abs(Tdiff) >= threshold_f

        def is_temperature_hvac_detected(t=1800, q=1, T0=70, Td=0.6, threshold_f=1.8):
            Tdiff = temperature_hvac(t, q, T0, Td) - T0
            return abs(Tdiff) >= threshold_f

        def is_humidity_change_detected(
            v_m3, q=1.0, t=1800, w0_gm3=11.9, g_min=10, T_F=70, threshold_pct=2.0
        ):
            RH0 = rh_percent(w0_gm3, T_F)
            w_t = integrate_water_content(v_m3, q, t, w0_gm3, g_min)
            RHt = rh_percent(w_t, T_F)
            dRH = RHt - RH0
            return abs(dRH) >= threshold_pct

        def is_smoke_detected(
            v_m3,
            q=1.0,
            t=1800,
            S0_ODpm=0,
            mg_min=40,
            lam=3e-3,
            mgm3_to_OD=0.02 / 13.0,
            threshold_mgm3=13.0,
        ):
            S_OD = smoke_concentration(v_m3, q, t, S0_ODpm, mg_min, lam, mgm3_to_OD)
            conc_mgm3 = S_OD / mgm3_to_OD
            return conc_mgm3 >= threshold_mgm3

        def is_illuminance_inverse_square_detected(x, Is=815, threshold_lux=50):
            return illuminance_inverse_square(x, Is) >= threshold_lux

        def is_sound_spl_at_distance_detected(x2, x1, SPL1_dB=65, threshold_dB=55):
            return sound_spl_at_distance(x2, x1, SPL1_dB) > threshold_dB

        def is_pir_motion_detected(distance, R=1):
            return pir_motion_detected(distance, R)

        def is_power_overload_detected(power_input, rated_power=3000):
            return power_overload(power_input, rated_power)

        device1, x1, y1 = tca1_u.device, tca1_u.pos_x, tca1_u.pos_y
        device2, x2, y2 = tca2_u.device, tca2_u.pos_x, tca2_u.pos_y
        d = np.hypot(x1 - x2, y1 - y2)
        length = self.room_parameters.get("length", 5)
        width = self.room_parameters.get("width", 4)
        height = self.room_parameters.get("height", 3)
        t = self.room_parameters.get("time", 1800) * 60
        T0 = self.room_parameters.get("temperature", 70)
        w0_gm3 = self.room_parameters.get("humidity", 50)
        S0_ODpm = self.room_parameters.get("smoke", 0)
        rated_power = self.room_parameters.get("power", 3000)
        v_m3 = length * width * height
        value1_s = VALUE_NORMALIZE_D.get(tca1_u.value, tca1_u.value)
        q = 1 if value1_s == "on" else 0

        if channel_s == "Temperature":
            Ts = tca1_u.dev_params.get("source_temperature", 150)
            if Ts is not None:
                return is_temperature_diffusion_detected(d, t, T0, Ts)
            Td = tca1_u.dev_params.get("temperature_delta", 0.6)
            if Td is not None:
                return is_temperature_hvac_detected(t, q, T0, Td)
            return True

        if channel_s == "Humidity":
            g_min = tca1_u.dev_params.get("water_vapor", 10)
            return is_humidity_change_detected(v_m3, q, t, w0_gm3, g_min, T0)

        if channel_s == "Smoke":
            mg_min = tca1_u.dev_params.get("smoke_generate", 40)
            lam = tca1_u.dev_params.get("smoke_clearance", 3e-3)
            return is_smoke_detected(v_m3, q, t, S0_ODpm, mg_min, lam)

        if channel_s == "Illuminance":
            Is = tca1_u.dev_params.get("illuminance", 815)
            if value1_s == "off":
                return False
            return is_illuminance_inverse_square_detected(d, Is)

        if channel_s == "Sound":
            SPL1_dB = tca1_u.dev_params.get("sound_level", 60)
            if value1_s == "off":
                return False
            return is_sound_spl_at_distance_detected(d, 1, SPL1_dB)

        if channel_s == "Motion":
            if value1_s == "off":
                return False
            return is_pir_motion_detected(d)

        if channel_s == "Power":
            power_input = tca1_u.dev_params.get("power", 3000)
            if value1_s == "off":
                return False
            return is_power_overload_detected(power_input)
        return True

    def get_rule_conflicts(self, rules_l):
        rule_conflicts_l = []

        size_i = len(rules_l)

        def get_trigger_interferences(rule1_u, rule2_u):
            teci_l, tu_l, td_l, tp_l = [], [], [], []
            for trigger1_u in rule1_u.triggers:
                for trigger2_u in rule2_u.triggers:
                    each_tt_inter_l = self.get_pair_interference(trigger1_u, trigger2_u)
                    for each_tt_inter_u in each_tt_inter_l:
                        if each_tt_inter_u.type in [
                            TriggerInterEnum.TRIGGER_EQUAL,
                            TriggerInterEnum.TRIGGER_CONTAIN,
                            TriggerInterEnum.TRIGGER_INTERSECTION,
                        ]:
                            teci_l.append(each_tt_inter_u)
                        elif each_tt_inter_u.type in [
                            TriggerInterEnum.TRIGGER_UNIVERSAL
                        ]:
                            tu_l.append(each_tt_inter_u)
                        elif each_tt_inter_u.type in [
                            TriggerInterEnum.TRIGGER_DISJOINT
                        ]:
                            td_l.append(each_tt_inter_u)
                        else:
                            tp_l.append(each_tt_inter_u)

            return teci_l, tu_l, td_l, tp_l

        def get_deter_cond_infer(tt_inters_l, trigger_infer_l):
            num_inters_l = len(tt_inters_l)
            for i in range(num_inters_l):
                tt_inter_l = tt_inters_l[i]
                for tt_inter_u in tt_inter_l:
                    if tt_inter_u.type in trigger_infer_l:
                        return tt_inter_u
            return None

        rule1_u, rule2_u = rules_l

        tt_inters_l = get_trigger_interferences(rule1_u, rule2_u)
        at_inters_l = []
        ta_inters_l = []
        aa_inters_l = []

        for trigger2_u in rule2_u.triggers:
            at_inters_l.extend(self.get_pair_interference(rule1_u.action, trigger2_u))
        for trigger1_u in rule1_u.triggers:
            ta_inters_l.extend(self.get_pair_interference(rule2_u.action, trigger1_u))
        aa_inters_l.extend(self.get_pair_interference(rule1_u.action, rule2_u.action))

        infers_l = []

        for conflict_u, interference_l in CONFLICTS_D.items():
            if conflict_u in [ConflictEnum.LOOP]:
                continue
            trigger_deter_infer_l = interference_l[0]
            trigger_cond_infer_l = interference_l[1]
            action_infer_l = interference_l[2]
            chain_infer_l = interference_l[3]

            for aa_inter in aa_inters_l:
                if (aa_inter is not None) and (aa_inter.type in action_infer_l):
                    infer_t = None
                    tt_inter_u = get_deter_cond_infer(
                        tt_inters_l, trigger_deter_infer_l
                    )
                    if tt_inter_u is not None:
                        infer_t = (tt_inter_u, None, aa_inter, None)
                    else:
                        tt_inter_u = get_deter_cond_infer(
                            tt_inters_l, trigger_cond_infer_l
                        )
                        if tt_inter_u is not None:
                            infer_t = (None, tt_inter_u, aa_inter, None)
                    if infer_t is not None:
                        rule_conflicts_l.append(
                            EventConflictsClass(rules_l, infer_t, conflict_u)
                        )

            action_risk = rule2_u.action.action_risk
            for at_inter in at_inters_l:
                if (at_inter is not None) and (at_inter.type in chain_infer_l):
                    if at_inter.type in [
                        ChainInterEnum.CYBER_ENABLE,
                        ChainInterEnum.PHYSICAL_ENABLE,
                    ]:
                        self.connections[rule1_u].add(rule2_u)
                        self.action_trigger[(rule1_u, rule2_u)] = at_inter

                    infer_t = None
                    tt_inter_u = get_deter_cond_infer(
                        tt_inters_l, trigger_deter_infer_l
                    )
                    if (
                        at_inter.type == ChainInterEnum.PHYSICAL_ENABLE
                        or tt_inter_u is not None
                    ):
                        infer_t = (tt_inter_u, None, None, at_inter)
                    else:
                        tt_inter_u = get_deter_cond_infer(
                            tt_inters_l, trigger_cond_infer_l
                        )
                        if tt_inter_u is not None:
                            infer_t = (None, tt_inter_u, None, at_inter)
                    if infer_t is not None:
                        self.pair_connections[(rule1_u, rule2_u)] = infer_t
                        if action_risk >= self.risk_level:
                            rule_conflicts_l.append(
                                EventConflictsClass(rules_l, infer_t, conflict_u)
                            )

            action_risk = rule1_u.action.action_risk
            for ta_inter in ta_inters_l:
                if (ta_inter is not None) and (ta_inter.type in chain_infer_l):
                    if ta_inter.type in [
                        ChainInterEnum.CYBER_ENABLE,
                        ChainInterEnum.PHYSICAL_ENABLE,
                    ]:
                        self.connections[rule2_u].add(rule1_u)
                        self.action_trigger[(rule2_u, rule1_u)] = ta_inter

                    infer_t = None
                    tt_inter_u = get_deter_cond_infer(
                        tt_inters_l, trigger_deter_infer_l
                    )
                    if (
                        ta_inter.type == ChainInterEnum.PHYSICAL_ENABLE
                        or tt_inter_u is not None
                    ):
                        infer_t = (tt_inter_u, None, None, ta_inter)
                    else:
                        tt_inter_u = get_deter_cond_infer(
                            tt_inters_l, trigger_cond_infer_l
                        )
                        if tt_inter_u is not None:
                            infer_t = (None, tt_inter_u, None, ta_inter)
                    if infer_t is not None:
                        self.pair_connections[(rule2_u, rule1_u)] = infer_t
                        if action_risk >= self.risk_level:
                            rule_conflicts_l.append(
                                EventConflictsClass(rules_l[::-1], infer_t, conflict_u)
                            )
        return rule_conflicts_l

    def get_pair_interference(self, tca1_u, tca2_u):
        inters_l = []

        pair_relation_l = self.get_event_relation(tca1_u, tca2_u)

        interference_d = CHAIN_INTER_D
        if (tca1_u.type, tca2_u.type) == (TcaEnum.TRIGGER, TcaEnum.TRIGGER):
            interference_d = TRIGGER_INTER_D
        elif (tca1_u.type, tca2_u.type) == (TcaEnum.ACTUATOR, TcaEnum.ACTUATOR):
            interference_d = ACTION_INTER_D

        pair_rels_l = [item.type for item in pair_relation_l]

        def is_valid(base, cand):
            for a, b in zip(base, cand):
                if a:
                    if (not b) or (not set(a) & set(b)):
                        return False
                else:
                    if b:
                        return False
            return True

        for inter_u, relations_l in interference_d.items():
            if is_valid(pair_rels_l, relations_l):
                inters_l.append(
                    EventInterferenceClass([tca1_u, tca2_u], pair_relation_l, inter_u)
                )

        return inters_l

    def get_event_relation(self, tca1_u, tca2_u):

        def convert_to_number(value_s):
            try:
                return float(value_s)
            except:
                return value_s

        def generate_relation_pairs(x, y, low=-1000, high=1000):
            def satisfies(a, b, rel):
                if rel == "<":
                    return a < b
                if rel == ">":
                    return a > b
                return a == b

            result = []

            is_x_str = isinstance(x, str)
            is_y_str = isinstance(y, str)

            if not is_x_str and not is_y_str:
                return [(x, y)]

            elif is_x_str ^ is_y_str:
                known = y if not is_y_str else x
                unknown_is_x = is_x_str
                for rel in ["<", "==", ">"]:
                    while True:
                        val = random.randint(low, high)
                        if unknown_is_x and satisfies(val, known, rel):
                            result.append((val, known))
                            break
                        elif not unknown_is_x and satisfies(known, val, rel):
                            result.append((known, val))
                            break

            elif is_x_str and is_y_str:
                for rel in ["<", "==", ">"]:
                    while True:
                        a = random.randint(low, high)
                        b = random.randint(low, high)
                        if satisfies(a, b, rel):
                            result.append((a, b))
                            break

            return result

        def parse_condition(op, val):

            if op == ">":
                return Interval.open(val, float("inf"))
            elif op == ">=":
                return Interval(val, float("inf"))
            elif op == "<":
                return Interval.open(float("-inf"), val)
            elif op == "<=":
                return Interval(float("-inf"), val)
            return Interval(val, val)

        def get_logical_relation(tca1_u, tca2_u):

            result_e = set()
            if tca1_u.device != tca2_u.device:
                result_e.add(LogicalRelEnum.LOGICAL_INDEPENDENT)
                return EventRelationClass([tca1_u, tca2_u], result_e)

            value1_s = VALUE_NORMALIZE_D.get(tca1_u.value, tca1_u.value)
            value2_s = VALUE_NORMALIZE_D.get(tca2_u.value, tca2_u.value)

            value1_f = convert_to_number(value1_s)
            value2_f = convert_to_number(value2_s)

            if tca1_u.operator == tca2_u.operator and tca1_u.operator == "==":
                if isinstance(value1_f, str) and isinstance(value2_f, str):
                    if value1_f == value2_f:
                        result_e.add(LogicalRelEnum.LOGICAL_EQUAL)
                    elif value1_f in ["on", "off"]:
                        result_e.add(LogicalRelEnum.LOGICAL_UNIVERSAL)
                    else:
                        result_e.add(LogicalRelEnum.LOGICAL_DISJOINT)
                return EventRelationClass([tca1_u, tca2_u], result_e)

            number_pairs_l = generate_relation_pairs(value1_f, value2_f)
            for value1_f, value2_f in number_pairs_l:

                interval1 = parse_condition(tca1_u.operator, value1_f)
                interval2 = parse_condition(tca2_u.operator, value2_f)
                inter = Intersection(interval1, interval2)

                if inter == EmptySet:
                    result_e.add(LogicalRelEnum.LOGICAL_DISJOINT)
                elif interval1 == interval2:
                    result_e.add(LogicalRelEnum.LOGICAL_EQUAL)
                elif interval1.is_subset(interval2) or interval1.is_superset(interval2):
                    result_e.add(LogicalRelEnum.LOGICAL_CONTAIN)
                else:
                    result_e.add(LogicalRelEnum.LOGICAL_INTERSECTION)
            return EventRelationClass([tca1_u, tca2_u], result_e)

        def get_temporal_relation(tca1_u, tca2_u):
            result_e = set()

            if tca1_u.type == tca2_u.type:
                result_e.update(
                    [
                        TemporalRelEnum.TIME_PRECEDE,
                        TemporalRelEnum.TIME_MEET,
                        TemporalRelEnum.TIME_OVERLAP,
                        TemporalRelEnum.TIME_CONTAIN,
                        TemporalRelEnum.TIME_START,
                        TemporalRelEnum.TIME_FINISH,
                        TemporalRelEnum.TIME_EQUAL,
                    ]
                )
            return EventRelationClass([tca1_u, tca2_u], result_e)

        def get_causal_relation(tca1_u, tca2_u):
            is_physical = self.room_parameters.get("physical", False)
            result_e = set()

            if tca1_u.type == TcaEnum.TRIGGER and tca2_u.type == TcaEnum.TRIGGER:
                return EventRelationClass([tca1_u, tca2_u], result_e)

            if tca1_u.device == tca2_u.device:
                if (tca1_u.type == TcaEnum.ACTUATOR) and (
                    tca2_u.type == TcaEnum.TRIGGER
                ):
                    result_e.add(CausalRelEnum.CAUSAL_CAUSE)
                if (tca1_u.type == TcaEnum.TRIGGER) and (
                    tca2_u.type == TcaEnum.ACTUATOR
                ):
                    result_e.add(CausalRelEnum.CAUSAL_CAUSE)

            if tca1_u.type == TcaEnum.ACTUATOR and tca2_u.type == TcaEnum.TRIGGER:
                for channel_s, devices_l in PHYSICAL_DEVICES_D.items():
                    if (tca1_u.device in devices_l[0]) and (
                        tca2_u.device in devices_l[1]
                    ):
                        if (not is_physical) or (
                            is_physical
                            and self.is_physical_connect(tca1_u, tca2_u, channel_s)
                        ):
                            result_e.add(CausalRelEnum.CAUSAL_CAUSE)
            if tca1_u.type == TcaEnum.TRIGGER and tca2_u.type == TcaEnum.ACTUATOR:
                for channel_s, devices_l in PHYSICAL_DEVICES_D.items():
                    if (tca1_u.device in devices_l[1]) and (
                        tca2_u.device in devices_l[0]
                    ):
                        if (not is_physical) or (
                            is_physical
                            and self.is_physical_connect(tca2_u, tca1_u, channel_s)
                        ):
                            result_e.add(CausalRelEnum.CAUSAL_CAUSE)

            if tca1_u.type == TcaEnum.ACTUATOR and tca2_u.type == TcaEnum.ACTUATOR:
                for channel_s, devices_l in DEPENDENCY_DEPENDENT_D.items():
                    if (tca1_u.device in devices_l[0]) and (
                        tca2_u.device in devices_l[1]
                    ):
                        result_e.add(CausalRelEnum.CAUSAL_PRECONDITION)
                    elif (tca2_u.device in devices_l[0]) and (
                        tca1_u.device in devices_l[1]
                    ):
                        result_e.add(CausalRelEnum.CAUSAL_PRECONDITION)

            return EventRelationClass([tca1_u, tca2_u], result_e)

        def get_corefer_relation(tca1_u, tca2_u):
            def get_device_index(tca_u, devices_l):
                for i in range(len(devices_l)):
                    if tca_u.device in devices_l[i]:
                        return i
                return -1

            result_e = set()

            if tca1_u.type == TcaEnum.TRIGGER and tca2_u.type == TcaEnum.TRIGGER:
                return EventRelationClass([tca1_u, tca2_u], result_e)

            if tca1_u.device == tca2_u.device:
                return EventRelationClass([tca1_u, tca2_u], result_e)

            # if not (tca1_u.operator == tca2_u.operator and tca1_u.operator == "=="):
            #     return EventRelationClass([tca1_u, tca2_u], result_e)

            value1_s = VALUE_NORMALIZE_D.get(tca1_u.value, tca1_u.value)
            value2_s = VALUE_NORMALIZE_D.get(tca2_u.value, tca2_u.value)

            if tca1_u.operator == "==" and tca2_u.operator != "==":
                channel_s = tca2_u.device.capitalize()
                devices_l = DIFFERENT_TYPE_DEVICES_D.get(channel_s, [[], [], []])
                if tca1_u.device in devices_l[0]:
                    if value1_s == "on" and tca2_u.operator in [">", ">="]:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    elif value1_s == "off" and tca2_u.operator in ["<", "<="]:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    else:
                        result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                elif tca1_u.device in devices_l[1]:
                    if value1_s == "off" and tca2_u.operator in [">", ">="]:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    elif value1_s == "on" and tca2_u.operator in ["<", "<="]:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    else:
                        result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                elif tca1_u.device in devices_l[2]:
                    if "heat" in value1_s:
                        if tca2_u.operator in [">", ">="]:
                            result_e.add(CoreferRelEnum.COREFER_SAME)
                        elif tca2_u.operator in ["<", "<="]:
                            result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                    elif "cool" in value1_s:
                        if tca2_u.operator in [">", ">="]:
                            result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                        elif tca2_u.operator in ["<", "<="]:
                            result_e.add(CoreferRelEnum.COREFER_SAME)
                    elif "mode" in value1_s:
                        result_e.update(
                            [
                                CoreferRelEnum.COREFER_SAME,
                                CoreferRelEnum.COREFER_OPPOSITE,
                            ]
                        )
                    elif "on" in value1_s:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    elif "off" in value1_s:
                        result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                return EventRelationClass([tca1_u, tca2_u], result_e)

            if tca1_u.operator != "==" and tca2_u.operator == "==":
                channel_s = tca1_u.device.capitalize()
                devices_l = DIFFERENT_TYPE_DEVICES_D.get(channel_s, [[], [], []])
                if tca2_u.device in devices_l[0]:
                    if value2_s == "on" and tca1_u.operator in [">", ">="]:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    elif value2_s == "off" and tca1_u.operator in ["<", "<="]:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    else:
                        result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                elif tca2_u.device in devices_l[1]:
                    if value2_s == "off" and tca1_u.operator in [">", ">="]:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    elif value2_s == "on" and tca1_u.operator in ["<", "<="]:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    else:
                        result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                elif tca2_u.device in devices_l[2]:
                    if "heat" in value2_s:
                        if tca1_u.operator in [">", ">="]:
                            result_e.add(CoreferRelEnum.COREFER_SAME)
                        elif tca1_u.operator in ["<", "<="]:
                            result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                    elif "cool" in value2_s:
                        if tca1_u.operator in [">", ">="]:
                            result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                        elif tca1_u.operator in ["<", "<="]:
                            result_e.add(CoreferRelEnum.COREFER_SAME)
                    elif "mode" in value2_s:
                        result_e.update(
                            [
                                CoreferRelEnum.COREFER_SAME,
                                CoreferRelEnum.COREFER_OPPOSITE,
                            ]
                        )
                    elif "on" in value2_s:
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    elif "off" in value2_s:
                        result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                return EventRelationClass([tca2_u, tca1_u], result_e)

            is_value1_str = isinstance(value1_s, str)
            is_value2_str = isinstance(value2_s, str)

            if not (is_value1_str and is_value2_str):
                return EventRelationClass([tca1_u, tca2_u], result_e)

            if value2_s == "on":
                for channel_s, devices_l in DEPENDENCY_DEPENDENT_D.items():
                    if (tca1_u.device in devices_l[0]) and (
                        tca2_u.device in devices_l[1]
                    ):
                        if value1_s == "on":
                            result_e.add(CoreferRelEnum.COREFER_SAME)
                        elif value1_s == "off":
                            result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
            if value1_s == "on":
                for channel_s, devices_l in DEPENDENCY_DEPENDENT_D.items():
                    if (tca1_u.device in devices_l[1]) and (
                        tca2_u.device in devices_l[0]
                    ):
                        if value2_s == "on":
                            result_e.add(CoreferRelEnum.COREFER_SAME)
                        elif value2_s == "off":
                            result_e.add(CoreferRelEnum.COREFER_OPPOSITE)

            for channel_s, devices_l in DIFFERENT_TYPE_DEVICES_D.items():
                device_idx1_i = get_device_index(tca1_u, devices_l)
                device_idx2_i = get_device_index(tca2_u, devices_l)
                if device_idx1_i == -1 or device_idx2_i == -1:
                    continue
                if (device_idx1_i, device_idx2_i) in [(0, 0), (1, 1)]:
                    if (value1_s == "on" and value2_s == "off") or (
                        value1_s == "off" and value2_s == "on"
                    ):
                        result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                    elif (value1_s == "on" and value2_s == "on") or (
                        value1_s == "off" and value2_s == "of"
                    ):
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                elif (device_idx1_i, device_idx2_i) in [(0, 1), (1, 0)]:
                    if (value1_s == "on" and value2_s == "off") or (
                        value1_s == "off" and value2_s == "on"
                    ):
                        result_e.add(CoreferRelEnum.COREFER_SAME)
                    elif (value1_s == "on" and value2_s == "on") or (
                        value1_s == "off" and value2_s == "of"
                    ):
                        result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                else:
                    if device_idx1_i == 2:
                        if "heat" in value1_s:
                            if device_idx2_i == 0:
                                if value2_s == "on":
                                    result_e.add(CoreferRelEnum.COREFER_SAME)
                                elif value2_s == "off":
                                    result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                            elif device_idx2_i == 1:
                                if value2_s == "on":
                                    result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                                elif value2_s == "off":
                                    result_e.add(CoreferRelEnum.COREFER_SAME)
                        elif "cool" in value1_s:
                            if device_idx2_i == 0:
                                if value2_s == "on":
                                    result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                                elif value2_s == "off":
                                    result_e.add(CoreferRelEnum.COREFER_SAME)
                            elif device_idx2_i == 1:
                                if value2_s == "on":
                                    result_e.add(CoreferRelEnum.COREFER_SAME)
                                elif value2_s == "off":
                                    result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                        elif "mode" in value1_s:
                            result_e.update(
                                [
                                    CoreferRelEnum.COREFER_SAME,
                                    CoreferRelEnum.COREFER_OPPOSITE,
                                ]
                            )
                        elif "on" in value1_s:
                            result_e.add(CoreferRelEnum.COREFER_SAME)
                        elif "off" in value1_s:
                            result_e.add(CoreferRelEnum.COREFER_OPPOSITE)

                    elif device_idx2_i == 2:
                        if "heat" in value2_s:
                            if device_idx1_i == 0:
                                if value1_s == "on":
                                    result_e.add(CoreferRelEnum.COREFER_SAME)
                                elif value1_s == "off":
                                    result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                            elif device_idx1_i == 1:
                                if value1_s == "on":
                                    result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                                elif value1_s == "off":
                                    result_e.add(CoreferRelEnum.COREFER_SAME)
                        elif "cool" in value2_s:
                            if device_idx1_i == 0:
                                if value1_s == "on":
                                    result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                                elif value1_s == "off":
                                    result_e.add(CoreferRelEnum.COREFER_SAME)
                            elif device_idx1_i == 1:
                                if value1_s == "on":
                                    result_e.add(CoreferRelEnum.COREFER_SAME)
                                elif value1_s == "off":
                                    result_e.add(CoreferRelEnum.COREFER_OPPOSITE)
                        elif "mode" in value2_s:
                            result_e.update(
                                [
                                    CoreferRelEnum.COREFER_SAME,
                                    CoreferRelEnum.COREFER_OPPOSITE,
                                ]
                            )
                        elif "on" in value2_s:
                            result_e.add(CoreferRelEnum.COREFER_SAME)
                        elif "off" in value2_s:
                            result_e.add(CoreferRelEnum.COREFER_OPPOSITE)

            return EventRelationClass([tca1_u, tca2_u], result_e)

        logical_relation = get_logical_relation(tca1_u, tca2_u)
        temporal_relation = get_temporal_relation(tca1_u, tca2_u)
        causal_relation = get_causal_relation(tca1_u, tca2_u)
        corefer_relation = get_corefer_relation(tca1_u, tca2_u)

        return logical_relation, temporal_relation, causal_relation, corefer_relation

    def get_conflicts_statistics(self):

        stats_l = np.zeros((2, len(CONFLICTS_L)))
        for conflict_u in self.conflicts:
            possible_i = conflict_u.possible
            type_en = conflict_u.type
            index_i = CONFLICTS_INDEX_D[type_en]
            stats_l[possible_i][index_i] += 1
        return stats_l
