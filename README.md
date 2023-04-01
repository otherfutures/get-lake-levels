# Short Description:<br>
Produces CSV & JSON files for US lake level info.<br>

# Instructions:<br>
1. The source code for this project can be found in `lake_levels.py` above.

2. Please check the required libraries/packages before running. <br>
All of them should be native to Python except for `beautifulsoup4` & `prompt_toolkit`.<br>
Those can be downloaded via pip in the shell/command line:<br>
```python
pip install beautifulsoup4
```
```python
pip install prompt_toolkit
```

3. If you decide to fork/change this program, please don't hammer the website this program scrapes info from into oblivion.<br>
The information doesn't update all that often anyways.<br>

# Longer Descriptions:<br>
Since we're experiencing more & longer droughts, it might be useful/helpful to monitor lake levels.<br>
This program scrapes national lake information & creates a CSV & JSON file.<br>
The information comes from https://lakelevels.info & is already freely & publicly accessible,<br>
but it lacks a real API to programmatically use the info.<br> 
<br>
Info can be retrieved by state (a fuzzy autocomplete for searching states exists in the program) or<br>
all the lake levels on record can be amassed into one file each for CSV & JSON.<br>
Unfortunately, this is not a comprehensive list of all the lakes in the US (let alone the world),<br>
but can still be useful to get a sense of how familiar bodies of water are doing in near real time. 
