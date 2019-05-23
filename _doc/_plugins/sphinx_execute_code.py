#!/usr/bin/env/python
"""
This is a fork from sphinx-execute-code

Available options:
        'linenos': directives.flag,
        'output_language': directives.unchanged,
        'hide_code': directives.flag,
        'hide_headers': directives.flag,
        'filename': directives.path,
        'hide_filename': directives.flag,
        'hide_filename': directives.flag,
        'precode': directives.unchanged,
Usage:
.. example_code:
   :linenos:
   :hide_code:
   print 'Execute this python code'
"""
import functools
import subprocess
import sys
import traceback
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util import logging

log = logging.getLogger(__name__)


def PrintException( func):

    @functools.wraps(func)
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("{}\n{}".format( e, traceback.format_exc()))
            raise
    return f


class ExecuteCode(Directive):
    """ Sphinx class for execute_code directive
    """
    has_content = True
    required_arguments = 0
    optional_arguments = 6

    option_spec = {
        'linenos': directives.flag,
        'output_language': directives.unchanged,  # Runs specified pygments lexer on output data
        'hide_code': directives.flag,
        'hide_output': directives.flag,
        'header_code': directives.unchanged,
        'header_output': directives.unchanged,
    }

    @PrintException
    def run(self):
        """ Executes python code for an RST document, taking input from content or from a filename
        :return:
        """
        language = self.options.get('language', 'python')
        output_language = self.options.get('output_language', 'none')

        output = []

        shown_code = ''
        executed_code = ''

        hide = False
        skip = False
        for line in self.content:
            line_switch = line.replace(' ', '').lower()
            if line_switch == '#hide':
                hide = not hide
                continue
            if line_switch == '#skip':
                skip = not skip
                continue

            if not hide:
                shown_code += line + '\n'
            if not skip:
                executed_code += line + '\n'

        shown_code = shown_code.strip()

        # Show the example code
        if 'hide_code' not in self.options:
            input_code = nodes.literal_block(shown_code, shown_code)

            input_code['language'] = language
            input_code['linenos'] = 'linenos' in self.options
            if 'header_code' in self.options:
                output.append(nodes.caption(text=self.options['header_code']))
            output.append(input_code)

        # Show the code results
        if 'header_output' in self.options:
            output.append(nodes.caption(text=self.options['header_output']))

        code_results = execute_code( executed_code).strip()
        for out in code_results.split('\n'):
            if 'Error in ' in out:
                log.error(f'Possible Error in codeblock: {out}')

        code_results = nodes.literal_block(code_results, code_results)

        code_results['linenos'] = 'linenos' in self.options
        code_results['language'] = output_language
        output.append(code_results)
        return output


WORKING_DIR = None


@PrintException
def execute_code(code) -> str:

    run = subprocess.run([sys.executable, '-c', code], capture_output=True, cwd=WORKING_DIR)
    if run.returncode != 0:
        print(run.stdout.decode())
        print(run.stderr.decode())
        raise ValueError()
    return run.stdout.decode() + run.stderr.decode()


def builder_ready(app):
    global WORKING_DIR

    folder = app.config.execute_code_working_dir
    if folder is None:
        WORKING_DIR = folder
        return None

    # Make sure the folder is valid
    if isinstance(folder, str):
        folder = Path(folder)
    else:
        assert isinstance(folder, Path)
    if not folder.is_dir():
        log.error( f'Configuration execute_code_working_dir does not point to a directory: {folder}')
    WORKING_DIR = folder

    # Search for a python package and print a warning if we find none
    # since this is the only reason to specify a working dir
    for f in folder.iterdir():
        if not f.is_dir():
            continue

        # log warning if we don't find a python package
        for file in f.iterdir():
            if file.name == '__init__.py':
                return None

    log.warning(f'No Python package found in {folder}')
    return None


def setup(app):
    """ Register sphinx_execute_code directive with Sphinx """

    app.add_config_value('execute_code_working_dir', None, 'env')

    app.connect('builder-inited', builder_ready)
    app.add_directive('execute_code', ExecuteCode)
    return {'version': '0.2'}
