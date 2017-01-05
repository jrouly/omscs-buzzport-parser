Run `python parser.py` to do everything. Requires `table.html` in the same
directory in order to parse the available courses.

Will automatically filter only Foundational courses that are able to be
registered for by an OMSCS student.

### table.html

Raw `<tbody>` from the Buzzport registration page. Make sure to delete any
intermediate header `<tr>`s, only keeping the very first one.
