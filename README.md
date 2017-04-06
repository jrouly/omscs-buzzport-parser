# omscs-buzzport-parser

Generates a CSV of courses available for an OMSCS student to sign up for sorted by the number of remaining slots.

## How To

### Setup

Create a Python virtual environment and install dependencies.

    virtualenv omscs
    source omscs/bin/activate
    pip install -r requirements.txt

### Navigating GA Tech's OSCAR

1. Login to BuzzPort, hit `Student` and then find `OSCAR`.
2. Navigate to `Student Services & Financial Aid`.
3. Navigate to `Registration`.
4. Navigate to `Look up Classes` and select your desired term.
5. Hit `Advanced Search`.
6. On the `Advanced Search` screen, select your desired subject(s) and other criteria. Hit `Section Search`.
7. Inspect the page source and find the main `<tbody>` element.
   Copy it into a new file called `table.html` in the `input/` directory.
   There is a sample `table.html` in the root directory of this repo.

### Running the parser script

Run `python parser.py`.
Make sure that you've loaded the course data into `input/table.html`.
This should generate an output file `table.csv` which will contain the filtered and sorted data.

