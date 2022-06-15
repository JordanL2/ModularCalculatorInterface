# Changelog

## 1.4.0
- Added Export Results button, to export the calculation results as a CSV file.
- Added Number format option, to automatically display all numerical answers as e.g. hexadecimal, scientific notation.
- Added Rounding option to determine how numbers are rounded.
- Added option to determine the maximum size of numbers before the decimal point.
- Replaced application menu with a toolbar, for easier access to all buttons.
- All configuration is done through a single options panel, removing all the various menu items.
- All application configuration is now stored in the config.yml file.
- Fixed bug causing glitching when editing earlier statements when later statements had an execution error.
- Fixed bug when disabling arrays feature and we're already displaying results with arrays.
- Syntax highlighting is now faster.
- 'Show execution errors' syntax highlighting now done in a separate process.
- Added modularcalculator repository into this repository as a submodule, to make manual installation easier.
### Using modularcalculator calculator engine version 1.3.0:
- Big improvements for alternative-base numbers and scientific notation numbers:
	- Converting a number to an alternative-base number, or scientific notation number, respects the calculator's precision option.
	- Alternative-base numbers and scientific notation numbers now all stored internally as a Number, with 'number_cast' attribute storing a function reference to convert back to its original representation - this is done when casting to a string. This avoids converting between formats multiple times internally, potentially losing precision each time.
- Number casters now includes a reference to the function to reverse the casting to Number.
- Numerical Engine has `number_set_rounding` function to set rounding mode, use names of `decimal` rounding modes.
- Fixing error thrown when throwing a CalculateException.
- Fixing scientific notation number 0E0 being displayed as E0.

## 1.3.1
- Fixed "Line Highlighting" option.
- Fixed displaying an answer which is just a unit.
- Fixed About dialog not being modal.
### Using modularcalculator calculator engine version 1.2.2:
- Closing file handle in externalfunctions.
- Rewrote test framework to use unittest, now faster, and more coherant as all tests now use same framework.

## 1.3.0
- Added the ability to configure the font (family, size, boldness) for the input and output panes.
- Added the ability to change the theme, and add new themes.
- Added seven themes:
	- Darker
	- Default
	- High Contrast (Black)
	- High Contrast (White)
	- Monochrome (Black)
	- Monochrome (White)
	- Tango
- Added Help menu, with link to Calculator Reference pages, and About dialog.
- Missing styling in certain elements in the output pane have been fixed.
- Double clicking an item in an Insert dialogue will now choose the item and insert it.
- Install/Remove Features window is no longer hidden when opening the file picker.
- Switching a tab is now faster, no longer automatically re-executes the input when you switch tab.
- Fixed bug when opening a file and being able to undo, resulting in blank page.

## 1.2.1
- Middle clicking an answer now pastes either the normal or draction version, depending on which you middle clicked.
### Using modularcalculator calculator engine version 1.2.1:
- Precision improvement for Number.log.
- Minor performance improvement for Number.is_integer.

## 1.2.0
- If an answer can be expressed as a fraction, it is displayed under the normal answer.
### Using modularcalculator calculator engine version 1.2.0:
- Replaced internal number representiation with new Number class:
	- Stores all numbers as a ratio between two integers, allowing storing fractions (e.g. 1/3) perfectly without rounding errors.
	- Rounds number only when representing it as a string.
	- Can return number in integer+num/den fraction format.

## 1.1.2
- Updating appdata homepage URL.

## 1.1.1
- Various changes for flatpak packaging.

## 1.1.0
- First version split from modularcalculator repo.
### Using modularcalculator calculator engine version 1.1.0:
- First version after splitting interface to its own repository.
