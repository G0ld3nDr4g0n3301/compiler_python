from enum import Enum, auto
from dataclasses import dataclass

class OpCode(Enum):
    CONST = auto()
    ASSIGN = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTEQ = auto()
    GT = auto()
    GTEQ = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    JMP = auto()
    JMP_IF_FALSE = auto()
    LABEL = auto()
    CALL = auto()
    PARAM = auto()
    RET = auto()
    PRINT = auto()
    FUNC_START = auto()
    FUNC_END = auto()

@dataclass
class LLMRInstruction:
    op: OpCode
    result: str = ""
    arg1: str = ""
    arg2: str = ""

class LLMRProgram:
    def __init__(self):
        self.instructions: list[LLMRInstruction] =[]

    def print_program(self):
        for inst in self.instructions:
            if inst.op in (OpCode.LABEL, OpCode.FUNC_START, OpCode.FUNC_END):
                print()
                if inst.op == OpCode.FUNC_START:
                    print(f"FUNCTION {inst.arg1}:")
                elif inst.op == OpCode.FUNC_END:
                    print("END_FUNCTION")
                else:
                    print(f"{inst.arg1}:")
                continue

            op_name = inst.op.name.ljust(10)
            res = f"{inst.result} = " if inst.result else ""
            arg1 = inst.arg1 if inst.arg1 else ""
            arg2 = f" {inst.arg2}" if inst.arg2 else ""
            
            print(f"  {op_name}{res}{arg1}{arg2}")
