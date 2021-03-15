
# Name: Luís Miguel Dias dos Santos Pereira da Costa
# Nmec: 85044

from tree_search import *
from cidades import *
from strips import *

class MyNode(SearchNode):
    def __init__(self,state,parent,depth,offset):
        super().__init__(state,parent)
        self.depth = depth
        self.offset = offset
        self.diff = self.depth-self.offset

class MyTree(SearchTree):

    def __init__(self,problem, strategy='breadth'): 
        self.problem = problem
        self.root = MyNode(problem.initial, None,0,0)
        self.open_nodes = [self.root]
        self.strategy = strategy
        self.terminal = 0
        self.non_terminal = 0
        self.solution = None
        self.from_init = ''
        self.to_goal = ''
        

    def hybrid1_add_to_open(self,lnewnodes):  
        if lnewnodes == []:
            self.open_nodes = self.open_nodes
        else:     
            even_nodes = [p for idx, p in enumerate(lnewnodes) if idx%2==0]
            odd_nodes = [p for idx, p in enumerate(lnewnodes) if idx%2!=0]
            even_nodes.reverse()
            odd_nodes.reverse()
            self.open_nodes= even_nodes+self.open_nodes+odd_nodes
        

    def hybrid2_add_to_open(self,lnewnodes):
        # checks if lnewnodes is not empty
        if lnewnodes == []:
            self.open_nodes = self.open_nodes
        else:
            # adds the new nodes to the list of open nodes
            self.open_nodes.extend(lnewnodes)
            # sorts the open_nodes list according to the difference between depth and offset
            #self.open_nodes.sort(key=lambda node: (node.diff,node.depth))
            self.open_nodes.sort(key=lambda node: node.diff)


    def search2(self):
        dic = {}
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node.state):
                self.terminal = len(self.open_nodes)+1
                self.solution = node
                return self.get_path(node)
            self.non_terminal+=1
            node.children = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                if newstate not in self.get_path(node):
                    if dic.get(node.depth+1):
                        offset = dic.get(node.depth+1)
                    else:
                        offset = dic[node.depth+1]  = 0
                    dic[node.depth+1]+=1
                    newnode = MyNode(newstate,node,depth=node.depth+1,offset=offset)
                    node.children.append(newnode)  
            self.add_to_open(node.children)
        return None


    def search_from_middle(self):
        middle_state = MinhasCidades.middle(self.problem.domain,city1=self.problem.initial, city2=self.problem.goal)
        problem_1 = SearchProblem(self.problem.domain, initial=self.problem.initial, goal=middle_state)
        problem_2 = SearchProblem(self.problem.domain, initial=middle_state, goal=self.problem.goal)
        self.from_init = MyTree(problem_1,self.strategy)
        self.to_goal = MyTree(problem_2,self.strategy)
        p1 = self.from_init.search2()
        p2 = self.to_goal.search2()
        # removes duplicates and mantains order
        return list(dict.fromkeys(p1+p2))


class MinhasCidades(Cidades):

    def middle(self,city1,city2):
        # creates a tuple (distance, city) that contains de city 
        # with the smallest distante to city1 and 2
        minimum = min([(self.heuristic(city1,p) + self.heuristic(p,city2),p) for p in self.coordinates if (str(p) not in [city1,city2])])
        return minimum[1]

        
class MySTRIPS(STRIPS):
    # allows for comparisons between with ">" operator
    # removed since we are comparing strings
    #def __gt__(self,predicate):
    #    return str(self) > str(predicate)  
    
    def result(self, state, action):
        if not all(p in state for p in action.pc):
            return None
        new_state = [p for p in state if p not in action.neg]
        new_state.extend(action.pos)
        return new_state
        
    def sort(self,state):
        if state == []:
            return None
        state.sort(key=str)
        return state
        
        # implementation for the bubble sort algorithm
        # deprecated in favor of the native sort function 
        #n = len(state)-1
        #for i in range(n): 
        #    for j in range(0, n-i): 
        #        if str(state[j]) > (str(state[j+1])):
        #            (state[j], state[j+1]) = (state[j+1], state[j])
        #return state