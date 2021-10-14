<h1>SERVER MIGRATION DOCUMENT </h1>
<h3>PUBMED/CT DATABASE BUILDING SCRIPTS</h3>

Pubmed - Downloader
[ run.py, ap2.py, pubmed_docs ]

The pubmed downloader is python script which downloads the user requested files from the pubmed database according to the arguments specified in the shell query. After writing `python3 run.py` there are 2 arguments - `baseline` and `daily` which visit 2 different places in the pubmed database and downloads, as the name suggests, ‘baseline’ and ‘daily update files’. The second argument - `range` is optional. By specifying this keyword the program knows that it needs to download a range of files from the next few arguments that are specified. The next argument is the number of the file. If the user chose to put `range` in the arguments before the program will accept two file names [the starting the ending files, both included]. Otherwise the program will download and parse the names of the space separated files listed.

Pubmed - Parser
[ file_parser_new.py, mysql db, tables and workbench ]

The file parser will create a list of all the files in the updatefiles or the baseline folder and establish a connection with the mysql server. It will then go through every file, parsing its contents and updating the mysql table until it reaches the last file. After that is done, it will automatically create a log entry in the specified file for the session that took place.

Steps: 
<ul>
  <li>[file_parser_new.py]</li>

Change LOGFILE_PATH and FILE_PATH to appropriate file paths in the server
Change BASE_DIR_NAME and DAILY_DIR_NAME in `folder_select()` to appropriate file paths in the server.

  <li>[ap2.py]</li>

Change FILE_PATH to an appropriate file path in the server.

  <li>[run.py]</li>

Change LOGFILE_PATH and FILE_PATH to appropriate file paths in the server.

  <li>[Dependencies]</li>

Install all the dependencies from requirements.txt by running the command `pip install -r requirements.txt` . 
You still might need to install mysql-connector separately, depending on whether the next few steps are successful or not. If they are not then python will tell you what to install.

  <li>[Main]</li>

  <li>For one file: </li>
  
`python3 run.py [baseline / daily] xxxx`
  
  <li>For a range of files:</li>
  
`python3 run.py [baseline / daily] range xxxx`
  
  <li>For a selection of files:</li>
  
`python3 run.py [baseline / daily] xxxx xxxx xxxx …`
  
 </ul>

 <h3>INDEXING</h3>

 To index the documents in the database for elasticsearch to use, we use Logstash. Logstash utilizes a configuration file of the format `.conf` to connect to the database and creates a mapping/index of all the documents. <br>
 
 Use `logstash_full_index.conf` to index the database. The logstash executable file resides in the `/usr/share/logstash/bin/` directory. <br>

 Things to keep in mind:
 
 <ul>
    <li> jdbc_user: this is the mysql database user. </li>
    <li> jdbc_password: this is the password of the mysql database user. </li>
    <li> statement: this is the mysql command which tells logstash to track the specified columns of the table in the database. </li>
    <li> tracking_column: this is the primary key of the table. </li>
    <li> index: this is the name of the index that will be created. </li>
</ul>

To run the configuration file:

<ul>
    <li>Running in the foreground of the current shell: </li>

    `/usr/share/logstash/bin/logstash -f logstash_full_index.conf`

<li>Running in the background: </li>

    `nohup /usr/share/logstash/bin/logstash -f logstash_full_index.conf &`

</ul>

To check existing logstash indices: `curl logstash:9200/_cat/indices`<br>
To delete an existing logstash index: `curl -XDELETE 'localhost:9200/[index_name]'`<br>
