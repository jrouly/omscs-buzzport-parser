# omscs-buzzport-parser

Given the HTML from the Buzzport advanced course search, generate a CSV of
courses an OMSCS student can sign up for sorted by the number of remaining
slots.

Run `python parser.py` to do everything. Requires `table.html` in the same
directory in order to parse the available courses.

### table.html

Raw `<tbody>` from the Buzzport registration page. Make sure to delete any
intermediate header `<tr>`s, only keeping the very first one.
