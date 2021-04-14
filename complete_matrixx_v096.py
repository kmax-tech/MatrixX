import tgf_load, apx_load, time, pickle, argparse,functools

#this is the matrixx solver for complete semantics

#the solver creates a matrix like structure, with information about node attacks and defenses
#the matrix is systematically shrinkened and evaluated in a top down approach

#deal with the associated task
class Semantics_Dealer():
    def __init__(self):
        self.filename = ""
        self.file_format=""
        self.semantics = ""
        self.additional_parameter = ""

        self.Ctrl_Calc = Control_Calculation()  #create the object for the calculation
        #are required by the desired semantics
        self.credulous_interpretations = set()
        self.sceptical_interpretations = set()

        #deal with the control flow
        self.parse_arguments()
        self.control_calculations()

    #needed in evaluation for loop calc and after calc
    def empty_func(self):
        pass

    #get input from command line
    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="get the options from the command line")
        parser.add_argument("-fo", help=".tgf or .apx")
        parser.add_argument("-f", help="file for the calculation")
        parser.add_argument("-p", help="specify the tasks")
        parser.add_argument("-a", help="use additional parameter")
        args = parser.parse_args()
        self.filename = args.f
        self.semantics= args.p
        self.addit_para = args.a
        self.file_format = args.fo

        #self.debug = True
        self.debug = False #debug flag for more detailed output
        #debug part for more verbose output
        if self.debug:
            self.semantics = "DEBUG"
            self.filename = "../../A-1-admbuster_6000.apx"  #specify the filename directly here
            self.addit_para ="a1"

    #init the Calculation according to the specified semantics
    def control_calculations(self):
        #Init the complete Framework
        if self.file_format == "tgf" or self.filename.endswith(".tgf"):
            Init_Struct = tgf_load.AF_Init_Struct(self.filename)
        elif self.file_format == "apx" or self.filename.endswith(".apx"):
            Init_Struct = apx_load.AF_Init_Struct(self.filename)

        # do preprocessing
        sp = Structure_Preprocessing(Init_Struct)  # preprocessing of calculation object
        for x in sp.output:
            for complete_interpretation in sp.complete_start_interpretations:
                if complete_interpretation not in self.Ctrl_Calc.total_interpretations:
                    self.Ctrl_Calc.total_interpretations.append(complete_interpretation)
            self.Ctrl_Calc.interpretation_hierarchy_manager(x)

        #loop calc is needed for the semantics where checks are occuring during evaluation
        #after calc is needed for evaluation; after evaluation has finished
        loop_eval = self.empty_func
        after_eval = self.empty_func

        #expand calculation according to the specified semantics
        if self.semantics == "CE-CO":
            after_eval = self.sem_check_CE_CO

        #check parameter in sceptical interpretations
        elif self.semantics == "DS-CO":
            after_eval = self.sem_check_DS_CO

        elif self.semantics == "DC-CO": #credulously accepted
            loop_eval = self.sem_check_DC_CO_loop
            after_eval = self.sem_check_DC_CO_after

        elif self.semantics == "SE-CO": #one extension
            loop_eval = self.sem_check_SE_CO_loop
            after_eval = self.sem_check_SE_CO_after

        #measure time and print all interpretations
        elif self.semantics == "DEBUG": #one extension
            self.start = time.time()
            after_eval = self.print_interpretations

     #separate whether checks need to be done during calculation or not
        while True:
            loop_eval() #do calc check
            current_calc_object = self.Ctrl_Calc.instance_checker()
            if self.Ctrl_Calc.calc_completed == True:
                break
            self.Ctrl_Calc.eval_Calc_Object(current_calc_object) #evaluate the current selected object
        after_eval()

    #define specified semantics
    def sem_check_CE_CO(self): #give number of all extensions
        print(len(self.Ctrl_Calc.total_interpretations))

    def sem_check_DS_CO(self): #check sceptical interpretations
        if len(self.Ctrl_Calc.total_interpretations) != 0:
            self.sceptical_interpretations = functools.reduce(lambda x,y: x.intersection(y), self.Ctrl_Calc.total_interpretations)
            if self.addit_para in self.sceptical_interpretations:
                print("YES")
            else:
                print("NO")
        else:
            print("YES")

    #decide whether an argument is credulously accepted
    def sem_check_DC_CO_loop(self):
        for interpretation in self.Ctrl_Calc.total_interpretations:
            self.credulous_interpretations = self.credulous_interpretations.union(interpretation)
        self.Ctrl_Calc.total_interpretations = [] #reset parameter

        if self.addit_para in self.credulous_interpretations:
            print("YES")
            self.Ctrl_Calc.calc_completed = True #abort the calculation procedure

    def sem_check_DC_CO_after(self):
        if self.addit_para not in self.credulous_interpretations:
            print("NO")

    #give one extension
    def sem_check_SE_CO_loop(self):
        if len(self.Ctrl_Calc.total_interpretations) != 0:
            pre_string = ",".join(self.Ctrl_Calc.total_interpretations[0])
            print("[" + pre_string + "]")
            self.Ctrl_Calc.calc_completed = True  #abort the calculation procedure

    def sem_check_SE_CO_after(self):
        if len(self.Ctrl_Calc.total_interpretations) == 0:
            print("NO")

    #used in order to print all interpretations
    def print_interpretations(self):
        self.end = time.time()
        print("\nPrinting All Complete Interpretations \n")
        for index, x in enumerate(self.Ctrl_Calc.total_interpretations):
            print("Nr.{}".format(index + 1), x, "\n")
        print("Total Time")
        print(self.end - self.start)


class Structure_Information():
    def __init__(self):
        self.interpretations = set()
        self.complete_interpretations = []
        self.current_buffer_nodes  = set()
        self.current_interpretation_node = set()
        #lists for the current used nodes
        self.offensive_nodes = set()
        self.defensive_nodes = set() #for considering column information
        self.Structure_Information = dict()
        #information about the used steps of calculation
        self.calc_offensive_depth = 0
        self.calc_defense_depth = 0

def node_def_re_evaluate(node): #calculate again number of edge connections
        node.number_is_defensive = len(node.defensive)

class Copy_Calcstrucutre(): #fast deepcopy of the Node_Structure
    def __init__(self,Node_Structure):
        self.output = []
        self.clone_out(Node_Structure)

    def clone_out(self,Node_Structure):
        for x in range(0,2):
            pick_struct = pickle.dumps(Node_Structure)
            unpick_object = pickle.loads(pick_struct)
            self.output.append(unpick_object)

#deal with a control_class which can spawn new instances as desired
#if several options are existing, we fork the current interpretation
class Control_Calculation():
    def __init__(self):
        self.total_interpretations = [] #acts as the global object where all formulae are stored
        self.total_storage_of_calc_object = dict() #store objects according to the recursion depth
        self.maximum_calc_depth = 0
        self.calc_completed = False


    def interpretation_hierarchy_manager(self, Calc_Object):
        new_depth = Calc_Object.calc_offensive_depth
        if new_depth not in self.total_storage_of_calc_object.keys(): #create key
            self.total_storage_of_calc_object.update({new_depth : []})
        if new_depth > self.maximum_calc_depth:
            self.maximum_calc_depth = new_depth
        self.total_storage_of_calc_object[new_depth].append(Calc_Object)

    def final_interpretation_manager(self,Calc_Object):
        if Calc_Object.interpretations not in self.total_interpretations:
            self.total_interpretations.append(Calc_Object.interpretations)

    #check for complete interpretations
    def check_defense(self,Node_Structure):

        #check whether there are unattacked nodes in the current set
        for defense_info in Node_Structure.defensive_nodes:
            if Node_Structure.Structure_Information[defense_info].number_is_defensive == 0:
                return False

        #check whether all nodes are defended at the moment
        for node in Node_Structure.interpretations:
            if Node_Structure.Structure_Information[node].number_is_defensive != 0:
                return False
        return True

    def eval_Calc_Object(self,Node_Structure):
        if self.check_defense(Node_Structure):
            self.final_interpretation_manager(Node_Structure) #append the interpretations
        if len(Node_Structure.offensive_nodes) != 0:
            defenses = Defensive_Ripper(Node_Structure) #if no possible combination is found defenses.output is empty
            for obj in defenses.output:
                Offensive_Ripper(obj)
                self.interpretation_hierarchy_manager(obj) #if objects are existing, they are added to the calculation list

    #look whether there exists object in the work lists, the first element is returned, else there is a check one hierarchy lower
    def instance_checker(self):
        for hierarchy_level in reversed(range(0, self.maximum_calc_depth + 1)):
            if len(self.total_storage_of_calc_object[hierarchy_level]) != 0: #entries exist at this hierarchy level
                current_instance = self.total_storage_of_calc_object[hierarchy_level].pop(0) #get the first element, and remove it from pool list
                return  current_instance
        self.calc_completed = True #no further calculations have to be done anymore, calculations can be stopped

#filter out nodes, which are not compatible with the current_interpretation
#column part in ALG-X
class Defensive_Ripper():
    def __init__(self,Pre_Node_Structure):
        self.Pre_Node_Structure = Pre_Node_Structure
        self.new_objects = Copy_Calcstrucutre(Pre_Node_Structure).output
        self.output = []
        self.nodes_to_be_evaluated = self.Pre_Node_Structure.offensive_nodes.intersection(self.Pre_Node_Structure.defensive_nodes)

        if len(self.nodes_to_be_evaluated) != 0:  # there is at least one defensive node left, which can be processed
            self.eval_defense()  #start calculations

    def eval_defense(self):
        #get the defense information with the lowest combinations
        defensive_node = self.search_defense_info()
        #means that there exists at least a node, which attacks the current node
        if defensive_node[1] == 0:  #an unattacked object should always be chosen, no forking occurs
            x = self.use_node(self.new_objects[0], defensive_node[0])
            self.output.append(x)
        else:
            x = self.use_node(self.new_objects[0], defensive_node[0])
            y = self.erase_node(self.new_objects[1], defensive_node[0])

            self.output.append(x)
            self.output.append(y)

    #find the argument, with the least number of attackers
    def search_defense_info(self):
        analyze_set =  self.nodes_to_be_evaluated
        defense_name = analyze_set.pop()
        defense_numbers = self.Pre_Node_Structure.Structure_Information[defense_name].number_is_defensive
        for defense_info in analyze_set:
            def_len = self.Pre_Node_Structure.Structure_Information[defense_info].number_is_defensive
            if def_len == 0:
                defense_numbers = def_len
                defense_name = defense_info
                break     # breaking at this point
            if def_len <= defense_numbers:
                defense_numbers = def_len
                defense_name = defense_info
        return (defense_name,defense_numbers)

    #create object where the node itself is contained
    def use_node(self,Node_Structure,node):
        Node_Structure.calc_defense_depth += 1
        # create object where the node corresponding to the selected column had been chosen
        Node_Structure.interpretations.add(node)  # node had been chosen; so it is added to the interpretations
        Node_Structure.current_interpretation_node = node
        # mark the node which are getting attacked by the selected node
        Node_Structure.current_buffer_nodes = self.Pre_Node_Structure.Structure_Information[node].defensive
        return Node_Structure

    #create second object where the selected column is erased
    def erase_node(self,Node_Structure,node):
        Node_Structure.calc_defense_depth += 1
        Node_Structure.current_buffer_nodes = set()
        Node_Structure.current_buffer_nodes.add(node)
        Node_Structure.current_interpretation_node = set()
        return Node_Structure


#does the part of rows in ALG-X
class Offensive_Ripper():
    def __init__(self,Node_Structure):
        self.Node_Structure = Node_Structure
        self.offensive_nodes_rem = set()
        self.defensive_nodes_rem = set()
        self.offense_eval()

    def offense_eval(self):
        self.Node_Structure.calc_offensive_depth += 1

        #select nodes, which are not combinable with the current selected interpretation, for offensive deletion
        for attacking_node in self.Node_Structure.current_buffer_nodes:
            self.offensive_nodes_rem.add(attacking_node)

        #erase the information
        self.clean_offense_nodes()
        self.offensive_nodes_rem = set()

        #no node has been selected therefore just buffer information are selected
        if len(self.Node_Structure.current_interpretation_node) != 0:
            self.clean_nodes_under_attack() #mark nodes for deletion, which are attacked by the current interpretation
            self.clean_offensive_attack_nodes()
            self.offensive_nodes_rem.add(self.Node_Structure.current_interpretation_node)
            self.defensive_nodes_rem.add(self.Node_Structure.current_interpretation_node)
            self.clean_offense_nodes()
            self.clean_defense_nodes()

    #the nodes in nodeset are not compatible with the current selected interpretation
    #every attack which is directed by these noncompatible nodes is going to get removed
    def clean_offensive_attack_nodes(self):
        for attacking_node in self.offensive_nodes_rem: #sets up the erasing procedure, for the offensive nodes in current used nodes
            for rel_attack in self.Node_Structure.Structure_Information[attacking_node].offensive:
                #remove dependencies of all nodes being attacked
                if attacking_node in self.Node_Structure.Structure_Information[rel_attack].defensive:
                    self.Node_Structure.Structure_Information[rel_attack].defensive.remove(attacking_node)
                    node_def_re_evaluate(self.Node_Structure.Structure_Information[rel_attack])

    #erase the nodes and defensive information, which are attacked by the current selected interpretation node
    def clean_nodes_under_attack(self):
        for attacked_node in self.Node_Structure.Structure_Information[self.Node_Structure.current_interpretation_node].offensive:
            #all attacks by these nodes are getting removed
            self.offensive_nodes_rem.add(attacked_node)
            self.defensive_nodes_rem.add(attacked_node)

    #erase the current selected nodes for offensive and defensive information
    def clean_offense_nodes(self):
        for node in self.offensive_nodes_rem:
            if node in self.Node_Structure.offensive_nodes:
                self.Node_Structure.offensive_nodes.remove(node)

    def clean_defense_nodes(self):
        for node in self.defensive_nodes_rem:
            if node in self.Node_Structure.defensive_nodes:
                self.Node_Structure.defensive_nodes.remove(node)


#deal with true nodes and self-attacking relations
class Structure_Preprocessing():
    def __init__(self,Init_Node_Structure):
        self.Init_Node_Structure = Init_Node_Structure
        self.output = []
        #prepare the calc structure for further processing
        self.calc_structure = Structure_Information()

        #storage for nodes,which will be removed in the first run
        self.prepro_offensive_nodes_rem = set()
        self.prepro_defensive_nodes_rem = set()
        #nodes, where the defensive information is updated
        self.offensive_defense_update_nodes = set()

        self.complete_start_interpretations = []
        self.complete_sing_interpretation = set()

        self.init_calc_structure()

        #repeat the starting procedure until a fixpoint is found
        fixpoint_cycling=self.init_cycling()
        while fixpoint_cycling == 1:
            fixpoint_cycling = self.init_cycling()
            #self.complete_start_interpretations.append(copy.deepcopy(self.complete_sing_interpretation))

        self.complete_start_interpretations.append(self.complete_sing_interpretation)

        #return the final structure
        self.output.append(self.calc_structure)

    #init the Node Structure for further processing
    #use of a modified offensive ripper for the preprocessing

    def init_calc_structure(self):
        self.calc_structure.defensive_nodes = set(self.Init_Node_Structure.formulae.keys())
        self.calc_structure.offensive_nodes = set(self.Init_Node_Structure.formulae.keys())
        self.calc_structure.Structure_Information = self.Init_Node_Structure.formulae

        #preprocessing of self-attacking nodes
        for self_att_node in self.Init_Node_Structure.self_attacking_nodes:
            self.prepro_offensive_nodes_rem.add(self_att_node)
            #are not actively selected, therefore their attacks cannot be directly erased
            #self.offensive_defense_update_nodes.add(self_att_node)

        #preprocessing of true nodes
        self.true_node_preprocessing(self.Init_Node_Structure.not_attacked_nodes)

        # erase attacks of nodes, which are going to be removed:
        self.attack_defense_relation_handler()

        #apply the changes
        self.apply_and_reset()


    #apply the changes and set everything back to the original state
    def apply_and_reset(self):
        #apply changes to the preprocessed calc structure
        for node in self.prepro_offensive_nodes_rem:
            if node in self.calc_structure.offensive_nodes:
                self.calc_structure.offensive_nodes.remove(node)

        for node in self.prepro_defensive_nodes_rem:
            if node in self.calc_structure.defensive_nodes:
                self.calc_structure.defensive_nodes.remove(node)

        #set back erase about the nodes, which are removed
        self.prepro_offensive_nodes_rem = set()
        self.prepro_defensive_nodes_rem = set()


    def true_node_preprocessing(self, true_node_set):
        for true_node in true_node_set:  # erase nodes, which are attacked by the nodes, which are always true
            self.calc_structure.interpretations.add(true_node)  # add it to the true interpretations
            self.prepro_offensive_nodes_rem.add(true_node)
            self.prepro_defensive_nodes_rem.add(true_node)
            self.complete_sing_interpretation.add(true_node)

            # all nodes, which are marked for removal, also attacks are marked for removal
            for attacked_node in self.calc_structure.Structure_Information[true_node].offensive:
                self.prepro_offensive_nodes_rem.add(attacked_node)
                self.prepro_defensive_nodes_rem.add(attacked_node)
                self.offensive_defense_update_nodes.add(attacked_node)


    #remove attack dependencies of the nodes which are going to be removed
    def attack_defense_relation_handler(self):
        for node in self.offensive_defense_update_nodes:
            for rel_attack in self.calc_structure.Structure_Information[node].offensive:
                if node in self.calc_structure.Structure_Information[rel_attack].defensive:
                    self.calc_structure.Structure_Information[rel_attack].defensive.remove(node)
                    node_def_re_evaluate(self.calc_structure.Structure_Information[rel_attack])
        #set back the used set
        self.offensive_defense_update_nodes = set()

    #fixpoint procedure till no new nodes are found anymore
    def init_cycling(self):
        new_true_nodes = []
        self.nodes_to_be_evaluated = self.calc_structure.offensive_nodes.intersection(self.calc_structure.defensive_nodes)

        for node in self.nodes_to_be_evaluated:
            if self.calc_structure.Structure_Information[node].number_is_defensive == 0:
                new_true_nodes.append(node)
        if new_true_nodes == []:
            return 0

        #append the new nodes
        self.true_node_preprocessing(new_true_nodes)

        #erase attacks and apply changes
        self.attack_defense_relation_handler()
        self.apply_and_reset()

        return 1


if __name__ == "__main__":
    Semantics_Dealer()
