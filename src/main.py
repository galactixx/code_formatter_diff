from rich.markdown import Markdown
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from pathlib import Path
import autopep8
import difflib
import click
import os

from src.mutually_exclusive import MutuallyExclusiveOption
    
@click.command()
@click.option('--py-file',
              cls=MutuallyExclusiveOption,
              help='The name of the py file.',
              mutually_exclusive=['path'],
              type=click.Path(exists=True))
@click.option('--path',
              cls=MutuallyExclusiveOption,
              help='The name of the path that contains py files.',
              mutually_exclusive=['py_file'],
              type=click.Path(exists=True))
@click.option('--max-line-length',
              help='The maximum number of characters in a line of code.',
              type=int,
              default=79)
@click.option('--aggresiveness',
              help='The degree of aggresiveness when formatting code.',
              type=int,
              default=1)
def cli(py_file: str, path: str, max_line_length: int, aggresiveness: int) -> None:
    console = Console()
    file_list = []
    if not py_file and not path:
        console.print(Markdown('**Error**: *Path or py file must be specified. Please try again*'))
        return
    if py_file:
        if Path(py_file).suffix[1:] != 'py':
            console.print(Markdown('**Error**: *File specified is not a py file, please try again and specify a py file*'))
            return
        file_list.append(py_file)
    else:
        py_files = [os.path.join(path, i) for i in os.listdir(path) if 
                    not os.path.isdir(os.path.join(path, i)) and Path(i).suffix[1:] == 'py']
        if not file_list:
            console.print(Markdown('**Error**: *There are no py files in specified path, try again and specify path with py files.*'))
            return
        file_list.extend(py_files)
    for file in file_list:
        with open(file, 'r') as f:
            code = f.read()
        formatted_code = autopep8.fix_code(code, options={'aggressive': aggresiveness,
                                                          'max_line_length': max_line_length})

        # calculate delta of both files
        diff = difflib.unified_diff(a=code.splitlines(), b=formatted_code.splitlines())
        diff = '\n'.join(diff)

        if formatted_code == code:
            console.print(Markdown('**There were no changes to be made after re-formatting**'))
            continue

        # output diff to console
        syntax = Syntax(diff, "diff", theme="monokai", line_numbers=True)
        panel = Panel(syntax, title=file, padding=0)
        console.print(panel)

        # prompt the user
        response = input(f"Do you want to make these changes to {file}? (y/n): ")

        # check the response
        if response.lower() == 'y':

            # make changes to file
            with open(file, 'w') as f:
                f.write(formatted_code)
            console.print(Markdown(f"**Changes {file} were made**"))
        else:
            console.print(Markdown(f"**Changes to {file} were not made**"))

if __name__ == '__main__':
    cli()