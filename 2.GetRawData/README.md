# Project METAR_TAF GetRawData

## Source of raw metar/taf data
The raw data of METAR and TAF messages are avaiable on [REDEMET](https://www.redemet.aer.mil.br/), the Meteorology Network of the Brazil Aeronautical Command. REDEMET provides some [tools](https://www.redemet.aer.mil.br/?i=facilidades&p=api-redemet), such as APIs, scripsts and WGET, for users download such messages. REDEMET maintains meteorological data for all aerodromes in Brazil from a few years ago to current time.

## How to use
This project uses the script available in REDEMET to download raw data. Some fields in this script must be filled in as the script in this folder. This script is the same one available from REDEMET (2018/08/01), with fields filled in to the default used by the data cleanup phase used in this project. The airports of Brazil were divided into two groups, one composed only of airports in the southeast region and the other with airports in other regions. This division occurred because of the limits of the REDEMET system.

Steps:
* Change the mesage type field (metar,taf,...): tipos_de_mensagem=**"taf"**
* Change the locations field: localidades_ou_sinoticos=**"SBBR,SBGR,SBGL,SBPA,SBRF,SBEG,SBBE"**;
* The two groups of Brazilian airports are ready in the comments (southeast and others regions);
* Change the output file (.txt) name, it is recommend to use the following pattern : arquivo_resultado=**"taf2015outrasregioes.txt"**;
* Change the begin data: data_inicio=**"20150101"**;

Warning: It take some time to get an year data of all brasilian airports. 
More information about that on timeINFO.txt;