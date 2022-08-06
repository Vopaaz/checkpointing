from IPython.core.magic import magics_class, cell_magic, Magics

@magics_class
class CellCheckpoint(Magics):
    
    @cell_magic
    def cell_checkpoint(self, line, cell):
        res = self.shell.run_cell(cell)
