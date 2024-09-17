During my 8-week internship at Clermont Foot 63, I was tasked with creating an application offering information and data analysis on football club.
An overview of this application, available in both French and English, can be found in the repository.

To achieve this, I used Python and designed the application with Streamlit library. For data analysis, I imported raw data from Stats Bomb and Skill Corner API, two data football providers. I stored this raw data in an initial database (which I have added to the .gitignore file) created using the SQLite library, which allows for SQL queries in Python. Import programs can be found in the "Données brutes" folder.

After importing the data, I processed and stored it in the main database to generate or retain useful metrics. The data processing programs are located in the "Transformation data" folder.

Once the data processing was completed, I was responsible for creating interface/application to share relevant and meaningful football information. The Streamlit programs are located in the "Application_streamlit" folder.
