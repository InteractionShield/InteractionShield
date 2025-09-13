import os
import math
import json
import random
from itertools import compress
import concurrent.futures
import time
import numpy as np
from pathlib import Path

from Python.utils.constant import MEDIUM, ROOM_PARAMETERS_D
from Python.utils.application import ApplicationClass
from Python.utils.detector import ConflictDetectorClass
from Python.utils.miscellaneous import (
    read_json,
    print_seconds_to_readable,
    print_memory_usage,
    format_nd_array,
)
from Python.utils.enums import AppTypeEnum
from Python.utils.simulation import (
    read_appinfos,
    get_device_related_appinfos,
    plot_grouped_conflicts,
    read_rules,
    get_all_rules,
)


def _calculate_objective_for_process(args):
    all_rules, properties, risk_level, room_parameters, lamb, chromosome = args
    current_rules = list(compress(all_rules, chromosome))

    if not current_rules:
        return 0, 0, chromosome  # penalty, objective_value, chromosome
    else:
        detector = ConflictDetectorClass(current_rules, properties, risk_level, room_parameters)
        penalty = detector.penalty
        objective_value = penalty - lamb * len(current_rules)
        detector.clear()
        return penalty, objective_value, chromosome


class ConflictResolverClass:

    def __init__(
        self, rules_l, properties_l, risk_level_i=MEDIUM, room_parameters_d=ROOM_PARAMETERS_D, lambda_f=4
    ):
        if not rules_l:
            raise ValueError("Empty rules!")
        self.all_rules = rules_l
        self.properties = properties_l
        self.risk_level = risk_level_i
        self.room_parameters = room_parameters_d
        self.lamb = lambda_f
        self.num_rules = len(self.all_rules)

    def resolve(
        self,
        population_size=40,
        generations=80,
        crossover_rate=0.8,
        mutation_rate=0.02,
        tournament_size=5,
        early_stopping_patience=10,
        verbose=False,
    ):
        initial_detector = ConflictDetectorClass(
            self.all_rules, self.properties, self.risk_level, self.room_parameters
        )
        initial_penalty = initial_detector.penalty
        initial_detector.clear()

        if verbose:
            print(f"Initial Penalty: {initial_penalty}")

        population = [
            [random.randint(0, 1) for _ in range(self.num_rules)]
            for _ in range(population_size)
        ]
        best_solution_chromosome = None
        best_objective_value = float("inf")
        generations_without_improvement = 0

        with concurrent.futures.ProcessPoolExecutor() as executor:
            for gen in range(generations):
                args_list = [
                    (
                        self.all_rules,
                        self.properties,
                        self.risk_level,
                        self.room_parameters,
                        self.lamb,
                        chrom,
                    )
                    for chrom in population
                ]

                results = list(
                    executor.map(_calculate_objective_for_process, args_list)
                )

                penalties = [res[0] for res in results]
                objectives = [res[1] for res in results]

                min_obj_in_gen = min(objectives)
                if min_obj_in_gen < best_objective_value:
                    best_objective_value = min_obj_in_gen
                    best_solution_chromosome = results[
                        objectives.index(min_obj_in_gen)
                    ][2]
                    generations_without_improvement = 0
                else:
                    generations_without_improvement += 1

                if (gen + 1) % 10 == 0 or gen == 0:
                    if verbose:
                        print(
                            f"Iteration {gen + 1}/{generations}: Best f={best_objective_value:.2f} | {generations_without_improvement+1} generations without improvement"
                        )

                if best_solution_chromosome:
                    best_objective_idx = np.argmin(objectives)
                    best_penalty = penalties[best_objective_idx]

                    if (
                        math.isclose(best_penalty, 0.0)
                        and sum(best_solution_chromosome) == self.num_rules
                    ):
                        if verbose:
                            print(f"\nIteration {gen + 1} Found optimal solution!")
                        break

                    if generations_without_improvement >= early_stopping_patience:
                        if verbose:
                            print(
                                f"\n{early_stopping_patience} generations without improvement, stopping early at iteration {gen + 1}."
                            )
                        break

                new_population = []
                while len(new_population) < population_size:

                    def tournament_selection():
                        indices = random.sample(range(population_size), tournament_size)
                        return min(
                            ((objectives[i], population[i]) for i in indices),
                            key=lambda x: x[0],
                        )[1]

                    parent1, parent2 = tournament_selection(), tournament_selection()

                    if random.random() < crossover_rate:
                        point = random.randint(1, self.num_rules - 1)
                        child1, child2 = (
                            parent1[:point] + parent2[point:],
                            parent2[:point] + parent1[point:],
                        )
                    else:
                        child1, child2 = parent1[:], parent2[:]

                    def mutate(chromosome):
                        return [
                            1 - bit if random.random() < mutation_rate else bit
                            for bit in chromosome
                        ]

                    new_population.append(mutate(child1))
                    if len(new_population) < population_size:
                        new_population.append(mutate(child2))

                population = new_population

        final_rules = (
            list(compress(self.all_rules, best_solution_chromosome))
            if best_solution_chromosome
            else []
        )
        final_penalty, final_objective, _ = (
            _calculate_objective_for_process(
                (
                    self.all_rules,
                    self.properties,
                    self.risk_level,
                    self.room_parameters,
                    self.lamb,
                    best_solution_chromosome,
                )
            )
            if best_solution_chromosome
            else (0, 0, None)
        )

        if verbose:
            print("--- Finish ---")
        return final_rules, final_penalty, final_objective
