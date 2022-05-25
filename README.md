# Description

A powerful, scriptable, modular calculator aimed at scientific, engineering or computing work.

All features can be added, removed, and customised, and new features can be written in python.


# Requirements

* Linux
* One of:
	* Flatpak
* or:
	* Python 3.9+
	* Qt 5.11+


# Installation

## Flatpak

There is a flatpak available on [Flathub](https://flathub.org/apps/details/io.github.jordanl2.ModularCalculator).

## Manually

First, install the [modularcalculator](https://github.com/JordanL2/ModularCalculator) python library.

Then:
```
sudo ./install
```


# Uninstallation

## Manually

```
sudo ./uninstall
```


# Usage

"Modular Calculator" should be available in your desktop environment application menu.

Alternatively, run in a terminal:

1. Flatpak: `flatpak run io.github.jordanl2.ModularCalculator`
2. Manual installation: `modularcalculator`


## Input and Execution

Statements to be executed are entered in the left-hand pane, labelled "Input".

Multiple statements can be entered. Enter / Return inserts a new line.

For syntax and other topics, see the [modularcalculator wiki](https://github.com/JordanL2/ModularCalculator/wiki).

The Insert menu helps with quickly inserting constants, dates, operators, functions, units and user-defined functions. These menus help discover what constants etc are available.

To execute the statements, press Ctrl+Enter, or click the Execute button on the menu bar.

The right-hand pane labelled "Output" will be cleared, and the results of all the statements in the input pane will be displayed in order.


## Configuration

A lot of configuration options are available inside the application. It's possible to configure some more things with config files.

The application looks in these locations for config files, in this order:

1. `$XDG_CONFIG_HOME/ModularCalculator` (or `$HOME/.config/ModularCalculator`)
2. Each directory in `$XDG_CONFIG_DIRS`, followed by `/ModularCalculator`
3. `/etc/ModularCalculator`
4. `/app/share/ModularCalculator`
5. `/usr/share/ModularCalculator` (this is where the manual installation installs the default files to)
6. `../config/ModularCalculator` (relative to `main.py`)

To configure the flatpak, you'll need to add config files to `$HOME/.var/app/io.github.jordanl2.ModularCalculator/config/ModularCalculator`.

Otherwise, it's usually best to add them to `$HOME/.config/ModularCalculator`.

Look in [config/ModularCalculator] for the application's default config files.


### config.yml

This file can configure various aspects for how the application looks, such as font, font size and boldness.

An example can be found at [config/ModularCalculator/config.yml](config/ModularCalculator/config.yml)


### themes/*.yml

These files contain themes to change the colours of the input and output contents.

An example can be found at [config/ModularCalculator/themes/default.yml](config/ModularCalculator/themes/default.yml)

Note: `background` and `background_alt` are optional and will default to your Qt theme's Base and Alternate Base colours.
