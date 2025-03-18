# MESCNN: Magnitude Estimation System Based on Convolutional Neural Networks
## 1. System Functionality
MESCNN is a fast magnitude estimation system that performs magnitude estimation on user-uploaded seismic acceleration records using an embedded deep learning model. It provides visualized estimation results.
## 2. Environment Requirements
- Operating System: Windows
- Python: Version 3.9 or higher
- Dependencies: requests, geopy, flask, flask_cors, pandas, numpy, scipy, math, werkzeug, tensorflow, pymysql, dbutils
- Database: MySQL (pymysql and dbutils packages required)
- Frontend and API: See /frontend directory
- Local Storage: The seismic records uploaded by the user are saved to a custom path through /code/app.py
## 3. Basic Files
Users need to prepare the following basic data:
- Original seismic records
Example data can be found in the /backend/example/EQrecords directory.
## 4. Usage
### 4.1 Upload Event
- Main Program: /code/app.py
- Function: Provides an API for frontend-backend interaction, for users top upload earthquake records.
- For example:30 sample seismic records can be found  in /example/EQrecords directory, user can upload these records and estimate magnitude.
- Deployment: Configure the MySQL connection and run /code/app.py
### 4.2 Estimate Magnitude
- Main Program: /code/app.py
- Function: Provides an API to invoke the magnitude estimation deep learning model. After the user uploads the seismic records, the estimated magnitude results will be returned.
- Deployment: Configure the MySQL connection and run /code/app.py
## 5. API and Frontend
- Function: app.py provides all the APIs for frontend-backend interaction, and Frontend provides an intuitive display of magnitude estimation.
- Deployment: app.py can be found in /code  directory, Frontend related code can be found in /frontend Relevant programs can be found in /frontend directories.
## 6. Supporting Literature
- WANG Z F, LIAO J A, WANG Y W, et al. A fast magnitude estimation method based on deep convolutional neural networks[J]. Chinese Journal of Geophysics, 2023, 66(1): 272-288.
- Dongliang W, Yanwei W, Zifa W, et al. A fast estimation method of earthquake magnitude based on convolutional neural networks[J]. Acta Seismologica Sinica, 2022, 44(2): 316-326.
 
