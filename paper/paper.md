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
A single electrochemical experiment can generate on the order of up to ten thousand data points, and several individual experiments are frequently used to fully assess a single cell. Electrochemical experiments also generate large quantities of raw data which require extensive preprocessing before the data can be used to completely assess the performance of an electrochemical device. Processing and analyzing the data from a single experiment using conventional methods often takes close to an hour, so analyzing these electrochemical data can cause a bottleneck in the research process. Manually processing this data also introduces unnecessary human error into the results, resulting in increased variation both between individual researchers and between research groups within the electrochemical field.4 Therefore, an application which efficiently processes electrochemical data will standardize and expedite the analysis of data generated from electrochemical experiments.

# Statement of need

`Gala` is an Astropy-affiliated Python package for galactic dynamics. Python
enables wrapping low-level languages (e.g., C) for speed without losing
flexibility or ease-of-use in the user-interface. The API for `Gala` was
designed to provide a class-based and user-friendly interface to fast (C or
Cython-optimized) implementations of common operations such as gravitational
potential and force evaluation, orbit integration, dynamical transformations,
and chaos indicators for nonlinear dynamics. `Gala` also relies heavily on and
interfaces well with the implementations of physical units and astronomical
coordinate systems in the `Astropy` package [@astropy] (`astropy.units` and
`astropy.coordinates`).

`Gala` was designed to be used by both astronomical researchers and by
students in courses on gravitational dynamics or astronomy. It has already been
used in a number of scientific publications [@Pearson:2017] and has also been
used in graduate courses on Galactic dynamics to, e.g., provide interactive
visualizations of textbook material [@Binney:2008]. The combination of speed,
design, and support for Astropy functionality in `Gala` will enable exciting
scientific explorations of forthcoming data releases from the *Gaia* mission
[@gaia] by students and experts alike.

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