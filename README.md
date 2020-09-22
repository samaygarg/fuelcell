# fuelcell
fuelcell is a Python library  for electrochemical data analysis.

## Installation
`fuelcell` can be installed using `pip`:

```bash
pip install fuelcell
```
The latest version of the standalone GUI is published [here](https://drive.google.com/drive/folders/1oKhBIiCk0m0kc0RRme3VpfQP41taH4C7?usp=sharing)

##  Structure
- `datums.py`: Data processing functions
- `visuals.py`: Data visualization functions
- `utils.py`: File handling and general functions
- `model.py`:  `Datum` class to store electrochemical data along with associated features  and expereimental parameters
- `fuelcell_gui.py`: Graphical user interface for interactive use

## For contributors
### `datums.py`
Functions to load and process data
* Functions to implement new data processing protocol and new data analysis techniques should be added here 

### `visuals.py`
Functions for creating data visualizations
* Functions to implement new data visualizations  should be added here
* In order to link these functions to the GUI,  the function must accept the following arguments:
    * `fig`: a `matplotlib` `Figure` object
    * `ax`: a `matplotlib` `Axes` object or a list of `Axes` objects if multiple axes are needed
* Any and all other arguments can be specified as needed for that particular function

### `utils.py`
Functions for file handling and other general-purpose functions. 
*  If the current set of file handling functions is insufficient, new file handling functions shoud be added here

###  `model.py`
Contains the `Datum` class, which is used to store data along with all associated experimental parameters, such as MEA active area and reference electrode, and features extracted from post-processing operation,  such as tafel slope and high frequency resistance.
* Whenever a new attribute is added to the `Datum` class, it should be initialized in the `__init__` method with a default value, and accessor and modifier functions corresponding to attribute should be added to the class as well. 

## License
[MIT](https://choosealicense.com/licenses/mit/) 