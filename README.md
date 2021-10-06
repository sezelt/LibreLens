# LibreLens

This tool provides a (hopefully) sensible way to interact with the free lens control capabilities in TEMSpy. 

Much like the stigmator controls in the TEM UI, this tool lets you copy lens settings from the TEMSpy Outputs window to a set of registers, and copy them back as desired. 

To use LibreLens, _first_ open the Ouputs pane in TEMSpy, then load a Lens Definition File.

This is especially useful for Lorentz STEM, which ordinarily requires the user to write down and manually re-enter a variety of lens settings that the TEM frequently overrides against your will. With this tool, you can easily store and recall several instances of the state of every lens in the microscope.

Information on how to communicate with TEMSpy, including the names and IDs of all the lenses on your current instrument, are stored in a _lens definition file_. LibreLens is currently provided with definition files for the ThemIS microscope at NCEM (others may be added over time). This file can also be used to save the lens values from your session, so they can be recalled at a later time.

## Creating a Lens Definition File
The lens definition file contains the list of all the lenses that the TEMspy Outputs pane presents to you, and so may have to be updated for different microscopes. In addition, because LibreLens uses a rather backdoor way to access and modify this data, certain information in the lens definition file may require modification if a different build of TEMSpy is installed.