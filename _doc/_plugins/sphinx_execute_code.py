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
from docutils.parsers.rst import Directive, directives
from docutils import nodes

from io import StringIO


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
    def execute_code(cls, code):
        """ Executes supplied code as pure python and returns a list of stdout, stderr
        Args:
            code (string): Python code to execute
        Results:
            (list): stdout, stderr of executed python code
        Raises:
            ExecutionError when supplied python is incorrect
        Examples:
            >>> execute_code('print "foobar"')
            'foobar'
        """

        output = StringIO()
        err = StringIO()

        sys.stdout = output
        sys.stderr = err

        try:
            # pylint: disable=exec-used
            exec(code)
        # If the code is invalid, just skip the block - any actual code errors
        # will be raised properly
        except TypeError:
            pass
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        results = list()
        results.append(output.getvalue())
        results.append(err.getvalue())
        results = ''.join(results)

        return results

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
        if filename:
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
            input_code = nodes.literal_block(code, code)

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
        code_results = nodes.literal_block(code_results, code_results)

        code_results['linenos'] = 'linenos' in self.options
        code_results['language'] = output_language
        output.append(code_results)
        return output


def setup(app):
    """ Register sphinx_execute_code directive with Sphinx """
    app.add_directive('execute_code', ExecuteCode)
    return {'version': '0.1'}
