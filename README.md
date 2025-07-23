# Corn Stress Area and Color Analysis
This is a collection of files and scripts to analyse the stressed to healthy
leaf area in cold treated (or otherwise stressed corn) and to map the changes
in colorspace distribution over the span of two different timepoints. The
python script will identify the healthy and stressed tissue, as well as do
the area and colorspace analysis. There is a separate R script that will
do the arrow plot showing the shift in A and B values for the control and the
experimental plants.

## Folder layout
```
projectFolder/ 			# Scripts should be run from this folder
│
├── stressColorAnalysis.py  # Main Python script
├── plot_arrows.R        	  # R plotting script
├── requirements.txt     	  # Python dependencies
├── install_r_packages.R 	  # R dependencies
├── setup.sh             	  # Setup script (macOS/Linux)
├── setup.bat            	  # Setup script (Windows)
├── naive_bayes_pdfs.txt    # Naive Bayes pdfs for running the classifier
├── images/              	  # Input images Setup script
├── masks/               	  # Output masks (for QC)
└── results/             	  # Results csv and graph output folder
```

## Setup
Run the setup scripts first to install the dependencies. It will skip any
you have already installed. This only needs to be run once.

**Install dependencies**:
   - unix: Run `bash setup.sh`
   - Windows: Double-click `setup.bat`


## Running the Python Script
the basic command usage is:

`python stressColorAnalysis.py images/`

If you want to specify different names for the masks directory and the results
directory you can do it like so:

`python stressColorAnalysis.py images/ resultsNewName/ masksNewName/`

You do not need to make the results or the mask directories, the script will handle
that for you. However, any rerun will rewrite the contents of those directories unless
you supply new directory names

## Running the R script
Assuming you did not change the ouput csv filename from the python script, all
you need to generate the arrow plots is to run

`Rscript arrowPlot.R results/`

(Replace results/ with whatever you chose to name it, if you went with something
other than the defaults. Keep in mind that the `/` at the end is required)


## Output files
These scripts will generate 5 output files (not including the masks).
1. healthy_stressed_results.csv # Your .csv file with the plant areas and the color mass
2. healthy_stressed_area.svg 	# The stacked bar chart showing healthy/stressed area
3. colorchange_cold.png		# The arrow plot of the cold treated plants
4. colorchange_control.png	# The arrow plot of the control plants
5. colorchange_combined.png	# The combined arrow plot showing cold and control
