from subprocess import Popen, PIPE, TimeoutExpired
from pathlib import Path
from difflib import Differ
from textwrap import indent
import shlex
import time

DEFAULT_TIMEOUT = 2
DEFAULT_TESTS_DIR = './tests'

class TestRunner:
    def __init__(self, command, tests=None, timeout=DEFAULT_TIMEOUT):
        if tests == None:
            tests_path = Path(DEFAULT_TESTS_DIR)
            if not tests_path.is_dir():
                tests_path = Path('.')
        else:
            tests_path = Path(tests)
            if not tests_path.is_dir() :
                raise ValueError("tests must be an existing folder path string")
        self.tests_path = tests_path
        self.command = shlex.split(command)
        self.timeout = timeout

    def _test(self, input_file, output_file):
        input_file = input_file.open()
        output_file = output_file.open()

        start_time = time.time()

        execution = Popen(self.command, stdin=input_file, stdout=PIPE, stderr=PIPE,
                          universal_newlines=True)
        try:
            output, errors = execution.communicate(timeout=self.timeout)
        except TimeoutExpired:
            execution.kill()
            print('Input file "{0}" timed out\n'.format(input_file.name))
            return False

        run_time = time.time() - start_time

        output = output.splitlines(keepends=True)
        correct_output = output_file.readlines()

        if errors:
            print('Input file "{0}" caused one or more errors:\n'.format(input_file.name))
            print(indent(errors, '    '))
            return False

        if output != correct_output:
            print('Input file "{0}" gave incorrect output:\n'.format(input_file.name))
            differ = Differ()
            for line in differ.compare(correct_output, output):
                print(line, end='')
            print()
            return False

        input_file.close()
        output_file.close()

        print('Input file "{0}" finished in {round(run_time, 3)} seconds'.format(input_file.name))
        return run_time

    def run_test(self, testName):
        input_file = next(self.tests_path.glob('{0}-input.txt'.format(testName))).open()
        output_file = next(self.tests_path.glob('{0}-output.txt'.format(testName))).open()

        self._test(input_file, output_file)

    def run_all_tests(self):
        input_files = sorted(self.tests_path.glob('*-input.txt'))
        output_files = sorted(self.tests_path.glob('*-output.txt'))
        if len(input_files) != len(output_files):
            raise ValueError('different number if input files to output files')

        total = len(input_files)
        passed = 0
        total_time = 0
        for input_file, output_file in zip(input_files, output_files):
            output = self._test(input_file, output_file)
            if output:
                passed += 1
                total_time += output
        print("{0}/{1} tests passed in {2} seconds".format(passed, total, round(total_time, 1)))

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Run stdin and stdout tests')
    parser.add_argument("command", help="command to be tested")
    parser.add_argument("-f", "--folder", dest="folder",
                        help="path to folder containing tests")
    parser.add_argument("-t", "--timeout", dest="timeout", type=int, default=DEFAULT_TIMEOUT,
                        help="maximum time for a test to run")

    args = parser.parse_args()

    a = TestRunner(args.command, tests=args.folder, timeout=args.timeout)
    a.run_all_tests()
