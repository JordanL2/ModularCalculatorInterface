# Changelog

## 1.4.0
- All application configuration is now stored in the config.yml file.
- All configuration is done through a single options panel, removing all the various menu items.
- Replaced application menu with a toolbar, for easier access to all buttons.
- Added Export Results button, to export the calculation results as a CSV file.
- Fixed bug causing glitching when editing earlier statements when later statements had an execution error.
- Fixed bug when disabling arrays feature and we're already displaying results with arrays.
- Syntax highlighting is now faster.
- 'Show execution errors' syntax highlighting now done in a separate process.
- Added modularcalculator repository into this repository as a submodule, to make manual installation easier.

## 1.3.1
- Fixed "Line Highlighting" option.
- Fixed displaying an answer which is just a unit.
- Fixed About dialog not being modal.
- Using modularcalculator version 1.2.2.

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
- Using modularcalculator version 1.2.1.

## 1.2.0
- Using modularcalculator version 1.2.0, with its new Number class, enabling better precision.
- If an answer can be expressed as a fraction, it is displayed under the normal answer.

## 1.1.2
- Updating appdata homepage URL.

## 1.1.1
- Various changes for flatpak packaging.

## 1.1.0
- First version split from modularcalculator repo.
