# REST API for HackNU 2022

This project is a bare-bones API server designed to solve the problem of HackNU 2022 hackathon prepared by the Beeline BigData team. The server recreate dependencies for each final processed column after running src folder's scripts. It does it by parsing scripts' physical schemes. 

The server return a json message with following structure: <br />
<pre>
[{  id :  ..., 
   filename : ..., 
   code : ..., 
   graph : ... 
 } 
 ... 
] 
</pre>

## Getting Started with App

1. First of all, clone project in the working directory `git clone ...`; <br />
2. Then go into the working folder `cd Web_hack`; <br />
3. Use the `pip3 install -r requirements.txt` command to install all of the Python modules and packages listed in the requirements.txt file; <br />
4. Upload the physical schemes of the scripts that need to be parsed to the folder `hacknu-api/parser/src`. <br />

## Running the server

Run `python3 manage.py runserver` to run the server locally.

## Learn More

Go to 'https://github.com/wertypotom/graphs' to see visual representation of the graph.
