# TestRunner
TestRunner is a command line tool to check code against stdin/stdout sample files
  - Measures running time
  - Checks output against sample
  - Runs multiple tests at once
  - Works with any programming language

### Installation

TestRunner requires [Python](https://www.python.org/) 3.6+ to run.

Download the source folder, and extract the archive.

### Quick start
Place your code in the folder containing `test-runner.py`.

Create a folder called `tests`, containing your sample input and output.
Sample input and output files should have the suffixes `-input.txt` and
`-output.txt` respectively

Your file structure should be:
```
test-runner/
├── my-code.<ext>
├── test-runner.py
└── tests/
    ├── sample1-input.txt
    ├── sample1-output.txt
    ├── sample2-input.txt
    └── sample2-output.txt
```
Then run in the terminal:
```sh
$ python3 test-runner.py "<command to run your code>"
```
For example, to test a python file called `my-code.py`:
```sh
$ python3 test-runner.py "python3 ./my-code.py"
```

### Custom Configuration

#### Tests folder
By default TestRunner will look for the `./tests` folder, and if no such folder exists, it will look for any files in the root directory `./`.
By using the `-f` option, you can specify a  folder containing the tests.
```sh
$ python3 test-runner.py "<command to run your code>" -f ./my-tests
```
#### Timeout
By default, TestRunner will stop any test if it runs longer than 2 seconds.
By using the `-t` option, you can specify a custom timeout in seconds ( e.g for large tests):
```sh
$ python3 test-runner.py "<command to run your code>" -t 60
```
