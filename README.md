# SoccerMongoDB
Web Scraped/Parsed Soccer Data NOSQL MongoDB

Python program that prompts for which nations soccer league stats you want to upload to a mongodb database.
After selecting a country. A website http://www.football-data.co.uk/ that has soccer stats from the major leagues in Europe going back to the 1993/1994 season is scraped and parsed. This is done using Beautiful Soup.


![Capture](https://user-images.githubusercontent.com/62077185/106338703-78ec4800-6262-11eb-9d58-3aa36713d6ff.JPG)


After all csv files are found for the selected country, the csv files for each season are put into a pandas dataframe. This dataframe is then parsed and converted into json.
At this point the data is uploaded to a mongodb database. 
The database is called 'Soccer'.
The collection is named after the country selected. Ex 'Netherlands'

As you can see in the search below, all games for the 2003/2004 Arsenal Invincible Season are present (38 games in season)


![Capture3](https://user-images.githubusercontent.com/62077185/106338702-7853b180-6262-11eb-9ac3-43b254297ffc.JPG)
