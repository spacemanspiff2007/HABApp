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
import sys
import os
from pathlib import Path

from docutils.parsers.rst import Directive, directives
from docutils import nodes

import functools
import traceback
import subprocess

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
    optional_arguments = 5

    option_spec = {
        'linenos': directives.flag,
        'output_language': directives.unchanged,  # Runs specified pygments lexer on output data
        'hide_code': directives.flag,
        'hide_headers': directives.flag,
        'filename': directives.path,
        'hide_filename': directives.flag,
        'precode': directives.unchanged
    }

    @classmethod
    @PrintException
    def execute_code(cls, code):
        project_folder = Path(__file__).parent.parent.parent

        run = subprocess.run([sys.executable, '-c', code], capture_output=True, cwd=project_folder)
        if run.returncode != 0:
            print(run.stdout.decode())
            print(run.stderr.decode())
            raise ValueError()
        return run.stdout.decode() + run.stderr.decode()


    @PrintException
    def run(self):
        """ Executes python code for an RST document, taking input from content or from a filename
        :return:
        """
        language = self.options.get('language', 'python')
        output_language = self.options.get('output_language', 'none')
        filename = self.options.get('filename')
        code = ''

        if not filename:
            code = '\n'.join(self.content)
        else:
            try:
                with open(filename, 'r') as code_file:
                    code = code_file.read()
                    self.warning('code is %s' % code)
            except (IOError, OSError) as err:
                # Raise warning instead of a code block
                error = 'Error opening file: %s, working folder: %s' % (err, os.getcwd())
                self.warning(error)
                return [nodes.warning(error, error)]

        output = []

        # Show the example code
        if 'hide_code' not in self.options:
            shown_code = ''
            hide = False
            for line in self.content:
                if line.replace(' ', '').lower() == '#hide':
                    hide = not hide
                    continue
                if hide:
                    continue
                shown_code += line + '\n'
            shown_code = shown_code.strip('\n').strip()


            input_code = nodes.literal_block(shown_code, shown_code)

            input_code['language'] = language
            input_code['linenos'] = 'linenos' in self.options
            if 'hide_headers' not in self.options:
                suffix = ''
                if 'hide_filename' not in self.options:
                    suffix = '' if filename is None else str(filename)
                output.append(nodes.caption(
                    text='Code %s' % suffix))
            output.append(input_code)

        # Show the code results
        if 'hide_headers' not in self.options:
            output.append(nodes.caption(text='Results'))
        # add precode
        if 'precode' in self.options:
            code = self.options['precode'] + '\n' + code

        code_results = self.execute_code( code)
        for out in code_results.split('\n'):
            if 'Error in ' in out:
                log.error(f'Possible Error in codeblock: {out}')

        code_results = nodes.literal_block(code_results, code_results)

        code_results['linenos'] = 'linenos' in self.options
        code_results['language'] = output_language
        output.append(code_results)
        return output


def setup(app):
    """ Register sphinx_execute_code directive with Sphinx """
    app.add_directive('execute_code', ExecuteCode)
    return {'version': '0.1'}
