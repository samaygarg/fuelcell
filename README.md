[![Documentation Status](https://readthedocs.org/projects/fuelcell/badge/?version=latest)](https://fuelcell.readthedocs.io/en/latest/?badge=latest)

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
    * `data`: a list of `Datum` objects which contain the data to be plotted
    * `fig`: a `matplotlib` `Figure` object
    * `ax`: a `matplotlib` `Axes` object or a list of `Axes` objects if multiple axes are needed
* Any and all other arguments can be specified as needed for that particular function

### `utils.py`
Functions for file handling and other general-purpose functions. 
*  If the current set of file handling functions is insufficient, new file handling functions shoud be added here

###  `model.py` and `Datum`
`model.py` contains the `Datum` class, which is used to store data along with all associated experimental parameters and any features extracted from post-processing operations.
* Whenever a new attribute is added to the `Datum` class, it should be initialized in the `__init__` method with a default value, and accessor and modifier functions corresponding to attribute should be added to the class as well. 
#### Key features of `Datum`
The `Datum` object has a wide range of attributes to allow for flexible storage of data from different electrochemical experiments. The most useful attributes are:
* `name`: The original filename from which the data were retrieved this. This will be set when the data file is initally read in and should not be changed.
* `label`: The label which appear in the legends of any plots which contain these data.
*  `raw_data`: a pandas DataFrame containing the data as it appears in the original file .This will be set when the data file is initally read in and should not be changed.
*  `processed_data`: a pandas DataFrame containing the data after after it has been processed
The remaining attributes are set as need to store experimental parameters, such as the MEA area, the reference electrode, etc; and features extracted from post-processing operations, such as the tafel slope, the high frequency resistance, etc.

## License
[MIT](https://choosealicense.com/licenses/mit/) 