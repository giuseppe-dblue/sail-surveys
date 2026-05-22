# Project goal
This is a data analysis project. It analayzes surveys responses regarding AI usage by students and teachers from 4 countries in europe, namely
* Italy 
* Spain 
* Slovenia
* Turkey

## History
Data was spread in different files, each one of them with a different language.
Data cleaning and preparation was performed with Claude Code. We prepared language maps that allowed to merge all the different files into a master english file.


## Current status
We now target the Students Responses - merged-en.csv file for running the full analysis. We will divide it into 2 layers of analysis:
* a homogeneous, horizontal descriptive analysis of the answers.
* analysis of specific aspects/questions that might involve looking at correlations of pairs or set of questions
I will need to provide charts and brief comments to my project partners, therefore we need to find a light library to produce the charts, and I will need to be able to quickly copy text of the comments/interpretations, so, no text embedded in the images for each image. If we need to enrich the stack, maybe to inlcude javascript first propose to me some options and brainstorm.


## Stack
* Python 3.13.5 in Conda
* always use conda venv named "sail"


## Data peculiarities and organization
* All data is in the data/students folder
* Full dataset is: data/students/Students Responses - merged-en.csv
* Read in utf-8
* Questionnaire Schema is in: students/students-responses-map/Students Responses Map - en.csv


* List of the columns that contain open text (like "other" option or equivalently in different language) Indexes start from 0
    ** 1. Country. Index=1
    ** 2.2 Primary use case. Index=6
    ** 2.4 General Feeling. Index=15



# Current goals
* Analyse the questions in a repeatable way: produce the code for the analysis, not just the result
* First objective is the descriptive analysis that we can break and combine with the following groups
    * by country: question 1.Country, Index:1
    * by gender: question 2.Gender, Index 2
    * by Grade/year: question 3.Grade/Year of Study, Index 3
* We will define specific analysis later on

