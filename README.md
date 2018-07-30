# Project METAR_TAF
INPE - Data Science Project   
CAP394 Introduction to Data Science - 2018.2

The project content in this repository is an analyse of observations and forecasts aerodrome reports. This project focus on analyses and comparison of METAR (Meteorological Aerodrome Report) and TAF (Terminal Aerodrome Forecast) reports from Brazil aerodrome. The project is all developed in python 3 and its libraries.

### RAW DATA

The raw data of METAR and TAF messages are avaiable on [REDEMET](https://www.redemet.aer.mil.br/), the Meteorology Network of the Brazil Aeronautical Command. REDEMET provides some [tools](https://www.redemet.aer.mil.br/?i=facilidades&p=api-redemet), such as APIs, scripsts and WGET, for users download such messages. REDEMET maintains meteorological data for all aerodromes in Brazil from a few years ago to current time.

### 01- Data cleaning and preparation

The frist product of this project were the metar and taf data cleaned and organized. METAR and TAF messages were cleaned and organized by hour for each airport. They were organized in .csv files, where each file have dada of an specific airport and year. The information extracted from these messages was wind (direction and speed), weather phenom, horizontal visibility, groups of clouds, temperature and pressure.

The library used to clean the data is based on regex operation and the .csv files were generated using pandas library. The python library was developed in a way that it was prepared to additions in data extrated process. 

#### Hypotheses
During the cleaning on raw data some hypotheses and aproximation were used.
* Time was approximated to the nearest hour, eliminating the minutes;
* Newer messages replace the older one;

### 02- EDA	

### 03- Results	
