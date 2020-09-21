# fuelcell
fuelcell is a Python library  for electrochemical data analysis.

##  Structure
- `datums.py`: Data processing functions
- `visuals.py`: Data visualization functions
- `utils.py`: File handling and general functions
- `model.py`:  `Datum` object to store electrochemical data along with associated features  and expereimental parameters
- `fuelcell_gui.py`: Graphical user interface for interactive use

## For contributors
### `datums.py`
Functions to load and process data
* Functions to implement new data processing protocol and new data analysis techniques should be added here 

### `visuals.py`
Functions for creating data visualizations
* Functions to implement new data visualizations  should be added here
* In order to link these functions to the GUI,  the function must accept the following arguments:
    * `data` OR `xdata` and `ydata`: either a list of `Datum` objects which contain the data to be used in the plot, or arguments to individually specify x- and y- data 
    * `fig`: a `matplotlib` `Figure` object
    * `ax`: a `matplotlib` `Axes` object or a list of `Axes` objects if multiple axes are needed
* Any and all other arguments can be specified as needed for that particular function

### `utils.py`
Functions for file handling and other general-purpose functions. 
*  If the current set of file handling functions is insufficient, new file handling functions shoud be added here
## License
[MIT](https://choosealicense.com/licenses/mit/) 