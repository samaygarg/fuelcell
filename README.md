[![Documentation Status](https://readthedocs.org/projects/fuelcell/badge/?version=latest)](https://fuelcell.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) HTML: <a href="https://joss.theoj.org/papers/79df7852b6fedb417b625979da1f5567"><img src="https://joss.theoj.org/papers/79df7852b6fedb417b625979da1f5567/status.svg"></a>
Markdown: [![status](https://joss.theoj.org/papers/79df7852b6fedb417b625979da1f5567/status.svg)](https://joss.theoj.org/papers/79df7852b6fedb417b625979da1f5567)

# fuelcell
`fuelcell` is a Python package which streamlines electrochemical data analysis. 

`fuelcell` includes both a standard Python package which can be used programmatically and incorporated into an existing workflow, as well as a standalone graphical user interface for interactive use.

If you have a feature request or find a bug, please file an [issue](https://github.com/samaygarg/fuelcell/issues) or submit a [pull request](https://github.com/samaygarg/fuelcell/pulls). This is designed to be an open-source tool which the entire electrochemical community can build upon and use.

## Installation
`fuelcell` can be installed from PyPI using `pip`:

```bash
pip install fuelcell
```

## GUI 
The latest version of the standalone GUI can be downlaoded [here](https://fuelcell.readthedocs.io/en/latest/gui.html). There are separate versions for Mac and Windows operating systems.

## Documentation
The documentation can be found at [fuelcell.readthedocs.io](https://fuelcell.readthedocs.io/en/latest/) 

##  Package Structure
- `datums.py`: Data processing functions
- `visuals.py`: Data visualization functions
- `utils.py`: File handling and general auxilliary functions
- `model.py`:  `Datum` class to store electrochemical data along with associated features  and expereimental parameters
- `fuelcell_gui.py`: Graphical user interface for interactive use

## License
[MIT](https://choosealicense.com/licenses/mit/) 
