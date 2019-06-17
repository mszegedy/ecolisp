import sys       # For the various sys.exit() commands
import itertools # Needed for powerset() in Part 2.2

### PART 1: STORE THE FILE IN NESTED CMDBLOCKS ###
class cmdblock:
    '''A non-evaluated block consisting of a command word and a list of arguments.'''
    def __init__(self,cmdword):
        self.cmdword = cmdword
        self.args = []
    def __repr__(self):
        return self.cmdword+self.args.__repr__()
    def appendarg(self,arg):
        self.args.append(arg)
def charkind(char):
    '''Tells whether a char is a data character, a whitespace character, or miscellaneous, and returns 'data', 'ws', or 'misc' appropriately.'''
    if char in ' \t\n':
        return 'ws'
    elif char in '+-?!abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890':
        return 'data'
    else:
        return 'misc'
try:
    infile = open('in.ecolisp')
except IOError:
    print 'Error: the input file "in.ecolisp" does not exist. Are you sure you made one?'
    sys.exit()
prevchar    = '' # What was the previous character that was processed?
mode        = '' # The mode that the interpreter is processing words with; possible values are 'cmd' and 'data'
cmds        = [] # The list of command blocks that are currently being constructed (this is in fact the representation of the whole program while it is still under construction)
word        = '' # A command or data word that is currently being constructed
for line in infile:
    for char in line:
        if charkind(char) == 'ws':
            if charkind(prevchar) == 'data':
                if mode == 'cmd':
                    mode = 'data'
                    cmds.append(cmdblock(word))
                    word = ''
                elif mode == 'data':
                    cmds[-1].appendarg(word)
                    word = ''
        elif char == '(':
            if prevchar == '\'':
                cmds.append(cmdblock('\''))
                mode = 'data'
            else:
                mode = 'cmd'
        elif char == ')':
            if charkind(prevchar) == mode: # True when they're both 'data'
                cmds[-1].appendarg(word)
            try:
                cmds[-2].appendarg(cmds.pop()) # This is magic and works. Do not try this with augmented assignment, because Python is stupid and does those differently.
            except IndexError:
                break
            mode = 'data'
        elif charkind(char) == 'data':
            if charkind(prevchar) == 'data':
                word += char
            else:
                word = char
        else:
            print 'Illegal character in file:',char
            infile.close()
            sys.exit()
        prevchar = char
program = cmds # program gets declared here!
if len([x for x in program if x == 'digest']) > 1 or len([x for x in program if x == 'make']) > 1 or len([x for x in program if x == 'produce']) > 1:
    print 'Error: badly formed program structure (too many top-level statements of one kind)'
    sys.exit()
# Cleanup:
infile.close()
del cmds
### PART 2: INTERPRET THE FILE ###
'''
print 'DNA:'    
for enzyme in enzymes:
    if enzyme == 'exoglucanase':
        print 'Part:BBa_K118022:\n (protein coding sequence)\n cex coding sequence encoding Cellulomonas fimi exoglucanase\n http://parts.igem.org/Part:BBa_K118022'
    elif enzyme == 'B-glucosidase':
        print 'Part:BBa_K118028:\n (protein coding sequence)\n beta-glucosidase gene bglX (chu_2268) from Cytophaga hutchinsonii\n http://parts.igem.org/Part:BBa_K118028'
    elif enzyme == 'endoglucanase-A':
        print 'Part:BBa_K118023:\n (protein coding sequence)\n cenA coding sequence encoding Cellulomonas fimi endoglucanase A\n http://parts.igem.org/Part:BBa_K118023'
    elif enzyme == 'B-hydroxy-butyryl-coA-dehydrogenase':
        print 'Part:BBa_I725011:\n (protein coding sequence)\n B-hydroxy butyryl coA dehydrogenase\n http://parts.igem.org/Part:BBa_I725011'
    elif enzyme == 'enoyl-coA-hydratase':
        print 'Part:BBa_I725012:\n (protein coding sequence)\n Enoyl-coA hydratase'
    elif enzyme == 'butyryl-coA-dehydrogenase':
        print 'Part:BBa_I725013:\n (protein coding sequence)\n Butyryl CoA dehydrogenase\n http://parts.igem.org/Part:BBa_I725013'
    elif enzyme == 'butyraldehyde-dehydrogenase':
        print 'Part:BBa_I725014:\n (protein coding sequence)\n Butyraldehyde dehydrogenase\n http://parts.igem.org/Part:BBa_I725014'
    elif enzyme == 'butanol-dehydrogenase':
        print 'Part:BBa_I725015:\n (protein coding sequence)\n Butanol dehydrogenase\n http://parts.igem.org/Part:BBa_I725015'
'''
## Part 2.1: Find out what conditions the program relies on (basically all the (existsp) statements)
def traceconds(block):
    conditions = set([])
    if block.cmdword == 'existsp':
        for arg in block.args:
            if isinstance(arg,str):
                conditions.add(arg)
            else:
                print 'Error: (existsp) doesn\'t take expressions as arguments (sorry)' # Fix this; it's deplorable
                sys.exit()
    else:
        for arg in block.args:
            if isinstance(arg,cmdblock):
                conditions.update(traceconds(arg))
    return conditions
conditions = set([])
for block in program:
    conditions.update(traceconds(block))
## Part 2.2: Find out what combination of translated enzymes each combination of compounds corresponds to
def powerset(iterable):
    '''powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)'''
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))
def evaluate(block,env):
    '''Take in a command block, and evaluate it Lisp-style, returning a symbol'''
    if isinstance(block,str):
        return block
    elif isinstance(block,cmdblock):
        if block.cmdword == 'existsp':
            retval = 't'
            for arg in block.args:
                if isinstance(arg,cmdblock):
                    arg = evaluate(arg,env)
                if not arg in env:
                    retval = 'nil'
            return retval
        elif block.cmdword == 'if':
            if len(block.args) != 3:
                print 'Error: (if) must have 3 arguments, with the syntax (if condition true-val false-val)'
                sys.exit()
            else:
                if evaluate(block.args[0],env) != 'nil':
                    return evaluate(block.args[1],env)
                else:
                    return evaluate(block.args[2],env)
        elif block.cmdword == 'cond':
            for index,arg in enumerate(block.args):
                if index == len(block.args)-1:
                    return evaluate(arg,env)
                else:
                    if not isinstance(arg,cmdblock):
                        print 'Error: (cond) takes only "lists" (not exactly) as arguments'
                        sys.exit()
                    elif len(arg.args) != 1:
                        print 'Error: (cond)\'s arguments must consist of a condition followed by a return value'
                        sys.exit()
                    else:
                        if evaluate(arg.cmdword,env) != 'nil':
                            return evaluate(arg.args[0],env)
        elif block.cmdword == 'and':
            if not len(block.args) == 2:
                print 'Error: (and) must have 2 arguments'
                sys.exit()
            else:
                if block.args[0] != 'nil' and block.args[1] != 'nil':
                    return 't'
                else:
                    return 'nil'
        elif block.cmdword == 'or':
            if not len(block.args) == 2:
                print 'Error: (or) must have 2 arguments'
            else:
                if block.args[0] == 'nil' and block.args[1] == 'nil':
                    return 'nil'
                else:
                    return 't'
def producttoenzymes(product):
    '''Takes a product string, and returns a set of enzymes that are needed to make the product.'''
    if product == 'butanol':
        return set(('B-hydroxy-butyryl-coA-dehydrogenase','enoyl-coA-hydratase','butyryl-coA-dehydrogenase','butyraldehyde-dehydrogenase','butanol-dehydrogenase'))
    elif product == 'D-glucose':
        return set(('exoglucanase','B-glucosidase','endoglucanase-A'))
    else:
        print 'Error: a product you want to make is not in the database. Sorry.'
        sys.exit()
def substratetoenzymes(substrate):
    '''Takes a product string, and returns a set of enzymes that are needed to make the product.'''
    if substrate == 'aceto-acetyl-coA':
        return set(('B-hydroxy-butyryl-coA-dehydrogenase',
                            'enoyl-coA-hydratase',
                'butyryl-coA-dehydrogenase',
                'butyraldehyde-dehydrogenase',
                'butanol-dehydrogenase'))
    elif substrate == 'cellulose':
        return set(('exoglucanase',
                'B-glucosidase',
                'endoglucanase-A'))
    elif substrate == 'cellulobiose':
        return set(('B-glucosidase',))
    else:
        print 'Error: a substrate you want to digest is not in the database. Sorry.'
        sys.exit()
envs = dict((tuple(env),set([])) for env in tuple(powerset(conditions))) # Put in a tuple of molecules, get out the enzymes that those molecules should induce to be transcribed
enzymes = set([]) # The set of possible enzymes that the program can return
for env in envs:
    for block in program:
        if block.cmdword == 'make':
            for arg in block.args:
                envs[env].add(evaluate(arg,env))
                enzymes.update(envs[env]) # Faster than enzymes.add(evaluate(arg,env))
        elif block.cmdword == 'produce':
            for arg in block.args:
                envs[env].update(set(producttoenzymes(evaluate(arg,env))))
                enzymes.update(envs[env])
        elif block.cmdword == 'digest':
            for arg in block.args:
                envs[env].update(set(substratetoenzymes(evaluate(arg,env))))
                enzymes.update(envs[env])
# Cleanup:
del program # All our information is now in envs and enzymes
## Part 2.3: Break envs up into a few smaller problems based on independence of a particular enzyme of a particular condition
dependences = {} # Put in an enzyme, get out the set of conditions that the enzyme depends on
for enzyme in enzymes:
    dependences[enzyme] = set([])
    for condition in conditions:
        if not ([(enzyme in env) for env in envs if condition in envs] == [(enzyme in env) for env in envs if not condition in envs]): # Oh my god... in English, "if the enzyme is independent of the condition"
            dependences[enzyme].add(condition)
# Cleanup:
del enzymes # We can get the same thing by looping over the keys of dependences
### PART 3: COME UP WITH THE DNA SEQUENCES ###
## Part 3.1: Classify the relationships of particular enzymes to their conditions (basically just turn conditions into a more sophisticated object)
def listtokey(l):
    key = ''
    for item in l:
        if item:
            key += 't'
        else:
            key += 'f'
    return key
class relationship:
    '''Holds a logical relationship between an enzyme and its conditions.'''
    def __init__(self,conditions):
        self.kind = None
        self.conditions = conditions
        self.size = len(conditions)
        self.truthtable = {}
    def makekind(self):
        if self.size == 0:
            kind = 'ALWAYS-ON'
        elif self.size == 1:
            if self.truthtable == {listtokey([True]):True,listtokey([False]):False}:
                kind = 'INDUCED'
            elif self.truthtable == {listtokey([True]):False,listtokey([False]):True}:
                kind = 'REPRESSED'
            else:
                kind = 'CONFUSED'
        elif self.size == 2:
            if self.truthtable == {listtokey([True,True]):True,listtokey([True,False]):False,listtokey([False,True]):False,listtokey([False,False]):False}:
                kind = 'AND'
            elif self.truthtable == {listtokey([True,True]):True,listtokey([True,False]):True,listtokey([False,True]):True,listtokey([False,False]):False}:
                kind = 'OR'
            elif self.truthtable == {listtokey([True,True]):False,listtokey([True,False]):False,listtokey([False,True]):False,listtokey([False,False]):True}:
                kind = 'NAND'
            elif self.truthtable == {listtokey([True,True]):False,listtokey([True,False]):True,listtokey([False,True]):True,listtokey([False,False]):True}:
                kind = 'NOR'
            elif self.truthtable == {listtokey([True,True]):True,listtokey([True,False]):False,listtokey([False,True]):False,listtokey([False,False]):True}:
                kind = 'XNOR'
            elif self.truthtable == {listtokey([True,True]):False,listtokey([True,False]):True,listtokey([False,True]):True,listtokey([False,False]):False}:
                kind = 'XOR'
            elif self.truthtable == {listtokey([True,True]):True,listtokey([True,False]):True,listtokey([False,True]):True,listtokey([False,False]):True} or self.truthtable == {listtokey([True,True]):False,listtokey([True,False]):False,listtokey([False,True]):False,listtokey([False,False]):False}:
                kind = 'CONFUSED'
            else:
                kind = 'DIFFICULT'
        else:
            print 'Error: AUGHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH' # Feature, not bug
            sys.exit()
        if kind == 'CONFUSED':
            print 'Error: the algorithm that assigns logical relationships between enzymes and signaling molecules got confused and screwed up. I\'m really sorry about that!'
            sys.exit()
        elif kind == 'DIFFICULT':
            print 'Error: the problem requires parts that do not exist. Sorry.'
            sys.exit()
def multiand(args):
    '''Takes all the args in args and ands them together, and returns the result. args should be an iterable.'''
    retval = True
    for arg in args:
        retval = retval and arg
    return retval
def multior(args):
    '''Takes all the args in args and ors them together, and returns the result. args should be an iterable.'''
    retval = False
    for arg in args:
        retval = retval or arg
    return retval
relationships = {} # Put in an enzyme, get out a relationship
for enzyme,enzconditions in dependences.iteritems():
    enzconditions = tuple(enzconditions)
    relationships[enzyme] = relationship(enzconditions)
    truthlist = []
    for enzenv in tuple(powerset(enzconditions)):
        for enzcondition in enzconditions:
            truthlist.append(enzcondition in enzenv)
        relationships[enzyme].truthtable[listtokey(truthlist)] = [(enzyme in env) for env in envs if multiand([(truthlist[index] == (enzcondition in env) for index,enzcondition in enumerate(enzconditions))])][0] # Just... fuck it
        relationships[enzyme].makekind()
        truthlist = []
## Part 3.2: Print out beautiful DNA
for enzyme,relationship in relationships.iteritems():
    if relationship.size == 0:
        print 'Part:BBa_J23100\n  (promoter)'
    elif relationship.size == 1:
        if relationship.conditions[0] == 'lead' and kind == 'INDUCED':
            print 'Part:BBa_I721001\n (promoter)'
        elif relationship.conditions[0] == 'copper' and kind == 'INDUCED':
            print 'Part:BBa_I760005\n  (promoter)'
        elif relationship.conditions[0] == 'iron' and kind == 'INDUCED':
            print 'Part:BBa_I765000\n (promoter)'
        else:
            print 'Tough luck. You need a promoter',kind,'by',relationship.conditions[0]+'.'
    elif relationship.size == 2:
        print 'Tough luck. You need a promoter that performs a',kind,',operation on the presence of',conditions[0],'and',conditions[1]+'.'
    print '(the DNA sequence for',enzyme+')'
