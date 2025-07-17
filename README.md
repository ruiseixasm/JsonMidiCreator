# JsonMidiCreator
Program that creates files for the JsonMidiPlayer program: https://github.com/ruiseixasm/JsonMidiPlayer

# Pre requisites and installations
1. Python version 3.11 or above due to the new `Self` type;
2. Library `matplotlib` for plotting in order to do `>> Plot()`;
3. [JsonMidiPlayer](https://github.com/ruiseixasm/JsonMidiPlayer) shared library in order to do `>> Play()`;
4. Library [ctypes](https://docs.python.org/3/library/ctypes.html) to run the [JsonMidiPlayer](https://github.com/ruiseixasm/JsonMidiPlayer) library above. Normally is already installed.
5. Library [mido](https://mido.readthedocs.io/en/stable/) to export Midi files with `>> Export("midi_file.mid")`;
6. [Jupyter](https://jupyter.org/) library if you intend to use Notebooks. Highly recommended.

## How to install matplotlib
Go to your command line and type:
```
python -m pip install -U pip
python -m pip install -U matplotlib
```

## How to get the JsonMidiPlayer files
1. Go to the [JsonMidiPlayer Releases page](https://github.com/ruiseixasm/JsonMidiPlayer/releases) and in the last release page you open, download the `.dll` or `.so` file for Windows or Linux respectively;
2. Copy the `.dll` or `.so` file into your own local [JsonMidiCreator](https://github.com/ruiseixasm/JsonMidiCreator) library `/lib` folder.
Go to [/lib](https://github.com/ruiseixasm/JsonMidiCreator/tree/main/lib) to see even more details.

## How to install the mido library
Go to your command line and type:
```
python3 -m pip install mido
```

## How to install and use Jupyter
### Installation
Go to your command line and type:
```
python3 -m pip install jupyterlab
```
### Usage
Open the command line in the [JsonMidiCreator](https://github.com/ruiseixasm/JsonMidiCreator) folder, and type:

```
jupyter notebook --no-browser
```
Then open you favorite browser and copy and paste one of the given URLs as instructed in the output of the previous command.

# Documentation
## Classes docstrings documentation
All classes are documented with docstrings, you can mouse over the class to get a pop up with the class description.
## Classes documentation in Jupyter
While using Jupyter notebooks, you may press `Shift + Tab` to get the class popup equal to the one described above.
## Jupyter Notebooks examples
If you prefer real examples, you can go to the folder [Jupyter](https://github.com/ruiseixasm/JsonMidiCreator/tree/main/Jupyter) in the present library
and open any of those files with the extension `.ipynb` in your computer or directly in GitHub, by clicking on them.

