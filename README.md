# Description

A powerful, scriptable, modular calculator aimed at scientific, engineering or computing work.

All features can be added, removed, and customised, and new features can be written in python.

For syntax and other topics, see the [modularcalculator wiki](https://github.com/JordanL2/ModularCalculator/wiki).

[Licence](LICENSE)

[Changelog](CHANGELOG.md)


# Requirements

* Linux
* One of:
	* Flatpak
* or:
	* Python 3.9+
	* Qt 6.3+
	* PyQt6
	* libyaml


# Installation

## Flatpak

There is a flatpak available on [Flathub](https://flathub.org/apps/details/io.github.jordanl2.ModularCalculator).

## Nix

There is a community maintained Nix flake available in this repository. This flake can be used to run or install the program on NixOS or other distributions.

Run the program once without installing:

```bash
nix run --no-write-lock-file github:JordanL2/ModularCalculatorInterface
```

Install the program:

```bash
nix profile add --no-write-lock-file github:JordanL2/ModularCalculatorInterface
```

Add to system configuration (NixOS only):

```nix
# In flake.nix
{
  inputs = {
    modularcalculator.url = "github:JordanL2/ModularCalculatorInterface";
  };

  outputs = { modularcalculator, ... }: {
    nixosConfigurations.<host> = nixpkgs.lib.nixosSystem {
      modules = [
        ./configuration.nix
      ];
      specialArgs = {
        inherit modularcalculator;
      };
    };
  };
}

# in configuration.nix
{ modularcalculator, ... }:
{
    environment.systemPackages = [
        modularcalculator.packages.x86_64-linux.default
    ];
}
```

Install python library (NixOS only):

```nix
# in configuration.nix
{ pkgs, modularcalculator, ... }:
{
    environment.systemPackages = [
        (pkgs.python3.withPackages([
            modularcalculator.packages.x86_64-linux.python
        ]))
    ];
}
```

## Manually

Clone this repository, then run:

```
sudo ./install
```

If you download the source tarball, you'll also need to download the [modularcalculator](https://github.com/JordanL2/ModularCalculator) tarball and install it prior to running the above command.


# Uninstallation

## Nix

```bash
nix profile remove ModularCalculatorInterface
```

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

The application stores all configuration options inside its config file: `config.yml`.

The config files can be found in any of the below locations.

1. `$XDG_CONFIG_HOME/ModularCalculator` (or `$HOME/.config/ModularCalculator`)
2. Each directory in `$XDG_CONFIG_DIRS`, followed by `/ModularCalculator`
3. `/etc/ModularCalculator`
4. `/app/share/ModularCalculator` (this is where the flatpak's config files are installed to, inside the flatpak)
5. `/usr/share/ModularCalculator` (this is where the manual installation installs the default files to)
6. `../config/ModularCalculator` (relative to `main.py`)

All found config files are merged together, with the top locations being highest precedence.


### Themes

Themes are stored inside the config directory, inside `themes/*.yml`.

These files contain themes to change the colours of the input and output contents.

An example can be found at [config/ModularCalculator/themes/default.yml](config/ModularCalculator/themes/default.yml)

Note: `background` and `background_alt` are optional and will default to your Qt theme's Base and Alternate Base colours.
