"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.Running = True
        self.branch_table = {}
        self.branch_table[0b10000010] = self.LDI
        self.branch_table[0b00000001] = self.HLT
        self.branch_table[0b01000111] = self.PRN

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
                    self.ram_write(address, n)
                    address += 1
        except FileNotFoundError:
            print(f'File not found: "{sys.argv[1]}"')
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.Running:
            self.trace()
            ir = self.branch_table[self.ram_read(self.pc)]
            
            numofoperands = ir()

            self.pc += numofoperands + 0b1
            self.trace()
    def RNOP(self):
        # print('rnop')
        return self.ram[self.pc] >> 0b110
    def ram_read(self, address):
        return self.ram[address]
    
    def ram_write(self, address, data):
        self.ram[address] = data
    def LDI(self):
        self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.pc+2)
        return self.RNOP()
    def HLT(self):
        self.Running = False
        return self.RNOP()
    def PRN(self):
        print(self.reg[self.ram_read(self.pc+1)])
        return self.RNOP()
# 777
# 022
#755