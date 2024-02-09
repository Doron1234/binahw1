"""Search (Chapters 3-4)

The way to use this code is to subclass Problem to create a class of problems,
then create problem instances and solve them with calls to the various search
functions."""
import copy

from utils import (
    is_in, argmin, argmax, argmax_random_tie, probability, weighted_sampler,
    memoize, print_table, open_data, Stack, FIFOQueue, PriorityQueue, name,
    distance, hashabledict
)

from collections import defaultdict
import math
import random
import sys
import bisect
import time

infinity = float('inf')

# ______________________________________________________________________________


class Problem(object):

    """The abstract class for a formal problem.  You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal.  Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        raise NotImplementedError
# ______________________________________________________________________________


class Node:

    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next = problem.result(self.state, action)
        return Node(next, self, action,
                    problem.path_cost(self.path_cost, self.state,
                                      action, next))

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

# ______________________________________________________________________________


def astar_search(problem, h=None):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    # Memoize the heuristic function for better performance
    h = memoize(h or problem.h, 'h')
    # Function to calculate f(n) = g(n) + h(n)
    # Memoize this function for better performance
    f = memoize(lambda n: n.path_cost + h(n), 'f')
    cur_node = Node(problem.initial)
    open = [cur_node]

    sorting_time = 0

    distances = {hashify_state(cur_node.state):0} #TODO maybe switch to hash
    closed = []
    while(len(open) > 0):
        t = time.time()
        open = sorted(open, key=f)
        cur_node = open.pop(0)
        sorting_time+=time.time()-t
        if cur_node not in closed: #or cur_node.path_cost < distances[hashify_state(cur_node.state)]:
            time.sleep(0.01)
            closed.append(cur_node)
            distances[hashify_state(cur_node.state)] = cur_node.path_cost
            if problem.goal_test(cur_node.state):
                #print(sorting_time)
                return cur_node
            # print("checking actions of:")
            # print(cur_node.state["id"])
            # print(cur_node.state["pirate_ships"]["pirate_ship_1"])
            # print(cur_node.state["treasures"])
            # print(cur_node.state["order"])
            for a in problem.actions(cur_node.state):
                s = problem.result(cur_node.state, a)
                new_node = Node(s,cur_node, a, cur_node.path_cost + 1)
                if h(new_node)<float('inf'):
                    open.append(new_node)
        # else:
        #     print("duplicate detected!")
        #print(len(closed))

    return "unsolvable"



def hashify_state(state):
    state = copy.deepcopy(state)
    for key in state["pirate_ships"].keys():
        state["pirate_ships"][key] = tuple(state["pirate_ships"][key])
    for key in state["treasures"].keys():
        state["treasures"][key][1] = hashabledict(state["treasures"][key][1])
        state["treasures"][key] = tuple(state["treasures"][key])
    for key in state["marine_ships"].keys():
        state["marine_ships"][key] = tuple(state["marine_ships"][key])
    state["map"] = tuple(tuple(row) for row in state["map"])
    state["treasures"] = hashabledict(state["treasures"])

    if "order" in state.keys():
        state["order"] = tuple(state["order"])

    state["pirate_ships"] = hashabledict(state["pirate_ships"])

    state["marine_ships"] = hashabledict(state["marine_ships"])
    id = state["id"]
    del state["id"]
    ret = hashabledict(state)
    state["id"] = id
    return ret


