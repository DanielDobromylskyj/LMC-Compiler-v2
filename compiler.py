class Variable:
    def __init__(self, name, variableType, value):
        self.name = name
        self.type = variableType
        self.value = value

        self.size = 1 if variableType == 'int' else len(value)


def getDatatype(value):
    if value.isnumeric():
        return "int"
    else:
        raise TypeError("Unknown Datatype: " + value)


def operationSplit(data: list, char):
    output = []
    for item in data:
        if char in item:
            segments = item.split(char)
            for segment in segments:
                output.append(segment)
                output.append(char)
            output.pop(-1)  # remove extra char
        else:
            output.append(item)

    return output


class Program:
    def __init__(self, programCode):
        self.code = programCode
        self.lineNumber = 0

        self.locationStack = []
        self.variables = {}
        self.program = []

        self.compile()

    def compile(self):
        for line in self.code.split("\n"):
            self.parseLine(line.lstrip(" "))
            self.lineNumber += 1

        self.program.append(0)
        self.createVariableCode()
        self.DATify()

    def createVariableCode(self):
        lengthOfProgram = len(self.program)
        freeMemoryPointer = 0

        variableCode = []
        for variable in self.variables.values():  # Todo - ADD STRING SUPPORT
            variablePointer = lengthOfProgram + freeMemoryPointer

            if variable.type == "int":
                variableCode.append(variable.value)

                for line, instruction in enumerate(self.program):
                    if type(instruction) == int:
                        self.program[line] = instruction


                    elif (len(instruction) == 2) and (type(instruction) is list):
                        if instruction[1] == variable.name:  # [Code, variable]
                            self.program[line] = (instruction[0] * 100) + variablePointer


                    elif (len(instruction) == 3) and (type(instruction) is list):  # [Code, "CONST", value]
                        raise NotImplementedError("Constants are not supported yet")



            else:
                raise NotImplementedError("Can't Allocate Memory For Variable Of Type: " + variable.type)

            freeMemoryPointer += variable.size

        self.program.extend(
            variableCode
        )

    def createVariable(self, line):
        _, name, __, value = line.split(" ")

        if name in self.variables:
            raise NameError(f"[Line {self.lineNumber}] Variable already exists")
        else:
            self.variables[name] = Variable(name, getDatatype(value), value)

    def performMaths(self, line):
        outputVariable, operation = line[4:].lstrip(" ").split("=")
        outputVariable = outputVariable.rstrip(" ")
        operation = [operation.replace(" ", "")]

        validOperators = "+-"  # TODO - * and /
        for operator in validOperators:
            operation = operationSplit(operation, operator)

        self.program.extend([
            [5, outputVariable],  # LOAD
            [1, operation.pop(0)],  # ADD
            [3, outputVariable],  # STORE
        ])

        lastVariable = outputVariable
        for i in range(((len(operation)) // 2)):
            operator = operation[i * 2]
            variable = operation[i * 2 + 1]

            if operator == "+":
                self.program.extend([
                    [5, lastVariable],  # LOAD
                    [1, variable],  # ADD
                    [3, lastVariable],  # STORE
                ])

            elif operator == "-":
                self.program.extend([
                    [5, lastVariable],  # LOAD
                    [2, variable],  # SUB
                    [3, lastVariable],  # STORE
                ])

            else:
                raise NameError(f"[Line {self.lineNumber}] Unknown Operator {operator}")


        if outputVariable not in self.variables:
            self.createVariable(f"VAR {outputVariable} = 0")

        self.program.extend([
            [3, outputVariable]
        ])

    def outputVariable(self, line):
        self.program.extend([
            [5, line.split(" ")[1]],
            902
        ])


    def parseLine(self, line):
        if line.startswith("VAR "):
            self.createVariable(line)

        if line.startswith("MATH "):
            self.performMaths(line)

        if line.startswith("VAROUT "):
            self.outputVariable(line)

    def DATify(self):
        for i, line in enumerate(self.program):
            self.program[i] = f"DAT {line}"

    def export(self):
        print("\n".join(self.program))


if __name__ == "__main__":
    code = """
    VAR a = 4
    VAR b = 2
    
    MATH c = a + b - a + a
    VAROUT c
    
    """

    program = Program(code)
    program.export()
