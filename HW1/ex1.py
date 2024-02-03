import itertools

import search
import random
import math


ids = ["111111111", "111111111"]


class OnePieceProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        search.Problem.__init__(self, initial)
        self.state = initial
        for key,value in self.state["pirate_ships"]:
            self.state["pirate_ships"][key] = (value,0)

        treasures = self.state["treasure"]
        for key,value in treasures.items():
            treasures[key] = [value,{ship:0 for ship in self.state["pirate_ships"].keys()}]
            treasures[key]["base"]=0

        marines = self.state["marine_ships"]
        for key,value in marines:
            marines[key]+=reversed(marines[key][1:-1])

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        pirates_actions = []
        for pirate,data in state["pirate_ships"].items():
            actions = [("wait",pirate)]
            pos = data[0]
            #sail actions:
            for i in range(4):
                new_pos =pos[i%2]+i//2
                if state["map"][new_pos]!="I":
                    actions.append(("sail",pirate,new_pos))
            #collecting actions
            for treasure,data in state["treasures"].items():
                t_pos = data[0]
                if self.manh_dist(t_pos,pos)==1:
                    actions.append(("collect_treasure",pirate,treasure))
            #deposit
            if state["map"][pos]=="B":
                actions.append(("deposit_treasures",pirate))
            pirates_actions.append(actions)

        return list(itertools.product(*pirates_actions))

    def manh_dist(self,x,y):
        distance = 0
        for i in range(2):
            distance += abs(x[i] - y[i])

        return distance


    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        ships_num = len(state["pirate_ships"])
        new_state = state.copy()
        for i in range(ships_num):
            act = action[i]
            if act[0] == "sail":
                new_state["pirate_ships"][act[1]][0] = act[2]
            elif act[0] == "collect_treasure":
                new_state["treasures"][act[2]][1][act[1]]+=1
                new_state["pirate_ships"][act[1]][1]+=1
            elif act[0] == "deposit_treasure":
                treasures = new_state["treasures"]
                for name,data in treasures.items():
                    if data[1][act[1]]>=1:
                        new_state["treasures"][name][1][act[1]]=0
                        new_state["treasures"][name][1]["base"]+=1
                        new_state["pirate_ships"][act[1]][1] -= 1

        #move marines

        for marine,data in new_state["marine_ships"].items():
            new_state["marine_ships"][marine]+=new_state["marine_ships"][marine].pop(0)

        new_state = self.check_collision(new_state)

        #TODO: add collisions

        return new_state

    def check_collision(self,state):
        for pirate,data in state["pirate_ships"].items():
            pos = data[0]
            for marine,path in state["marine_ships"].items():
                if self.manh_dist(path[0],pos)==0:
                    state["pirate_ships"][pirate][1] = 0
                    for treasure,not_needed in state["treasures"].items():
                        state["treasures"][treasure][1][pirate]=0
        return state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for treasure,data in state["treasures"].items():
            if data[1]["base"] == 0:
                return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return 0

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""





def create_onepiece_problem(game):
    return OnePieceProblem(game)

