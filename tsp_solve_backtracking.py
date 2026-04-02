import math
from platform import node
import random

from utils import Tour, SolutionStats, Timer, score_tour, Solver
from cuttree import CutTree


def random_tour(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    stats = []
    n_nodes_expanded = 0
    n_nodes_pruned = 0
    cut_tree = CutTree(len(edges))

    while True:
        if timer.time_out():
            return stats

        tour = random.sample(list(range(len(edges))), len(edges))
        n_nodes_expanded += 1

        cost = score_tour(tour, edges)
        if math.isinf(cost):
            n_nodes_pruned += 1
            cut_tree.cut(tour)
            continue

        if stats and cost > stats[-1].score:
            n_nodes_pruned += 1
            cut_tree.cut(tour)
            continue

        stats.append(SolutionStats(
            tour=tour,
            score=cost,
            time=timer.time(),
            max_queue_size=1,
            n_nodes_expanded=n_nodes_expanded,
            n_nodes_pruned=n_nodes_pruned,
            n_leaves_covered=cut_tree.n_leaves_cut(),
            fraction_leaves_covered=cut_tree.fraction_leaves_covered()
        ))

    if not stats:
        return [SolutionStats(
            [],
            math.inf,
            timer.time(),
            1,
            n_nodes_expanded,
            n_nodes_pruned,
            cut_tree.n_leaves_cut(),
            cut_tree.fraction_leaves_covered()
        )]


def greedy_tour(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    solutions: list[SolutionStats] = []

    def greedy_explore(current: int, tour: Tour, visited: set[int]) -> None:
        if timer.time_out():
            return
        
        if len(tour) == len(edges):
            if not math.isinf(edges[current][tour[0]]):
                score = score_tour(tour, edges)
                if not solutions or score < solutions[-1].score:
                    solutions.append(SolutionStats(
                        tour=tour.copy(),
                        score=score,
                        time=timer.time(),
                        max_queue_size=1,
                        n_nodes_expanded=0,
                        n_nodes_pruned=0,
                        n_leaves_covered=0,
                        fraction_leaves_covered=0
                    ))
            return
        
        min_edge = math.inf
        min_index = -1
        for index, edge in enumerate(edges[current]):
            if index in visited or math.isinf(edge):
                continue
            if edge < min_edge:
                min_edge = edge
                min_index = index

        if min_index == -1:
            return # No unvisited neighbors, dead end

        tour.append(min_index)
        visited.add(min_index)
        greedy_explore(min_index, tour, visited)

    for curr_node in range(len(edges)):
        if timer.time_out():
            break
        greedy_explore(curr_node, [curr_node], {curr_node})

    return solutions


def backtracking(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    solutions: list[SolutionStats] = []

    def backtracking_explore(current: int, tour: Tour, visited: set[int]) -> None:
        if timer.time_out():
            return
        
        if len(tour) == len(edges):
            if not math.isinf(edges[current][tour[0]]):
                score = score_tour(tour, edges)
                if not solutions or score < solutions[-1].score:
                    solutions.append(SolutionStats(
                        tour=tour.copy(),
                        score=score,
                        time=timer.time(),
                        max_queue_size=1,
                        n_nodes_expanded=0,
                        n_nodes_pruned=0,
                        n_leaves_covered=0,
                        fraction_leaves_covered=0
                    ))
            return
        
        for index, edge in enumerate(edges[current]):
            if index in visited or math.isinf(edge):
                continue
            else:
                tour.append(index)
                visited.add(index)
                backtracking_explore(index, tour, visited)
                tour.pop()
                visited.remove(index)

    for curr_node in range(len(edges)):
        if timer.time_out():
            break
        backtracking_explore(curr_node, [curr_node], {curr_node})

    return solutions

def backtracking_bssf(edges: list[list[float]], timer: Timer) -> list[SolutionStats]:
    greedy_solutions = greedy_tour(edges, timer)
    bssf = greedy_solutions[-1].score if greedy_solutions else math.inf
    solutions = greedy_solutions.copy()

    def bssf_explore(current: int, tour: Tour, visited: set[int], current_cost: float) -> None:
        nonlocal bssf
        if timer.time_out():
            return
        
        if len(tour) == len(edges):
            return_cost = edges[current][tour[0]]
            if not math.isinf(return_cost):
                total = current_cost + return_cost
                if total < bssf:
                    bssf = total
                    solutions.append(SolutionStats(
                        tour=tour.copy(),
                        score=total,
                        time=timer.time(),
                        max_queue_size=1,
                        n_nodes_expanded=0,
                        n_nodes_pruned=0,
                        n_leaves_covered=0,
                        fraction_leaves_covered=0
                    ))
            return
        
        for index, edge in enumerate(edges[current]):
            if index in visited or math.isinf(edge):
                continue
            if current_cost + edge >= bssf:
                continue
            tour.append(index)
            visited.add(index)
            bssf_explore(index, tour, visited, current_cost + edge)
            tour.pop()
            visited.remove(index)

    for curr_node in range(len(edges)):
        if timer.time_out():
            break
        bssf_explore(curr_node, [curr_node], {curr_node}, 0)

    return solutions

