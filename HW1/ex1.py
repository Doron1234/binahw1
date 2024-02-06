import itertools
import copy
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
        for key,value in self.state["pirate_ships"].items():
            self.state["pirate_ships"][key] = [value,0]

        treasures = self.state["treasures"]
        for key, value in treasures.items():
            treasures[key] = [value,{ship:0 for ship in self.state["pirate_ships"].keys()}]
            treasures[key][1]["base"]=0

        marines = self.state["marine_ships"]
        for key, value in marines.items():
            marines[key]+=reversed(marines[key][1:-1])
        self.base = self.state["pirate_ships"]["pirate_ship_1"][0]


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
                if i==1:
                    new_pos = (pos[0],pos[1]+1)
                elif i==2:
                    new_pos = (pos[0],pos[1]-1)
                elif i==3:
                    new_pos = (pos[0]+1,pos[1])
                elif i==0:
                    new_pos = (pos[0]-1,pos[1])
                if new_pos[0]>=0 and new_pos[0]<len(state["map"]) and new_pos[1]>=0 and new_pos[1]<len(state["map"][0]) and state["map"][new_pos[0]][new_pos[1]]!="I":
                    actions.append(("sail",pirate,new_pos))
            #collecting actions
            if state["pirate_ships"][pirate][1]<2:
                for treasure,data in state["treasures"].items():
                    t_pos = data[0]
                    if self.manh_dist(t_pos,pos)==1:
                        actions.append(("collect_treasure",pirate,treasure))
            #deposit
            if state["map"][pos[0]][pos[1]]=="B" and state["pirate_ships"][pirate][1] > 0:
                actions.append(("deposit_treasure",pirate))
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
        new_state = copy.deepcopy(state)
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
                        new_state["pirate_ships"][act[1]][1] = 0
        #move marines

        for marine,data in new_state["marine_ships"].items():
            new_state["marine_ships"][marine].append(new_state["marine_ships"][marine].pop(0))

        new_state = self.check_collision(new_state)

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

    def h1(self, node):
        count = 0
        s = node.state
        for t_name,value in s["treasures"].items():
            count+=1
            for ship,num in value[1].items():
                if num==1:
                    count-=1
                break
        return count/len(s["pirate_ships"])

    def h2(self,node):
        s = node.state
        sum = 0
        for t_name, value in s["treasures"].items():
            pos = value[0]
            posses = []
            for i in range(4):
                if i == 1:
                    new_pos = (pos[0], pos[1] + 1)
                elif i == 2:
                    new_pos = (pos[0], pos[1] - 1)
                elif i == 3:
                    new_pos = (pos[0] + 1, pos[1])
                elif i == 0:
                    new_pos = (pos[0] - 1, pos[1])
                if new_pos[0] >= 0 and new_pos[0] < len(s["map"]) and new_pos[1] >= 0 and new_pos[1] < len(
                        s["map"][0]) and s["map"][new_pos[0]][new_pos[1]] == "S":
                    posses.append(new_pos)
            if value[1]["base"]==1:
                sum+=1
                break
            for pirate,value in value[1].items():
                if pirate == "base":
                    continue
                elif value == 1:
                    pos = s["pirate_ships"][pirate][0]
                    for i in range(4):
                        if i == 1:
                            new_pos = (pos[0], pos[1] + 1)
                        elif i == 2:
                            new_pos = (pos[0], pos[1] - 1)
                        elif i == 3:
                            new_pos = (pos[0] + 1, pos[1])
                        elif i == 0:
                            new_pos = (pos[0] - 1, pos[1])
                        if new_pos[0] >= 0 and new_pos[0] < len(s["map"]) and new_pos[1] >= 0 and new_pos[1] < len(
                                s["map"][0]) and s["map"][new_pos[0]][new_pos[1]] == "S":
                            posses.append(new_pos)
            if len(posses)==0:
                return float('inf')
            sum+= min([self.manh_dist(x,self.base) for x in posses])
        return sum/len(s["pirate_ships"])




    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return self.h2(node)

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""





def create_onepiece_problem(game):
    return OnePieceProblem(game)

