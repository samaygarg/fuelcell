---
title: 'fuelcell: A Python package and graphical user interface for electrochemical data analysis'
tags:
  - Python
  - electrochemistry
  - chemical engineering
  - fuel cells
  - electrolysis
authors:
  - name: Samay Garg
    affiliation: "1, 2"
  - name: Julie C. Fornaciari
    affiliation: "1, 2"
  - name: Adam Z. Weber
    affiliation: 1
  - name: Nemanja Danilovic
  	affiliation: 1
affiliations:
 - name: Energy Storage and Distributed Resources Division, Lawrence Berkeley National Laboratory, Berkeley, CA 94720
   index: 1
 - name: Department of Chemical and Biomolecular Engineering, University of California Berkeley, Berkeley CA 94720
   index: 2
date: 10 November 2020
bibliography: paper.bib
---

# Overview

`fuelcell` is a Python package designed to standardize and streamline the anlysis of electrochemical data. This package includes modules for data processing and data visualization, as well as a graphical user interface (GUI) for interactive use.

# Introduction

As the demand for sustainable, carbon-free electricity increases globally, development of electrochemical energy conversion devices is increasing rapidly.  These devices include fuel cells, flow batteries, and water electrolysis cells. A wide range of diagnostic experiments is used to assess the performance, durability, and efficiency of electrochemical devices.1,2 Among the most commonly used techniques are chronopotentiometry (CP), chronoamperometry (CA), cyclic voltammetry (CV), linear sweep voltammetry (LSV), and electrochemical impedance spectroscopy (EIS) experiments.1-3 Although these experimental protocols have been well-established in the field of electrochemistry, the protocols for analyzing electrochemical data have not been clearly standardized. Standardizing electrochemical data analysis will also aid in applying machine learning frameworks to extract valuable information from electrochemical data sets. 

# Statement of need
A single electrochemical experiment can generate on the order of ten thousand data points, and several individual experiments are frequently used to assess a single cell. Electrochemical experiments also generate large quantities of raw data, which require extensive preprocessing before the data can be used to assess the performance of an electrochemical device completely. Processing and analyzing the data from a single experiment using conventional methods often is a bottleneck and time consuming. Manually processing this data also introduces unnecessary human error into the results, resulting in increased variation both between individual researchers and between research groups within the electrochemical field.4 Therefore, an application that efficiently processes electrochemical data will standardize and expedite the analysis of data generated from electrochemical experiments.

# Functionality

fuelcell includes modules for both data processing and visualization to enable a smooth, efficient workflow from raw data to publication-ready figures. These modules can be imported and used programmatically as a standard Python package, and fuelcell also includes a standalone GUI that allows users with little or no programming experience to utilize these modules.  fuelcell also serves as a platform that can be expanded to facilitate new and more advanced techniques as the needs of the electrochemical community evolve.
## fuelcell.datums
Every experiment requires a unique protocol to process the raw experimental data, so the datums module contains experiment-specific functions to read and process data for each experiment. Currently, functions to process CV, CP, CA, LSV, and EIS data are included fuelcell, and new protocols can be added to the project by opening an issue on github. The complexity of these processing protocols varies depending on the experiment, and the specific data processing steps carried out for each experiment are detailed in the documentation. The datums module also includes functions to determine the Tafel slope and exchange current density from LSV data as well as to extract the high-frequency resistance (HFR) value from EIS data.3,4
## fuelcell.visuals
The visuals module includes functions to generate visualizations, which are commonly used in the electrochemical community. fuelcell currently includes functions to generate polarization curves, cyclic voltammograms, linear sweep voltammograms, and Nyquist plots (Fig. 1). This module is built around the matplotlib library, which allows for highly customizable visualizations. The visuals module is designed to integrate both seamlessly with the datums module and to function as an independent module that can be incorporated into an existing workflow.
![Examples of figures created using functions in fuelcell.visuals. (a) Polarization curves generated using data from CP experiments. (b) Cyclic voltammograms. (c) LSV data with the Tafel fit overlaid in yellow. (d) EIS data with the HFR value calculated using both a semicircle fit and a linear fit.\label{fig:1}](fig1.png)
## fuelcell_gui
The GUI is included in the standard fuelcell installation, but it can also be installed independently as a single executable file (Windows and MacOS) that includes all necessary dependencies.  The GUI also enables users to interactively create and customize visualizations without being familiar with the ins and outs of the matplotlib library. This GUI has been shown to greatly reduce the time required to process electrochemical data, with researchers using the program reporting that it reduces the time required to process data from testing four cells from close to one hour to about five minutes.
![: Data visualization tab of the GUI. (a) Polarization curves generated using data from CP experiments. (b) Cyclic voltammograms. (c) LSV data with the Tafel fit overlaid in yellow. (d) EIS data with the HFR value calculated using both a semicircle fit and a linear fit.\label{fig:2}](fig2.png)



# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References