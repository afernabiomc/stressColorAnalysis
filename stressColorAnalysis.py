import numpy as np
# Imports PlantCV into notebook so that we can conduct plant phenotyping analyses
from plantcv import plantcv as pcv
# Imports library to handle workflow inputs compatible with parallel workflow execution.
from plantcv.parallel import WorkflowInputs
import cv2 as cv
import argparse
import pandas as pd
import os
import matplotlib.image
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputDir", help = "Directory containing the images to be processed. Folder should only contain image files")
parser.add_argument("-r", "--resultsDir", help = "Directory where the results files should be stored", default = "results/")
parser.add_argument("-m", "--masks", help = "Directory where the mask files should be stored", default = "masks/")
args = parser.parse_args()


pcv.params.debug = "None" # Suppress image generation in Jupyter notebook (slows the process way down)
def healthy_stress_ratio(imname, basename, masks):
	''' Uses a naive bayes pdf model with categories for stressed tissue,
	healthy tissue, and background to calculate the stressed vs. healthy
	tissue area, and return a color distribution for the whole plant in
	LAB colorspace '''

	img, path, img_filename = pcv.readimage(filename=imname, mode="native")
	# crop values may need to change based on image set, within one image set
	# plant positioning should be as consistent as possible
	img_crop = pcv.crop(img, x = 500, y = 1500, h = 1600, w = 2600)
	# runs the classifier
	mask = pcv.naive_bayes_classifier(rgb_img=img_crop, pdf_file="./naive_bayes_pdfs.txt")
	#print('done')
	# Generate healthy, stressed, and combined whole plant masks
	maskH = pcv.fill(mask['Healthy'], size = 1000)
	maskS = pcv.fill(mask['Stressed'], size = 1000)
	combinedPlant = pcv.image_add(maskH, maskS)
	pcv.print_image(combinedPlant, masks + basename + '_mask.jpg') # save mask
	analysis_image = pcv.analyze.color(rgb_img=img_crop, labeled_mask=combinedPlant, n_labels=1, colorspaces='lab')
	# Extract LAB values from pcv.analyze.color
	l = np.array(pcv.outputs.observations['default_1']['lightness_frequencies']['value'])
	lS = np.array(pcv.outputs.observations['default_1']['lightness_frequencies']['label'])
	a = np.array(pcv.outputs.observations['default_1']['green-magenta_frequencies']['value'])
	aS = np.array(pcv.outputs.observations['default_1']['green-magenta_frequencies']['label'])
	b = np.array(pcv.outputs.observations['default_1']['blue-yellow_frequencies']['value'])
	bS = np.array(pcv.outputs.observations['default_1']['blue-yellow_frequencies']['label'])

	# Calculate centers of mass
	comL = np.sum(l * lS) / np.sum(l)
	comA = np.sum(a * aS) / np.sum(a)
	comB = np.sum(b * bS) / np.sum(b)

	# Calculate areas
	stressArea = np.count_nonzero(maskS)
	healthyArea = np.count_nonzero(maskH)
	rat = stressArea / (healthyArea + stressArea)

	return(healthyArea, stressArea, rat, comL, comA, comB)

def analyze_directory(imgDir, maskDir, resultsDir):
	if not os.path.exists(maskDir):
		os.makedirs(maskDir)
	if not os.path.exists(resultsDir):
		os.makedirs(resultsDir)
	rs = []
	for file in os.listdir(imgDir):
		if file.lower().endswith(".jpg"):
			#print(f"Image: {file}")
			imname = imgDir + file
			filename = file
			outpath = resultsDir
			basename = filename.rsplit( ".", 1 )[ 0 ]
			date = basename.rsplit("_", 4)[0]
			genotype = basename.rsplit("_", 4)[1] + "_" + basename.rsplit("_", 4)[2] + "_" + basename.rsplit("_", 4)[3]
			treatment = basename.rsplit("_", 4)[4]
			healthyArea, stressArea, perc, L, A, B = healthy_stress_ratio(imname, basename, maskDir)
			rs.append(
				{
					"Genotype": genotype,
					"Date": date,
					"Treatment": treatment,
					"Area": healthyArea + stressArea,
					"HealthyArea": healthyArea,
					"StressedArea": stressArea,
					"PercentStressed": perc,
					"L": L,
					"A": A,
					"B": B
				}
			)

	out = pd.DataFrame(rs)

	## You will need to change the dates here based on your experimental dates,
	## otherwise we can amend the filenames to include a day parameter
	date_to_day = {"3june2025": 13, "10june2025": 20, "3june2025_2270": 13, "10june2025_2270":20}
	out["Day"] = out["Date"].map(date_to_day)
	out.to_csv(resultsDir + 'healthy_stressed_results.csv')

	''' This next section will generate the plots for assessing the ratio of stressed to healthy
	area and the directional color change'''

	# Melt the dataframe for plotting area
	df_melted = pd.melt(
		out,
		id_vars=['Genotype', 'Treatment', 'Day'],
		value_vars=['HealthyArea', 'StressedArea'],  # No spaces in your column names
		var_name='HealthStatus',
		value_name='PixelArea'  # Renamed to avoid confusion with 'Area' column
	)


	# 2. Create combined group identifier
	df_melted['Group'] = df_melted['Treatment'] + '_Day' + df_melted['Day'].astype(str)

	# 3. Create numeric x-axis positions for precise control
	groups = sorted(df_melted['Group'].unique())
	genotypes = sorted(df_melted['Genotype'].unique())
	x_positions = np.arange(len(genotypes) * len(groups))
	df_melted['x_pos'] = df_melted.apply(
		lambda row: genotypes.index(row['Genotype']) * len(groups) + groups.index(row['Group']),
		axis=1
	)

	# 4. Plot setup
	plt.figure(figsize=(14, 8))
	ax = plt.gca()

	# Plot healthy areas first (bottom)
	healthy = df_melted[df_melted['HealthStatus'] == 'HealthyArea']
	sns.barplot(
		x='x_pos',
		y='PixelArea',
		data=healthy,
		color='#66c2a5',  # Teal
		ax=ax,
		errorbar=None
	)

	# Plot stressed areas on top
	stressed = df_melted[df_melted['HealthStatus'] == 'StressedArea']
	sns.barplot(
		x='x_pos',
		y='PixelArea',
		data=stressed,
		bottom=healthy.groupby('x_pos')['PixelArea'].sum().values,
		color='#fc8d62',  # Orange
		ax=ax,
		errorbar=None
	)

	# 5. Custom x-axis labeling
	tick_positions = [i*len(groups) + (len(groups)-1)/2 for i in range(len(genotypes))]
	ax.set_xticks(tick_positions)
	ax.set_xticklabels(genotypes)

	# Add group labels
	for i, group in enumerate(groups):
		plt.text(i, -0.1*df_melted['PixelArea'].max(), group,
				ha='center', va='top', rotation=45)

	# 6. Custom legend
	from matplotlib.patches import Patch
	legend_elements = [
		Patch(facecolor='#66c2a5', label='Healthy'),
		Patch(facecolor='#fc8d62', label='Stressed')
	]
	ax.legend(handles=legend_elements)

	# 7. Final touches
	plt.title('Plant Stress by Genotype, Treatment and Day')
	plt.ylabel('Pixel Area')
	plt.xlabel('Genotype')
	plt.tight_layout()
	plt.savefig(resultsDir + 'healthy_stressed_area.svg')
	#plt.show()
	return(out)


oot = analyze_directory(args.inputDir, args.masks, args.resultsDir)
