from binaryninja import *

class Slicer():
    def __init__(self, instruction):    
        self.visited = set()
        self.instruction = instruction
        self.function = instruction.function

    def visit_backward(self, instruction):
        for var in instruction.vars_read:
            if type(var) != mediumlevelil.SSAVariable:
                return
            var_def = self.function.get_ssa_var_definition(var)
            if var_def is not None and var_def not in self.visited:
                self.visited.add(var_def)
                self.visit_backward(self.function[var_def])
    
    def visit_forward(self, instruction):
        for var in instruction.vars_written:
            if type(var) != mediumlevelil.SSAVariable:
                return
            for var_usage in self.function.get_ssa_var_uses(var):
                if var_usage and var_usage not in self.visited:
                    self.visited.add(var_usage)
                    self.visit_forward(self.function[var_usage])


def bw_slice(bv,instruction):
    do_slice(bv, instruction, 'BW')


def fw_slice(bv,instruction):
    do_slice(bv, instruction, 'FW')


def do_slice(bv,instruction, action):
    sl = Slicer(instruction.ssa_form)
    if action == 'BW':
        sl.visit_backward(instruction.ssa_form)
    else:
        sl.visit_forward(instruction.ssa_form)
    print('[Slicer] Visited: ' + ','.join(str(v) for v in sl.visited))
    color = HighlightStandardColor.WhiteHighlightColor
    bv.begin_undo_actions()
    sl.function.source_function.set_user_instr_highlight(instruction.address, color)
    for vr in sl.visited:
        inst = sl.function[vr]
        sl.function.source_function.set_user_instr_highlight(inst.address, color)
    bv.commit_undo_actions()


PluginCommand.register_for_medium_level_il_instruction("BW Slice", "", bw_slice)
PluginCommand.register_for_medium_level_il_instruction("FW Slice", "", fw_slice)
