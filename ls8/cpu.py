"""CPU functionality."""

import sys
import copy
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.ram[0xF4] = 0xF4
        self.pc = 0
        self.Running = True
        self.branch_table = {}
        self.branch_table[0b10000010] = self.LDI
        self.branch_table[0b00000001] = self.HLT
        self.branch_table[0b01000111] = self.PRN
        self.branch_table[0b01000101] = self.PUSH
        self.branch_table[0b01000110] = self.POP
        self.branch_table[0b01010000] = self.CALL
        self.branch_table[0b00010001] = self.RET


    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)
        try:
            with open(sys.argv[1]) as program:
                for instruction in program:
                    t = instruction.split('#')
                    n = t[0].strip()

                    if n == '':
                        continue

                    try:
                        n=int(n,2)
                    except ValueError:
                        print(f'Invalid number : "{n}"')
                        sys.exit(1)
                    self.write_ram(address, n)
                    address += 1
        except FileNotFoundError:
            print(f'File not found: "{sys.argv[1]}"')
            sys.exit(2)

    def ALU(self, reg_a, reg_b):
        """ALU operations."""
          
        def ADD():
            self.reg[reg_a] += self.reg[reg_b]
        def SUB():
            self.reg[reg_a] -= self.reg[reg_b]
        def MULT():
            self.reg[reg_a] *= self.reg[reg_b]
        def DIV():
            self.reg[reg_a] /= self.reg[reg_b]
        ALU_branch_table = {
            0b10100000: ADD,
            0b10100001: SUB,
            0b10100010: MULT,
            0b10100011: DIV,
        }
        try:
            op = ALU_branch_table[self.read_ram(self.pc)]
            op()
        except KeyError:
                print(f'Unsupported ALU operation: "{self.read_ram(self.pc),bin(self.read_ram(self.pc))}"')
                sys.exit(2)  

        return self.RNOP()
    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.read_ram(self.pc),
            self.read_ram(self.pc + 0b1),
            self.read_ram(self.pc + 0b10)
        ), end='')

        for i in range(0b1000):
            print(" %02X" % self.read_reg(i), end='')

        print()

    def run(self):
        """Run the CPU."""
        verbose = True
        if verbose == True:
            print('Start --------------------')
            self.trace()
            # x = []
            # for i in self.ram:
            #     x.append(hex(i))
            # print(x)
        while self.Running:
            # self.trace()
            try:
                a = copy.deepcopy(self.read_ram(self.pc)) 
                a &= 0b00100000
                a >>= 5
                # print('a',a)
                if a == 1:
                    ir = self.ALU
                    x,y = self.read_ram(self.pc+0b1),self.read_ram(self.pc+0b10)
                    # print(x,y)
                    numofoperands = ir(x,y)
                else:

                    n = self.read_ram(self.pc)
                    # print('n',n)
                    ir = self.branch_table[n]
                    numofoperands = ir()
                self.pc += numofoperands + 0b1
                # print(self.pc)
                if verbose == True:
                    self.trace()
                    if self.Running == False:
                        print('End --------------------')
            except KeyError:
                print(f'Uknown Instruction: "{a,bin(a)}"')
                sys.exit(2)
    def RNOP(self, setPC = None):
        if setPC == None:
            numofoperands = self.read_ram(self.pc) 
            numofoperands &= 0b11000000 
            numofoperands >>= 6
            return numofoperands
        else:
            return -1
        
    def read_ram(self, address):
        return self.ram[address]
    
    def write_ram(self, address, data):
        self.ram[address] = data
    def write_reg(self, data, regadr=0, ramadr=None):
        if ramadr == None:
            self.reg[regadr] = data
        else:
            self.reg[self.read_ram(ramadr)] = data
    def read_reg(self, regadr=0, ramadr=None):
        if ramadr == None:
            return self.reg[regadr]
        else:
            return self.reg[self.read_ram(ramadr)]
    def LDI(self):
        self.reg[self.read_ram(self.pc+1)] = self.read_ram(self.pc+2)
        return self.RNOP()
    def HLT(self):
        self.Running = False
        return self.RNOP()
    def PRN(self):
        print(self.read_reg(ramadr=self.pc+1))
        return self.RNOP()
    def PUSH(self):
        data = self.read_reg(ramadr=self.pc+1)
        address = self.read_reg(7) - 1
        self.write_ram(address, data)
        self.reg[7]-=1
        return self.RNOP()
    def POP(self):
        address = self.read_reg(7)
        data = self.read_ram(address)
        self.write_reg(data, ramadr=self.pc+1)
        self.reg[7]+=1
        return self.RNOP()
    def push_value(self, value):
        self.reg[7]-=1
        address = self.reg[7]
        self.write_ram(address,value)
    def pop_value(self):
        address = self.reg[7]
        value = self.read_ram(address)
        self.reg[7]+=1
        return value
    def CALL(self):
        return_adr = self.pc+2
        self.push_value(return_adr)
        value = self.read_reg(ramadr=self.pc+1)
        # print(value)
        self.pc = value
        # print(self.pc)
        return self.RNOP(True)
    def RET(self):
        return_adr = self.pop_value()
        self.pc=return_adr
        return self.RNOP(True)