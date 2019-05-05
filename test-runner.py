from subprocess import Popen, PIPE, TimeoutExpired
from pathlib import Path
from difflib import Differ
from textwrap import indent
import shlex

DEFAULT_TIMEOUT = 2
DEFAULT_TESTS_DIR = './tests'

class TestRunner:
    def __init__(self, command, tests=None, timeout=DEFAULT_TIMEOUT):
        if tests == None:
            testsPath = Path(DEFAULT_TESTS_DIR)
            if not testsPath.is_dir():
                testsPath = Path('.')
        else:
            testsPath = Path(tests)
            if not testsPath.is_dir() :
                raise ValueError("tests must be an existing folder path string")
        self.testsPath = testsPath
        self.command = shlex.split(command)
        self.timeout = timeout

    def _test(self, inputFile, outputFile):
        inputFile = inputFile.open()
        outputFile = outputFile.open()

        execution = Popen(self.command, stdin=inputFile, stdout=PIPE, stderr=PIPE,
                          universal_newlines=True)
        try:
            output, errors = execution.communicate(timeout=self.timeout)
        except TimeoutExpired:
            execution.kill()
            print(f'Input file "{inputFile.name}" timed out\n')
            return False

        output = output.splitlines(keepends=True)
        correctOutput = outputFile.readlines()

        if errors:
            print(f'Input file "{inputFile.name}" caused one or more errors:\n')
            print(indent(errors, '    '))
            return False

        if output != correctOutput:
            print(f'Input file "{inputFile.name}" gave incorrect output:\n')
            differ = Differ()
            for line in differ.compare(correctOutput, output):
                print(line, end='')
            print()
            return False

        return True

    def run_test(self, testName):
        inputFile = next(self.testsPath.glob(f'{testName}-input.txt')).open()
        outputFile = next(self.testsPath.glob(f'{testName}-output.txt')).open()

        self._test(inputFile, outputFile)

    def run_all_tests(self):
        inputFiles = sorted(self.testsPath.glob('*-input.txt'))
        outputFiles = sorted(self.testsPath.glob('*-output.txt'))
        if len(inputFiles) != len(outputFiles):
            raise ValueError('different number if input files to output files')

        total = len(inputFiles)
        passed = 0
        for inputFile, outputFile in zip(inputFiles, outputFiles):
            if self._test(inputFile, outputFile):
                passed += 1
        print(f"{passed}/{total} tests passed")

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
