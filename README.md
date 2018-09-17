# Project METAR_TAF
INPE - Data Science Project   
CAP394 Introduction to Data Science - 2018.2

The project in this repository is an analysis of aerodrome observations and forecasts reports. This project focus on analyses and comparisons of METAR (Meteorological Aerodrome Report) and TAF (Terminal Aerodrome Forecast) reports from southeast Brazil aerodromes. The project is fully developed on python 3 and its libraries.

### RAW DATA

The raw data of METAR and TAF messages are avaiable on [REDEMET](https://www.redemet.aer.mil.br/), the Meteorology Network of the Brazilian Aeronautical Command. REDEMET provides some [tools](https://www.redemet.aer.mil.br/?i=facilidades&p=api-redemet), such as APIs, scripts and WGET, for users to download such messages. REDEMET maintains meteorological data for all aerodromes in Brazil from a few years ago to current time.

### 01- Data cleaning and preparation

The first product of this project was the METAR and TAF data cleaned and organized. METAR and TAF messages were cleaned and organized by hour for each airport. They were organized in .csv files, where each file have dada of an specific airport and year. The information extracted from these messages to .csv files were wind speed, thunderstorm (TS), hail (>5mm, GR), small hail /snow pellets (<5mm, GS), cumulonimbus (CB) and towering cumulus (TCU).

The library used to clean the data is based on regex operation and the .csv files were generated using pandas library. The python library was developed in a way that it was prepared to receive additions in data extrated process. All METAR and TAF information are already split in objects as its own classes, such as wind (direction and speed), weather phenomenona, horizontal visibility, groups of clouds, temperature and pressure.

#### Hypotheses
During the cleaning on raw data some hypotheses and aproximations were used.
* Time was approximated to the nearest hour, eliminating the minutes;
* Newer messages replace the older ones;
* METAR with wind GUST use GUST wind speed as wind speed, as it is bigger;
* The raw data must be in this format '2015010100 - raw_message=' (format avaiable by REDEMET APIs);
* TAF BECMG uses previous data to fill in blank fields;
* TAF FM overlaps the previous data, so blanks mean that no phenomenon happened;
* NSW only fills "weather phenomenon" with "no weather";
* NSC only fills "groups of clouds" with "no clouds";

### 02- Exploratory Data Analysis (EDA)

The aim of data analysis was to evaluate the quality of TAF wind speed forecasting and to reveal any patterns regarding the accuracy of the forecasts. To achieve this, the error measurement RMSE was used. The RMSE was calculated on absolute mode and by wind speed scale. Also, some comparisons between the error measurement and the TS, TCU and CB phenomenona were verified. Only southeast Brazil airports were analysed, and the target was the Guarulhos  airport, because it is the most important Brazilian airport.      

### 03- Results	

The analysis shows that the absolute RMSE of SBGR airport, Guarulhos-Brazil, is 4.29 kt which seems good, but analysing this error by wind speed scale it increases with the wind speed, and when wind speed is higher than 15KT, it's error is higher than 9KT. 
The growth of the error shows some relations with the presence of TS and CB in METAR. No relation of the error with geografic characteristics or patterns were found. 

### 04- Future works

Suggestions:
 * Comparisons using wind direction variations;
 * Verifying relations between airport charateristics and its error;
 



