# Changelog

## 1.5.0
- Ported to Qt6.
- Categorised selection dialogs now have an 'All' category that is selected by default.
- Categorised selection dialogs now have a search box.
- Added option to auto-execute input after a specified number of seconds.
- Added insert menu for numerical types (used with 'as' operator).
- Improved buttons in Options menu.
- Added Qt and PyQt version to About dialog.
- Themes are reworked to have far fewer elements.
- Fixed pasting text that starts or ends with a space.
- Fixed selecting presets in Options > Features.
- Fixed displaying fractions in answer that are negative but less than 1.
### Using ModularCalculator engine version 1.4.0:
- New functions: lcm (lowest common multiple) and gcd (greatest common divisor).
- Added many special functions from SciPy.
- Added 'as' operator that can convert a value's numerical type (e.g. convert to binary).
- Added percentage numerical type.
- Function names can now contain, but not start with, a number.
- Fixed a unit assignment not having higher precedence than multiply.

## 1.4.5 (07 July 2022)
- Line highlighting now follows the same patten in Input as Output (even numbers are highlighted).
- Fixed application crashing on start if there was an error restoring state.
### Using ModularCalculator engine version 1.3.1:
- Fixed displaying units - divisor in brackets now used closed bracket properly.
- Fixed potential infinite loop when simplifying units. This has slightly reduced the kind of simplification that can be done.
- Unit powers can now be non-integers.
- Assignment operators (e.g. +=) now return the new value of the variable.
- Number power operator is now more accurate when given negative powers.

## 1.4.4 (26 June 2022)
- Fixed bug in show execution errors syntax highlighting when cutting and pasting mid-statement.
- Fixed line highlighting with a statement has a comment on the end of its line.
- Fixed lack of syntax highlighting when pasting the same text into the calculator as plaintext.

## 1.4.3 (20 June 2022)
- Tweaks to Material Dark and Light themes.
- Fixed show execution errors syntax highlighting not being triggered when switching tabs with keyboard.

## 1.4.2 (19 June 2022)
- Darker theme: Tweaked to reduce and balance brightness, and separate hues from each other more.
- Added "Darkish" theme, same as "Darker" but with a lighter background.
- Added themes "Material Light" and "Material Dark", based on Google's Material Design.
- Added "Dracula" dark theme.
- Added "Github" light theme.

## 1.4.1 (18 June 2022)
- Fixed not being able to select different option tabs with the keyboard.
- Fixed installer and README instructions when downloading a source tarball.
- Fixed cut/copy/paste/delete in context menu and drag+drop events not updating syntax highlighting or making an undo stage.

## 1.4.0 (16 June 2022)
- Replaced application menu with a toolbar. Can configure whether it shows icons, text, or both (default).
- Added Options dialog, replacing the various menu items.
- Added Export Results button, to export the calculation results as a CSV file.
- Added Number format option, to automatically display all numerical answers as e.g. hexadecimal, scientific notation.
- Added Rounding option to determine how numbers are rounded.
- Added option to determine the maximum size of numbers before the decimal point.
- Added options to configure font family, size, boldness of input and output panes.
- All application configuration is now stored in the config.yml file.
- Fixed bug causing glitching when editing earlier statements when later statements had an execution error.
- Fixed bug when disabling arrays feature and we're already displaying results with arrays.
- Fixed output background colour not being properly set on some platforms.
- Fixed font defaulting to Hack, now gets system default fixed-witch font.
- Syntax highlighting is now faster.
- 'Show execution errors' syntax highlighting now done in a separate process.
- Added modularcalculator repository into this repository as a submodule, to make manual installation easier.
### Using ModularCalculator engine version 1.3.0:
- Ceil and floor functions now also have an optional places parameter.
- Numerical Engine has `number_set_rounding` function to set rounding mode, use names of `decimal` rounding modes.
- Numerical Engine has `number_size_set` function to set the maximum size of numbers (before decimal point).
- Number casters now includes a reference to the function to reverse the casting to Number.
- Various improvements for alternative-base numbers and scientific notation numbers:
	- Converting a number to an alternative-base number, or scientific notation number, respects the calculator's precision option.
	- Alternative-base numbers and scientific notation numbers now all stored internally as a Number, with 'number_cast' attribute storing a function reference to convert back to its original representation - this is done when casting to a string. This avoids converting between formats multiple times internally, potentially losing precision each time.
	- Fixing scientific notation number 0E0 being displayed as E0.
	- Round, ceil and floor functions now all work properly with alternative-base numbers when specifying places.
	- Binary numbers now preserve their width (e.g. number of leading zeros) on creation and after a bitwise operation, all other operations discard the width afterwards.
- Fixing error thrown when throwing a CalculateException.

## 1.3.1 (06 June 2022)
- Fixed "Line Highlighting" option.
- Fixed displaying an answer which is just a unit.
- Fixed About dialog not being modal.
### Using ModularCalculator engine version 1.2.2:
- Closing file handle in externalfunctions.
- Rewrote test framework to use unittest, now faster, and more coherant as all tests now use same framework.

## 1.3.0 (26 May 2022)
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

## 1.2.1 (21 May 2022)
- Middle clicking an answer now pastes either the normal or fraction version, depending on which you middle clicked.
### Using ModularCalculator engine version 1.2.1:
- Precision improvement for Number.log.
- Minor performance improvement for Number.is_integer.

## 1.2.0 (19 May 2022)
- If an answer can be expressed as a fraction, it is displayed under the normal answer.
### Using ModularCalculator engine version 1.2.0:
- Replaced internal number representiation with new Number class:
	- Stores all numbers as a ratio between two integers, allowing storing fractions (e.g. 1/3) perfectly without rounding errors.
	- Rounds number only when representing it as a string.
	- Can return number in integer+num/den fraction format.

## 1.1.2 (04 October 2021)
- Updating appdata homepage URL.

## 1.1.1 (03 October 2021)
- Various changes for flatpak packaging.

## 1.1.0 (02 October 2021)
- First version split from modularcalculator repo.
### Using ModularCalculator engine version 1.1.0:
- First version after splitting interface to its own repository.
