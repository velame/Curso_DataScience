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

#### HOW TO USE?

Steps:
* Place the raw data (.txt) of METAR and TAF messages on './input/raw_data/';
* Change the year variable on "db_generator.py" (e.g.: year = "2017");
* Run "db_generator.py"; 

Following this steps a .csv file of the year selected will be created on ./output directory for each airport on raw data.  

#### How to make additions in the data extration process?

Additions on .csv files fields can be done by changing the "db_generator.py" file. The "Taf.py" and "MetarModel.py" are responsible only for regex functions. 
These variables on DataBase on "db_generator.py" file are responsible for these .csv fields:
* intrphem  = ['wind', 'TS', 'GRGS', 'CB', 'TCU']
* colstruct = [ ('metar',intrphem), ('taf',intrphem) ]
* handlers  = { 'wind':getspeedwind,
                  'TS'  :getTS,
                  'GRGS':getGRGS,
                  'CB'  :getCB,
                  'TCU' :getTCU}
