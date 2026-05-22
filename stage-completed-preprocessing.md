# Project goal
This is a pre-processing / data-cleaning and data analysis project. It analysis surveys responses regarding AI usage by students and teachers from 4 countries in europe, namely
* Italy 
* Spain 
* Slovenia
* Turkey

## Current status
Data Cleaning and Preparation. We are half way through the data preparation. The final goal of this phase is to merge all the responses of the different languages into a single file in english
I will update this part as we move forward. Might have additions on the stack, for the moment stick to data preparation.

## Stack
* Python 3.13.5 in Conda
* always use conda venv named "sail"
* launch scripts directly in the terminal

## Data peculiarities and organization
* Data contains responses from different languages, use at least utf8 encoding that supports the 4 languages
* Always remember the surveys come from 4 parallel surveys in their countries, there were some issues in alligning the surveys schemas, always recheck your assumptions
* Inside each survey, some questions with semantically the same answer options might have been transcribed in the surveys with slightly different wording, that is why we need to pass through a map that reflects specifically each question and aligns then with the english master
* Most of the questions contain closed end, ordered options like likert scale
* The data folder contains is organized as following
    ** students
        *** Students Responses - es.csv : csv file containing responses from spain, the language is catalan
        *** Students Responses - it.csv : csv file containing responses from italian, the language is italian
        *** Students Responses - sl.csv : csv file containing responses from slovenian, the language is slovenian
        *** Students Responses - tu.csv : csv file containing responses from turkey, the language is turkish

        *** students-responses-map folder
        This folder contains a set of files that will act as mapping from the different languages to our master language which is english. 
        English and Italian should be already final but might contain small errors. All the other files are draft files we need to elaborate in the preprocessing phase.
            *** Students Responses Map - en.csv
            *** Students Responses Map - it.csv
            *** draft - Students Responses Map - es.csv
            *** draft - Students Responses Map - sl.csv
            *** draft - Students Responses Map - tu.csv
* List of the columns that contain open text (like "other" option or equivalently in different language) Indexes start from 0
    ** 1. Country. Index=1
    ** 2.2 Primary use case. Index=6
    ** 2.4 General Feeling. Index=15



# Current goals
* We need to produce the response map of es, sl and tu languages
* Each response map file should contain for each column (which respresent a question, plus the initial timestamp)
    ** the possible answer options associated to that question
    ** they should follow their semantic order
    ** they should match exactly the value in the associated set of responses in that language and match semantically the same element in the same position in the translation i've put in the english language / master map
* Once we have all the language maps we will be able to merge all in a single english file. I will change the current goals when we are ready.




