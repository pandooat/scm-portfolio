import nbformat as nbf
import os

with open('04_Python_Notebooks/FMCG_Supply_Chain_Analytics_End_to_End.ipynb', 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

def mock_display(df):
    if hasattr(df, 'head'):
        print(df.head(5).to_string())
    else:
        print(df)

env = {'display': mock_display}

for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code':
        print(f"=== Executing Cell {i} ===")
        # Matplotlib non-interactive mode
        cell_source = "import matplotlib\nmatplotlib.use('Agg')\n" + cell.source
        exec(cell_source, env)

print("\nSUCCESS: All cells in FMCG_Supply_Chain_Analytics_End_to_End.ipynb executed without errors!")
