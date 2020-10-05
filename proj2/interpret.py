import getopt
import sys
import re
import xml.etree.ElementTree as ET

#IPPcode20 - IPP projekt č.2
#Autor - Filip Pospíšil
#xpospi0f@stud.fit.vutbr.cz


# Globální proměnné
source = "stdin";
input = "stdin";
sourcefile = '';
inputfile = [];
instruction_list = list();
labels = [];
frame_global = [];
frame_local = [];
frame_temporary = [];

# Funkce na tisk nápovědy
def napoveda( ):
    print("IPP 2019/2020 - 2. projekt - intepret.py");
    print("Dostupné příkazy:\n");
    print("--help - vypíše tuhle nápovědu\n");
    print("--source=file - vstupní XML soubor s reprezentací zdrojového kódu\n");
    print("--input=file - soubor se vstupy na stdin\n");

# Funkce na kontrolu argumentů, nastavuje vše potřebné pro další intepretaci, v případě, že zjistí, že něco nesedí, ukončuje program.
def check_args( ):
    global source;
    global input;
    argcount = 0;

    try:
        myargs, args = getopt.getopt(sys.argv [1:], "r", ["help", "source=", "input="]);

    except getopt.GetoptError as err:
        print(err);
        exit(10);

    for o, a in myargs:
        if o == "--help":
            argcount = argcount + 1;
            if len(sys.argv) > 2:
                sys.stderr.write("Argument --help nelze kombinovat s dalšími argumenty!\n");
                napoveda();
                exit(10);
            else:
                napoveda();
                exit(0);

        if o in ("--source"):
            argcount = argcount + 1;
            source = a;

        if o in ("--input"):
            argcount = argcount + 1;
            input = a;

        if argcount == 0:
            sys.stderr.write("Nebyl zadan zadny argument, vypisuji napovedu!\n");
            napoveda();
            exit(10);

        # Input a source zustaly nastavene na stdin:
        if sourcefile == "stdin" and inputfile == "stdin":
            exit(10);

# Klasikcý zásobník
class Stack():
    # Vytvoření zásobniku
    def __init__(self):
        self.stack = [];  # Zásobník je na začátku prázdný.

    # Vkládání na zásobník
    def push(self, item):
        self.stack.append(item);

    # Vyhození ze zásobníku
    def pop(self):
        if len(self.stack) == 0:
            print("Prazdny zasobnik!");
            exit(99);
        else:
            return self.stack.pop();

    def isEmpty(self):
        if len(self.stack) == 0:
            return True;
        else:
            return False;

    def get(self):
        return self.stack;

# Třída pro implementaci argumentů
class Argumenty:
    def __init__(self, source, input):
        self.source = source;
        self.input = input;

# Třída pro práci s proměnnými
class Variable:
    def __init__(self, name):
        self.name = name;
        self.value = None;

    def value(self, value, opcode):
        self.value = value;
        self.opcode = opcode;

    def set_value(self, value, opcode):
        self.value = value;
        self.opcode = opcode;

    def get_value(self):
        return self.value;

    def get_opcode(self):
        return self.opcode;

    def get_name(self):
        return self.name;

# Třída zpracovávající instrukce
class Instrukce:
    global xml;

    def __init__(self, instrukce):
        self.name = (instrukce.attrib).get('opcode');  # Získej název instrukce
        self.order = (instrukce.attrib).get('order');  # Získej číslo instrukce

        # Získej argumenty instrukce
        for instruct in xml.findall('instruction'):
            for argument in instruct:
                if not re.match("^arg[1|2|3]$", argument.tag):
                    exit(32);
                if not re.match(r"^\n*\s*$", argument.tail):
                    exit(32);

        self.arg1 = instruct.find("arg1");
        self.arg2 = instruct.find("arg2");
        self.arg3 = instruct.find("arg3");

        Instrukce.setValues(self);

    def setValues(self):
        if self.arg1 is None:
            self.ValueArg1 = None;
        else:
            self.TypeArg1 = self.arg1.attrib.get('type');
            self.ValueArg1 = {self.arg1.attrib.get('type'): self.arg1.text}

        if self.arg2 is None:
            self.ValueArg2 = None;
        else:
            self.TypeArg2 = self.arg2.attrib.get('type');
            self.ValueArg2 = {self.arg2.attrib.get('type'): self.arg2.text}

        if self.arg3 is None:
            self.ValueArg3 = None;
        else:
            self.TypeArg3 = self.arg3.attrib.get('type');
            self.ValueArg3 = {self.arg3.attrib.get('type'): self.arg3.text}

    def instr_name(self):
        return self.name;

    def instr_order(self):
        return self.order;

    def instr_args(self):
        return (self.arg1 + self.arg2 + self.arg3);

    def instr_arg1(self):
        return self.arg1;

    def instr_arg2(self):
        return self.arg2;

    def instr_arg3(self):
        return self.arg3;

    def instr_arg1_value(self):
        return self.ValueArg1;

    def instr_arg2_value(self):
        return self.ValueArg2;

    def instr_arg3_value(self):
        return self.ValueArg3;

    def instr_arg_values(self):
        return (self.ValueArg1, self.ValueArg2, self.ValueArg3);


##########################################
# Kontrola validnosti XML souboru.
##########################################
def check_xml( ):
    global xml;
    cisla_instrukci = [];

    # Kontrola, zda obsahuje parametr program.
    if (re.match(r"^program$", xml.tag)):
        pass;

    else:
        exit(31);

    # Obsahuje name/description a language = IPPcode20?
    for name, value in xml.attrib.items():
        if re.match(r"^\n*\s*$", xml.text) or xml.text is None:
            if re.match(r"^name$", name) or re.match(r"^description$", name):
                continue;
            else:
                if re.match(r"^language$", name) and re.match(r"^IPPcode20$", value):
                    continue;
                else:
                    exit(32);
        else:
            exit(32);

    for instruction in xml:
        # Pokračuje instrukce "order" a "opcode"?
        if "order" not in instruction.attrib:
            exit(31);

        if "opcode" not in instruction.attrib:
            exit(31);

        else:
            # Nevyskytují se dvě instrukce se stejným číslem?
            if len(cisla_instrukci) != len(set(cisla_instrukci)):
                exit(31);

            else:
                cisla_instrukci.append(instruction.attrib ['order']);

            # Nemá nějaká instrukce ID menší než 0?
            for x in cisla_instrukci:
                if int(x) <= 0:
                    exit(31);

            for argument in instruction:
                if "type" not in argument.attrib:
                    exit(31);

                # Kontrola validnsoti typu
                if argument.attrib ["type"] not in ["var", "bool", "int", "string", "nil", "label", "type"]:
                    exit(32);

    # Kontrola všech isntruckí
    for instruction in xml.findall("instruction"):
        for argument in instruction:
            # Kontrola validnosti zadaných argumentů
            if re.match("^arg[1|2|3]$", argument.tag):
                pass;
            else:
                exit(32);

            if re.match(r"^\n*\s*$", argument.tail):
                pass;
            else:
                exit(32);


# Funkce zpracovává instrukce jednu po druhé, vrací instrukci, kterou potřebujeme
def get_instructions( ):
    global instruction_list;
    global labels;

    for instr in xml.iter('instruction'):
        actual = Instrukce(instr);
        instruction_list.append(actual)  # insert all instructions into list
        if (actual.instr_name() == 'LABEL'):
            label = actual.instr_arg1_value();
            labels.append((next(iter(label.values())), actual.instr_order()));

    instruction_list.sort(key=lambda x: int(x.order), reverse=False) # Řazení seznamu, viz přednáška


# Jde o promennou?
def checkVariable( ):
    pass;


# def set_type(input):
#     if input.name is None:
#         return input.name
#     elif input.type == "bool" and re.match(r"^(true)$", input.name.lower()):
#         return True
#     elif input.type == "bool" and re.match(r"^(false)$", input.name.lower()):
#         return False
#     elif input.type == "int" and re.match(r"^([-|+]?\d+)$", input.name):
#         return int(input.name)
#     elif input.type == "string" and re.match(r"^(([\w]*(\\\\[0-9]{3})*)*)\S*$", input.name):
#         return input.name


# Jde o symbol?
def checkSymbol(value):
    global frame_global;
    global frame_local;
    global frame_temporary;

    if (re.match(r"^(GF@).*$", value [0:3]) and 'frame_global' not in globals()):
        exit(55);
    elif (re.match(r"^(LF@).*$", value [0:3]) and 'frame_local' not in globals()):
        exit(55);
    elif (re.match(r"^(TF@).*$", value [0:3]) and 'frame_temporary' not in globals()):
        exit(55);

    if (re.match(r"^(GF@).*$", value [0:3])):
        for returnName in frame_global:
            if returnName.get_name() == value:
                return returnName;

    if (re.match(r"^(LF@).*$", value [0:3])):
        if 'frame_local' in globals():
            try:
                frame_local_actual = frame_local [-1];
            except IndexError:
                exit(55);

            for returnName in frame_local:
                if returnName.get_name() == value:
                    return returnName;

    if (re.match(r"^(TF@).*$", value [0:3])):
        if 'frame_temporary' in globals():
            for returnName in frame_temporary:
                if returnName.get_name() == value:
                    return returnName;

    exit(54);


# Jde o cislo?
def checkInt(value):
    try:
        val = int(value);
    except ValueError:
        exit(32);


# Matoucí název, funkce zjišťuje, o jaký druh inputu jde
def checkMath(input):
    if isinstance(input, int):
        return "int";

    elif isinstance(input, bool):
        return "bool";

    elif isinstance(input, str):
        return "string";

    elif re.match(r"^(nil)$", input):
        return "nil";

    else:
        return None;


# Implementace instrukce move
def move(instruction):
    #  TODO NOT FIXED YET!
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    destination = instruction.instr_arg1_value();  # variable

    source = instruction.instr_arg2_value();  # symbol

    variable = checkSymbol(destination.get("var"));  # mame tam opravdu variable?

    if (source.get("var")) == None:  # nic se v podstatě nedějě
        variable.set_value(next(iter(source.values())), list(source.keys()) [0]);
    else:  # prohodit....
        variable2 = checkSymbol(source.get("var"));
        variable.set_value(variable2.get_value(), variable2.get_opcode());

# Implementace instrukce createframe
def createframe(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    if frame_temporary is None:
        frame_temporary = {};
    else:
        frame_temporary.clear();

# Implementace instrukce pushframe
def pushframe(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    if 'frame_local' not in globals():
        frame_local = [];
        exit(55);
    elif 'frame_temporary' not in globals():
        exit(55);
    elif not frame_temporary:
        exit(55);
    else:
        frame_local.append(frame_temporary);
        del frame_temporary;

# Implementace instrukce popframe
def popframe(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    if (not bool(frame_temporary) or frame_temporary) and frame_local:
        frame_temporary = frame_local.pop();
    else:
        exit(55);

# Implementace instrukce defvar
def defvar(instruction, frame_local_actual=None):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;
    # TODO HAZI CHYBU!

    value = instruction.instr_arg1_value().get('var');  # variable

    if value [0:3] == 'GF@':
        for global_frame_variable in frame_global:
            if (global_frame_variable.get_name() == value):
                exit(0);
                # TODO 52
        new = Variable(value);
        frame_global.append(new);


    elif (value [0:3] == 'LF@'):
        if 'frame_local' in globals():
            try:
                frame_local_actual = frame_local [-1];
            except IndexError:
                exit(55);

            for returnName in frame_local:
                if returnName.get_name() == value:
                    exit(52);
                    # TODO 52
        else:
            new = Variable(value);
            frame_local_actual.append(new);
            frame_local [-1] = frame_local_actual;

    elif (value [0:3] == 'TF@'):
        if 'frame_temporary' in globals():
            for returnName in frame_temporary:
                if returnName.get_name() == value:
                    exit(52);
                    # TODO 52
        else:
            exit(55);
        new = Variable(value);
        frame_temporary.append(new);

# Implementace instrukce call
def call(instruction, position):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    label = instruction.instr_arg1_value();

    zasobnik.push(position);
    if label in labels:
        return labels [label];
    else:
        exit(52);
        # TODO 52

# Implementace instrukce returnFCE
def returnFCE(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    if zasobnik.isEmpty():
        exit(56);
    else:
        zasobnik.pop();

# Implementace instrukce pushs
def pushs(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    symbol = checkSymbol((instruction.instr_arg1_value().get("var")));
    zasobnik.push(symbol);

# Implementace instrukce pops
def pops(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    variable_value = checkSymbol(variable.get("var"));

    if zasobnik.isEmpty() == True:
        exit(56);
    else:
        value = zasobnik.pop();

        if isinstance(value, Variable):
            variable_value.set_value(value.get_value(), value.get_opcode());
        else:
            variable_value.set_value(value [next(iter(value))], next(iter(value)));

# Implementace instrukce add
def add(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    valid = False;
    if ((checkMath(symbol1) == "int" and checkMath(symbol2) == "int") or (
            checkMath(symbol1) == "float" and checkMath(symbol2) == "float")):
        valid == True;

    if (valid == True):
        variable.update({instruction.instr_arg1_value() [3:]: symbol1 + symbol2});
    else:
        exit(53);

# Implementace instrukce sub
def sub(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    valid = False;
    if ((checkMath(symbol1) == "int" and checkMath(symbol2) == "int") or (
            checkMath(symbol1) == "float" and checkMath(symbol2) == "float")):
        valid == True;

    if (valid == True):
        variable.update({instruction.instr_arg1_value() [3:]: symbol1 - symbol2});
    else:
        exit(53);

# Implementace instrukce mul
def mul(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    valid = False;
    if ((checkMath(symbol1) == "int" and checkMath(symbol2) == "int") or (
            checkMath(symbol1) == "float" and checkMath(symbol2) == "float")):
        valid == True;

    if (valid == True):
        variable.update({instruction.instr_arg1_value() [3:]: symbol1 * symbol2});
    else:
        exit(53);

# Implementace instrukce idiv
def idiv(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    valid = False;
    if ((checkMath(symbol1) == "int" and checkMath(symbol2) == "int")):
        valid == True;

        if (symbol2 == 0):
            exit(57);  # dělení nulou

    if (valid == True):
        variable.update({instruction.instr_arg1_value() [3:]: symbol1 // symbol2});
    else:
        exit(53);

# Implementace instrukce lt
def lt(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    isItOk = False;

    if ((checkMath(symbol1) == "int" and checkMath(symbol2) == "int") or (
            checkMath(symbol1) == "float" and checkMath(symbol2) == "float") or (
            checkMath(symbol1) == "string" and checkMath(symbol2) == "string") or (
            (checkMath(symbol1) == "bool" and checkMath(symbol2) == "bool"))):
        isItOk = True;
    else:
        exit(53);

    if (isItOk):
        if symbol1 < symbol2:
            variable.update({instruction.instr_arg1_value().get("var"): True});
        else:
            variable.update({instruction.instr_arg1_value().get("var"): False});

# Implementace instrukce gt
def gt(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    isItOk = False;

    if ((checkMath(symbol1) == "int" and checkMath(symbol2) == "int") or (
            checkMath(symbol1) == "float" and checkMath(symbol2) == "float") or (
            checkMath(symbol1) == "string" and checkMath(symbol2) == "string") or (
            (checkMath(symbol1) == "bool" and checkMath(symbol2) == "bool"))):
        isItOk = True;
    else:
        exit(53);

    if (isItOk):
        if symbol1 > symbol2:
            variable.update({instruction.instr_arg1_value().get("var"): True});
        else:
            variable.update({instruction.instr_arg1_value().get("var"): False});

# Implementace instrukce eq
def eq(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    isItOk = False;

    if ((checkMath(symbol1) == "int" and checkMath(symbol2) == "int") or (
            checkMath(symbol1) == "float" and checkMath(symbol2) == "float") or (
            checkMath(symbol1) == "string" and checkMath(symbol2) == "string") or (
            (checkMath(symbol1) == "bool" and checkMath(symbol2) == "bool"))):
        isItOk = True;
    else:
        exit(53);

    if (isItOk):
        if symbol1 == symbol2:
            variable.update({instruction.instr_arg1_value().get("var"): True});
        else:
            variable.update({instruction.instr_arg1_value().get("var"): False});

# Implementace instrukce andFCE
def andFCE(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    if checkMath(symbol1) == "bool" and checkMath(symbol2) == "bool":
        if symbol1 and symbol2:
            variable.update({instruction.instr_arg1_value().get("var"): True});
        else:
            variable.update({instruction.instr_arg1_value().get("var"): False});
    else:
        exit(53);

# Implementace instrukce orFCE
def orFCE(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    if checkMath(symbol1) == "bool" and checkMath(symbol2) == "bool":
        if symbol1 or symbol2:
            variable.update({instruction.instr_arg1_value().get("var"): True});
        else:
            variable.update({instruction.instr_arg1_value().get("var"): False});
    else:
        exit(53);

# Implementace instrukce notFCE
def notFCE(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();

    if checkMath(symbol1) == "bool":
        variable.update({instruction.instr_arg1_value().get("var"): not symbol1});
    else:
        exit(53);

# Implementace instrukce int2char
def int2char(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();

    variable1 = checkMath(symbol1);

    if (variable1 == "int"):
        if 0 <= symbol1 <= 1114111:
            variable.update({instruction.instr_arg1_value().get("var"): chr(symbol1)});
        else:
            exit(58);

# Implementace instrukce stri2int
def stri2int(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    symbol1 = instruction.instr_arg2_value();
    symbol2 = instruction.instr_arg3_value();

    if (checkMath(symbol1) == "string" and checkMath(symbol2) == "int"):
        if (0 <= symbol2 < len(symbol1)):
            variable.update({instruction.instr_arg1_value().get("var"): ord(symbol1 [symbol2 + 1])});
    else:
        quit(58);


def read(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;
    # TODO
    pass;

# Implementace instrukce write
def write(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    variable = instruction.instr_arg1_value();
    print(variable);

# TODO!!
def concat(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def strlen(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def rename1(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def getchar(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def setchar(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def type(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def label(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def jump(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def jumpifeq(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def jumpifneq(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


def exitFCE(instruction):
    global zasobnik;
    global frame_global;
    global frame_temporary;
    global frame_local;

    pass;


# Spuštění celého kolosu.
def RunLikeHell( ):
    global instruction_list;
    actual = 0;

    #Cyklus procházející všechny instrukce.
    while int(actual) < (len(instruction_list)):
        instr = instruction_list [actual];
        argumenty = instr.instr_arg_values();

        #Volání správného návěstí.
        if (instr.instr_name() == "MOVE"):
            move(instr);
        elif (instr.instr_name() == "CREATEFRAME"):
            createframe(instr);
        elif (instr.instr_name() == "PUSHFRAME"):
            pushframe(instr);
        elif (instr.instr_name() == "POPFRAME"):
            popframe(instr);
        elif (instr.instr_name() == "DEFVAR"):
            defvar(instr);
        elif (instr.instr_name() == "CALL"):
            actual = int(call(instr, actual));
        elif (instr.instr_name() == "RETURN"):
            actual = returnFCE(instr);
        elif (instr.instr_name() == "PUSHS"):
            pushs(instr);
        elif (instr.instr_name() == "POPS"):
            pops(instr);
        elif (instr.instr_name() == "ADD"):
            pushs(instr);
        elif (instr.instr_name() == "SUB"):
            pops(instr);
        elif (instr.instr_name() == "MUL"):
            pushs(instr);
        elif (instr.instr_name() == "IDIV"):
            pops(instr);
        elif (instr.instr_name() == "LT"):
            pushs(instr);
        elif (instr.instr_name() == "GT"):
            pops(instr);
        elif (instr.instr_name() == "EQ"):
            pushs(instr);
        elif (instr.instr_name() == "AND"):
            andFCE(instr);
        elif (instr.instr_name() == "OR"):
            orFCE(instr);
        elif (instr.instr_name() == "NOT"):
            notFCE(instr);
        elif (instr.instr_name() == "INT2CHAR"):
            int2char(instr);
        elif (instr.instr_name() == "STRI2INT"):
            stri2int(instr);

        actual = actual + 1;


# Pouze pro testy
def stackTest( ):
    global frame_global;
    global frame_local;
    global zasobnik;
    zasobnik.push("baf");
    print(zasobnik.get());

# Pouze pro testy
def debug( ):
    print("source: " + str(source));
    print("input: " + str(input));
    print("sourcefile: " + str(sourcefile));
    print("inputfile: " + str(inputfile));


check_args();
test = Argumenty(source, input);
checkniTo = ET.parse(source);
xml = checkniTo.getroot();
check_xml();
get_instructions();
zasobnik = Stack();
RunLikeHell();
