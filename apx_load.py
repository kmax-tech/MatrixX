import re

#load files in apx format

#use in order to create a specific file structure
class AF_Object():
    def __init__(self,name):
        self.name = name
        self.defensive= set() #list for storing the node, which are attacking the current instance
        self.offensive = set()

        self.number_is_defensive = 0
        self.number_is_offensive = 0

    def update_defensive(self,node):
        self.defensive.add(node)
        self.number_is_defensive += 1

    def update_offensive(self,node):
        self.offensive.add(node)
        self.number_is_offensive += 1

class AF_Init_Struct():
    def __init__(self,filename):
        self.formulae = dict()
        self.not_attacked_nodes = set() #for finding nodes, which are always true; not attacked #hashmap
        self.mutual_attacking_relations = [] #for finding pairs, which are attacking themeselves
        self.self_attacking_nodes = set()
        self.create_af_structure(filename)

    #create an input structure
    def create_af_structure(self,filename):
        with open(filename,"r") as file:
            for line in file.readlines(): #go through every line in the file
                work_area = line.strip().split(".")
                for ent in work_area:
                    #print("workarea",ent)
                    if "arg" in ent:
                        tes = re.search("\(\s*(\S*)\s*\)", ent)
                        node_name=tes.group(1)
                        current_instance = AF_Object(node_name)
                        self.formulae.update({node_name: current_instance})
                        self.not_attacked_nodes.add(node_name)

                    elif "att" in ent:
                        tes = re.search("\(\s*(\S*)\s*,\s*(\S*)\s*\)",ent)
                        line_split = [tes.group(1),tes.group(2)]
                        if line_split[1] in self.formulae.keys() and line_split[0] in self.formulae.keys():

                            #update offensive and defensive
                            self.formulae[line_split[0]].update_offensive(line_split[1])
                            self.formulae[line_split[1]].update_defensive(line_split[0])

                            # node is being attacked and removed from set of unattacked nodes
                            if line_split[1] in self.not_attacked_nodes:
                                self.not_attacked_nodes.remove(line_split[1])

                            #look for self attacking relations
                            if line_split[1] in self.formulae[line_split[0]].defensive:
                                self.mutual_attacking_relations.append([line_split[0],line_split[1]])

                            if line_split[0] == line_split[1]:
                                self.self_attacking_nodes.add(line_split[0])


if __name__ == "__main__":
    Node_Struct_Init = AF_Init_Struct("CE-ST-1.apx")
    for form in Node_Struct_Init.formulae.values():
        print(form.name,"off",form.offensive,"def",form.defensive)
