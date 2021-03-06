from latex2ast import converter
#from latex2ast import ast

to_read = {'simple_superscript' : 'super %s ',
                'comp_superscript' : 'super %s endsuper ',
                'simple_subscript' : 'sub %s ',
                'comp_subscript' : 'sub %s %endsub ',
                'simple_frac' : '%s over %s ',
                'comp_frac' : 'fraction %s over %s endfraction ',
                'simple_sqrt' : 'squarerootof %s ',
                'comp_sqrt' : 'squarerootof %s endroot ',
                'simple_root' : 'root %s of %s ',
                'comp_root' : 'root %s of %s endroot ',
                'simple_choose' : 'from %s choose %s ',
                'comp_choose' : 'from %s choose %s end ',
                'simple_modulo' : 'modulo %s ',
                'comp_modulo' : 'modulo %s end ',
                'simple_text' : 'text %s ',
                'comp_text' : 'text %s endtext ',
                'from_to' : 'from %s to %s of ',
                'over' : 'over %s of ',
                'to' : 'to %s of '}

def literal_read(Node):
    #Dictionary with the possible nodes with children and the functions each case call.
    with_children = {'block' : literal_read_block,
                     'fraction' : literal_read_fraction,
                     'root' : literal_read_root,
                     'choose' : literal_read_choose_binom,
                     'binom' : literal_read_choose_binom,
                     'pmod' : literal_read_pmod,
                     'text' : literal_read_text,
                     'label' : literal_read_label}

    str_literal_read = ''

    #The attributes will be readed in this order:
    # accent -> content-> children* -> style -> superscript -> subscript
    #TODO: Add the option for the user to change this.

    #TODO: Add the translation by dictionary.




    #I'll go for the easiest and less elegant way: A chain of ifs.
    if(Node.accent != None):
        str_literal_read = str_literal_read + '%s '%Node.accent

    if(Node.content in with_children):
        #Identify the type of children the node has and act accordingly
        str_literal_read = str_literal_read + with_children[Node.content](Node.children)
    else:
        str_literal_read = str_literal_read + '%s '%Node.content

    if(Node.style != None):
        str_literal_read = str_literal_read + Node.style

    #This part is to read the limits of large Operators like integral or sum.
    if(Node.kind == 'LargeOperators'):
        if(Node.subscript != None and Node.superscript != None):
            str_literal_read = str_literal_read + to_read['from_to']%(literal_read(Node.subscript[0]),
                                                                    literal_read(Node.superscript[0]))
        elif(Node.subscript != None and Node.superscript == None):
            str_literal_read = str_literal_read + to_read['over']%literal_read(Node.subscript[0])

        elif(Node.subscript == None and Node.superscript != None):
            str_literal_read = str_literal_read + to_read['to']%literal_read(Node.superscript[0])

    else:
        if(Node.superscript != None):
            str_literal_read = str_literal_read + literal_read_superscript(Node.superscript[0])

        if(Node.subscript != None):
            str_literal_read = str_literal_read + literal_read_subscript(Node.subscript[0])

    if(not is_simple(Node) and Node.accent != None):
        str_literal_read  = str_literal_read + 'end%s '%Node.accent

    return str_literal_read
#EndOfFunction


def literal_read_superscript(node_script):
    #Here if the script is a block it will be considered as a compound script.
    #This to avoid the following ambiguity: a^{b_c} and a^b_c
    #That would be readed equals.
    if(is_simple(node_script) and node_script.content != 'block'):
        return to_read['simple_superscript']%literal_read(node_script)
    else:
        return to_read['comp_superscript']%literal_read(node_script)
#EndOfFunction

def literal_read_subscript(node_script):
    #See literal_read_superscript.
    if(is_simple(node_script) and node_script.content != 'block'):
        return to_read['simple_subscript']%literal_read(node_script)
    else:
        return to_read['comp_subscript']%literal_read(node_script)
#EndOfFunction

def is_simple(Node):
    bool_it_is = True #It is innocent by the moment.
    with_children = ['fraction',
                     'root',
                     'choose',
                     'binom',
                     'pmod' ,
                     'text',
                     'label']
    if(Node.content in with_children):
        bool_it_is = False
    elif(Node.content == 'block' and len(Node.get_children()) > 1):
        bool_it_is = False
    else:
        bool_it_is = True #Redundant but safe.
    return bool_it_is
#EndOfFunction

def literal_read_block(list_children):
    # The child of a block is a formula, a formula is a list of nodes.
    str_result = ''
    for node in list_children:
        str_result = str_result + literal_read(node)

    return str_result
#EndOfFunction

def literal_read_fraction(list_children):
    #The list received here must be of lenght 2. The numerator and denominator.
    if(is_simple(list_children[0]) and is_simple(list_children[1])):
        return to_read['simple_frac']%(literal_read(list_children[0]), literal_read(list_children[1]))
    else:
        return to_read['comp_frac']%(literal_read(list_children[0]), literal_read(list_children[1]))
#EndOfFunction

def literal_read_root(list_children):
    #There are two cases here: Either the root has an index \sqrt[i]{k} or not.
    if(len(list_children) == 1):#It has not index
        if(is_simple(list_children[0])):
            return to_read['simple_sqrt']%(literal_read(list_children[0]))
        else:
            return to_read['comp_sqrt']%(literal_read(list_children[0]))
    else:
        if(is_simple(list_children[1])):
            return to_read['simple_root']%(literal_read(list_children[0]), literal_read(list_children[1]))
        else:
            return to_read['comp_root']%(literal_read(list_children[0]), literal_read(list_children[1]))
#EndOfFunction

def literal_read_choose_binom(list_children):
    if(is_simple(list_children[0]) and is_simple(list_children[1])):
        return to_read['simple_choose']%(literal_read(list_children[0]), literal_read(list_children[1]))
    else:
        return to_read['comp_choose']%(literal_read(list_children[0]), literal_read(list_children[1]))
#EndOfFunction

def literal_read_pmod(list_children):
    if(is_simple(list_children[0])):
        return to_read['simple_modulo']%(literal_read(list_children[0]))
    else:
        return to_read['comp_modulo']%(literal_read(list_children[0]))
#EndOfFunction

def literal_read_text(list_children):
    return 'text %s endtext'%(list_children)#Here the child is a string
#EndOfFunction

def literal_read_label(list_children):
    return r'\%s'%(list_children)#The labels must be inaltered.
#EndOFFunction

def literal_read_formula(list_formula):
    str_result = ''
    for node in list_formula:
        str_result = str_result + literal_read(node)
    return str_result
#EndOfFunction

if __name__ == "__main__":
    while True:
        try:
            try:
                s = raw_input()
            except NameError: # Python3
                s = input('spi> ')

            cv_s = converter.latex2list(s)
            print(literal_read_formula(cv_s))
        except EOFError:
            break
