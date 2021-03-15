#encoding: utf8

from semantic_network import *
from bayes_net import *
from constraintsearch import *


class MyBN(BayesNet):

    def individual_probabilities(self):
        variaveis = [k for k in self.dependencies.keys()]
        individual_probs = {}
        for var in variaveis:
            new_var_list = [k for k in self.dependencies.keys() if k!=var]
            individual_probs[var] = sum([self.jointProb([(var,True)]+c) for c in self.conjunctions(new_var_list)])
        return individual_probs
        
    def conjunctions(self, variaveis):
        if len(variaveis) == 1:
            return [[(variaveis[0],True)],[(variaveis[0],False)]]    
        l = []
        for c in self.conjunctions(variaveis[1:]):
            l.append([(variaveis[0], True)] + c)
            l.append([(variaveis[0], False)] + c)
        return l
    
class MySemNet(SemanticNetwork):
    def __init__(self):
        SemanticNetwork.__init__(self)

    def translate_ontology(self):
        # TODO: clean this spaghetti code
        list_of_rels = list(set([d.relation for d in self.declarations if isinstance(d.relation,Subtype)]))
        relations = {}
        for rel in list_of_rels:
            if rel not in relations:
                relations[rel.entity1] = rel.entity2
        # create a dictionary with a list of subtypes per supertype
        new_dict = {}
        for key,value in sorted(relations.items()):
            new_dict.setdefault(value, []).append(key)
        
        string = 'Qx '
        list_of_strings = []
        for key,value in sorted(new_dict.items()):
            for val in value:
                string = string + str(val).capitalize() + '(x)'
                i = value.index(val)
                if i < len(value)-1:
                    string = string + ' or '
                else:
                    string = string + ' => ' + str(key).capitalize() + '(x)'
            list_of_strings.append(string)
            string = 'Qx '
        
        return list_of_strings
        
    def query_inherit(self,entity,assoc):
        queries = [self.query_inherit(d.relation.entity2, assoc) for d in self.declarations 
                          if isinstance(d.relation, (Member, Subtype)) and d.relation.entity1 == entity]
        return list(set([d for sublist in queries for d in sublist] + self.query_local(e1=entity, relname=assoc)))
        
        #queries = [d.relation for d in self.declarations if isinstance(d.relation, Association) and d.relation.inverse == assoc]
        #print(queries)
        
    def query(self,entity,relname):
        queries = [self.query_inherit(d.relation.entity2, relname) for d in self.declarations 
                          if isinstance(d.relation, (Member, Subtype)) and d.relation.entity1 == entity]
        return [d.relation.entity2 for d in queries]
        
        
class MyCS(ConstraintSearch):

    def search_all(self,domains=None,xpto=None):
        # Pode usar o argumento 'xpto' para passar mais
        # informação, caso precise
        #
        solutions = []
        if domains==None:
            domains = self.domains

        # se alguma variavel tiver lista de valores vazia, falha
        if any([lv==[] for lv in domains.values()]):
            return None

        # se nenhuma variavel tiver mais do que um valor possivel, sucesso
        if all([len(lv)==1 for lv in list(domains.values())]):
            return { v:lv[0] for (v,lv) in domains.items() }
       
        # continuação da pesquisa
        for var in domains.keys():
            if len(domains[var])>1:
                for val in domains[var]:
                    newdomains = dict(domains)
                    newdomains[var] = [val]
                    edges = [(v1,v2) for (v1,v2) in self.constraints if v2==var]
                    newdomains = self.constraint_propagation(newdomains,edges)
                    solution = self.search(newdomains)
                    if solution != None and solution not in solutions:
                        solutions.append(solution)
        
        if solutions != []:
            return solutions        
        return None


