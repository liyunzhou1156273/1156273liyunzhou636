from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect


app = Flask(__name__)
app.static_url_path='/static'

dbconn = None
connection = None

app.secret_key = 'your_secret_key'

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'user' in request.form:
            return redirect(url_for('home'))
        elif 'admin' in request.form:
            return redirect(url_for('admin'))
    
    return render_template('login.html')

@app.route("/home")  # public user home page for login. 
def home():
    return render_template("base.html")

@app.route("/listdrivers")
def listdrivers():
    connection = getCursor() 

    # get driver information along with car details
    connection.execute("SELECT driver_id, CONCAT(surname,' ',first_name) AS Name,date_of_birth,age,caregiver,car.model,car.drive_class\
                       FROM driver\
                       LEFT JOIN car ON driver.car=car.car_num\
                       ORDER BY surname ASC, first_name ASC;")
    driverList = connection.fetchall()
    return render_template("driverlist.html", driver_list = driverList)    


@app.route("/rundetails", methods=["GET"])
def rundetails():
    # Get parameter from url link
    drivername=request.args.get('drivername')
    connection = getCursor()
    
    #get detailed run information for a specific driver.
    connection.execute("SELECT * FROM (\
                       SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class,\
                       round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals\
                       FROM run\
                       LEFT JOIN driver ON run.dr_id = driver.driver_id\
                       LEFT JOIN course ON run.crs_id = course.course_id\
                       LEFT JOIN car ON driver.car = car.car_num) AS subquery\
                       WHERE subquery.drivers = %s;", (drivername,))
    driver_result = connection.fetchall()
    return render_template("rundetails.html",driver_name=drivername,driver_result=driver_result)    

@app.route("/listalldetails", methods=["GET","POST"])
def listalldetails():
    if request.method == "GET":
        connection = getCursor()
        #get a list of all drivers and their basic information as it can get unique driver_id to select option bar.
        connection.execute("SELECT * FROM driver;")
        driver_result = connection.fetchall()


        connection = getCursor()
        #get detailed run information for all drivers.
        connection.execute("SELECT * FROM (\
            SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class,\
            round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals\
            FROM run\
            LEFT JOIN driver ON run.dr_id = driver.driver_id\
            LEFT JOIN course ON run.crs_id = course.course_id\
            LEFT JOIN car ON driver.car = car.car_num) AS subquery;")
        run_result = connection.fetchall()

        return render_template("allrundetails.html", driver_result=driver_result, run_result=run_result)


    else:
        driverid = request.form.get('driver')

        try:
            driverid = int(driverid)

            # Query all drivers for the option bar.
            connection = getCursor()
            connection.execute("SELECT * FROM driver;")
            driver_result = connection.fetchall()

            #get detailed run information for the selected driver.
            connection = getCursor()
            connection.execute("SELECT * FROM (\
                SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class, \
                round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals \
                FROM run \
                LEFT JOIN driver ON run.dr_id = driver.driver_id \
                LEFT JOIN course ON run.crs_id = course.course_id \
                LEFT JOIN car ON driver.car = car.car_num) AS subquery \
                WHERE dr_id=%s;", (driverid,))
            run_result = connection.fetchall()
            return render_template("allrundetails.html", driverid=driverid, run_result=run_result, driver_result=driver_result)
        
        #Handle the case where the 'driver' parameter is not a valid integer. if user select the 'Select A driver'
        except ValueError:
            connection = getCursor()
            connection.execute("SELECT * FROM driver;")
            driver_result = connection.fetchall()

            connection = getCursor()
            connection.execute("SELECT * FROM (\
                SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class, \
                round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals \
                FROM run \
                LEFT JOIN driver ON run.dr_id = driver.driver_id \
                LEFT JOIN course ON run.crs_id = course.course_id \
                LEFT JOIN car ON driver.car = car.car_num) AS subquery;")
            run_result = connection.fetchall()

            return render_template("allrundetails.html", driverid=driverid, run_result=run_result,driver_result=driver_result)
        

@app.route("/listcourses")
def listcourses():
    connection = getCursor()

    #get all courses from the database.
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list = courseList)

@app.route("/listoverall")
def listoverall():
    connection = getCursor()

    #compute and fetch overall results for drivers.
    connection.execute("SELECT A.ID, A.DriverName, A.Car, \
                       COALESCE(B.courseA,'dnf') AS courseA, \
                       COALESCE(B.courseB,'dnf') AS courseB,\
                       COALESCE(B.courseC,'dnf') AS courseC,\
                       COALESCE(B.courseD,'dnf') AS courseD,\
                       COALESCE(B.courseE,'dnf') AS courseE,\
                       COALESCE(B.courseF,'dnf') AS courseF,\
                       COALESCE(B.Overall, 'NQ') AS Overall\
                       FROM (\
                       SELECT driver_id AS ID, CONCAT(first_name,' ', surname, \
                       CASE \
                       WHEN 12< age < 25 THEN ' (J)'\
                       ELSE ''\
                       END) AS DriverName, car.model AS Car\
                       FROM driver\
                       LEFT JOIN car ON driver.car=car.car_num) AS A\
                       JOIN \
                       (SELECT dr_id AS ID,\
                       round(MAX(CASE WHEN crs_id = 'A' THEN total END),2) AS courseA,\
                       round(MAX(CASE WHEN crs_id = 'B' THEN total END),2) AS courseB,\
                       round(MAX(CASE WHEN crs_id = 'C' THEN total END),2) AS courseC,\
                       round(MAX(CASE WHEN crs_id = 'D' THEN total END),2) AS courseD,\
                       round(MAX(CASE WHEN crs_id = 'E' THEN total END),2) AS courseE,\
                       round(MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS courseF,\
                       round(MAX(CASE WHEN crs_id = 'A' THEN total END) + MAX(CASE WHEN crs_id = 'B' THEN total END) +\
                       MAX(CASE WHEN crs_id = 'C' THEN total END) + MAX(CASE WHEN crs_id = 'D' THEN total END) +\
                       MAX(CASE WHEN crs_id = 'E' THEN total END) + MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS Overall\
                       FROM ( \
                       SELECT dr_id, \
                       crs_id,\
                       round(MIN(round((seconds + IFNULL(cones,0)*5 + IFNULL(wd,0) * 10),2)),2)  AS total\
                       FROM run\
                       WHERE seconds IS NOT NULL\
                       GROUP BY dr_id, crs_id) AS subquery\
                       GROUP BY dr_id) AS B ON A.ID=B.ID\
                       ORDER BY Overall;")
    overallList = connection.fetchall()
    print(overallList)
    return render_template("overallresults.html", overallList = overallList)    

@app.route("/showgraph")
def showgraph():
    connection = getCursor()

    #get the top 5 drivers overall, ordered by their final results.
    connection.execute("SELECT CONCAT(A.ID,' ', A.DriverName) AS Dnames\
                       FROM (SELECT driver_id AS ID, CONCAT(first_name,' ', surname,\
                       CASE \
                       WHEN 12< age < 25 THEN ' (J)'\
                       ELSE ''\
                       END) AS DriverName, car.model AS Car\
                       FROM driver\
                       LEFT JOIN car ON driver.car=car.car_num) AS A\
                       JOIN \
                       (SELECT dr_id AS ID,\
                       round(MAX(CASE WHEN crs_id = 'A' THEN total END),2) AS courseA,\
                       round(MAX(CASE WHEN crs_id = 'B' THEN total END),2) AS courseB,\
                       round(MAX(CASE WHEN crs_id = 'C' THEN total END),2) AS courseC,\
                       round(MAX(CASE WHEN crs_id = 'D' THEN total END),2) AS courseD,\
                       round(MAX(CASE WHEN crs_id = 'E' THEN total END),2) AS courseE,\
                       round(MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS courseF,\
                       round(MAX(CASE WHEN crs_id = 'A' THEN total END) + MAX(CASE WHEN crs_id = 'B' THEN total END) +\
                       MAX(CASE WHEN crs_id = 'C' THEN total END) + MAX(CASE WHEN crs_id = 'D' THEN total END) +\
                       MAX(CASE WHEN crs_id = 'E' THEN total END) + MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS Overall\
                       FROM ( \
                       SELECT dr_id, crs_id,\
                       round(MIN(round((seconds + IFNULL(cones,0)*5 + IFNULL(wd,0) * 10),2)),2)  AS total\
                       FROM run\
                       WHERE seconds IS NOT NULL\
                       GROUP BY dr_id, crs_id\
                       ) AS subquery\
                       GROUP BY dr_id) AS B ON A.ID=B.ID\
                       ORDER BY Overall IS NULL, Overall DESC LIMIT 5;")
    # Fetch the top 5 drivers' names and construct a list.
    bestDriverList=connection.fetchall()
  
    name_list=[]
    for i in bestDriverList:
        name_list.append(i[0])
    
    
    #get the overall results of the top 5 drivers.
    connection.execute("SELECT Overall\
                    FROM (SELECT driver_id AS ID, CONCAT(first_name,' ', surname,\
                    CASE \
                    WHEN 12< age < 25 THEN ' (J)'\
                    ELSE ''\
                    END) AS DriverName, car.model AS Car\
                    FROM driver\
                    LEFT JOIN car ON driver.car=car.car_num) AS A\
                    JOIN \
                    (SELECT dr_id AS ID,\
                    round(MAX(CASE WHEN crs_id = 'A' THEN total END),2) AS courseA,\
                    round(MAX(CASE WHEN crs_id = 'B' THEN total END),2) AS courseB,\
                    round(MAX(CASE WHEN crs_id = 'C' THEN total END),2) AS courseC,\
                    round(MAX(CASE WHEN crs_id = 'D' THEN total END),2) AS courseD,\
                    round(MAX(CASE WHEN crs_id = 'E' THEN total END),2) AS courseE,\
                    round(MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS courseF,\
                    round(MAX(CASE WHEN crs_id = 'A' THEN total END) + MAX(CASE WHEN crs_id = 'B' THEN total END) +\
                    MAX(CASE WHEN crs_id = 'C' THEN total END) + MAX(CASE WHEN crs_id = 'D' THEN total END) +\
                    MAX(CASE WHEN crs_id = 'E' THEN total END) + MAX(CASE WHEN crs_id = 'F' THEN total END),2) AS Overall\
                    FROM ( \
                    SELECT dr_id, crs_id,\
                    round(MIN(round((seconds + IFNULL(cones,0)*5 + IFNULL(wd,0) * 10),2)),2)  AS total\
                    FROM run\
                    WHERE seconds IS NOT NULL\
                    GROUP BY dr_id, crs_id\
                    ) AS subquery\
                    GROUP BY dr_id) AS B ON A.ID=B.ID\
                    ORDER BY Overall IS NULL, Overall DESC LIMIT 5;")
     # Fetch the overall results of the top 5 drivers and construct a list.
    resultsList=connection.fetchall() 
    value_list=[]
    for i in resultsList:
        value_list.append(i[0])

    return render_template("top5graph.html",name_list=name_list,value_list = value_list,resultsList=resultsList,bestDriverList=bestDriverList)

@app.route('/admin') #admin user enter only
def admin():
    return render_template("admin.html")

@app.route('/admin/listjuniordriver')
def listjuniordriver():
    connection = getCursor()

    #select junior drivers and their information.
    connection.execute("SELECT\
                       o.driver_id, \
                       IFNULL(CONCAT(n.first_name, ' ', n.surname), o.first_name) AS Name,\
                       o.date_of_birth,o.age,\
                       IFNULL(CONCAT(n2.first_name, ' ', n2.surname), ' ') AS Caregiver,\
                       o.car\
                       FROM driver AS o\
                       LEFT JOIN driver AS n ON o.driver_id = n.driver_id\
                       LEFT JOIN driver AS n2 ON o.caregiver = n2.driver_id\
                       WHERE o.age >=12 AND o.age<25\
                       ORDER BY \
                       CASE WHEN o.age IS NULL THEN 0 ELSE 1 END, \
                       o.age DESC,  \
                       IFNULL(n.surname, o.surname), \
                       IFNULL(n.first_name, o.first_name);")
    junior_driver_list = connection.fetchall()
    # print(junior_driver_list)
    return render_template("juniordriverlist.html",junior_driver_list=junior_driver_list)

@app.route('/admin/searchdriverlist')
def searchdriverlist():
    connection = getCursor()

    #select all drivers and their information, ordered by surname and first name.
    connection.execute("SELECT driver_id,surname,first_name,date_of_birth,age,caregiver,car FROM driver\
                       order by surname, first_name")
    driver_list = connection.fetchall()
    return render_template("searchdriverlist.html", driver_list = driver_list)

@app.route('/admin/searchrunlist')
def searchrunlist():
    connection = getCursor()

    #select detailed run information for all drivers.
    connection.execute("SELECT * FROM (\
        SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class,\
        round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals\
        FROM run\
        LEFT JOIN driver ON run.dr_id = driver.driver_id\
        LEFT JOIN course ON run.crs_id = course.course_id\
        LEFT JOIN car ON driver.car = car.car_num) AS subquery;")
    driverRun_list = connection.fetchall()
    return render_template("searchrunlist.html", driverRun_list = driverRun_list)

@app.route('/admin/searchdriverlist/filter', methods=["POST"])
def searchdriverlistfilter():
    drivers=request.form.get('driver') #  Get the search query for drivers from the form data.
    connection = getCursor()

    #select drivers whose surname or first name matches the search query.
    connection.execute("SELECT driver_id,surname,first_name,date_of_birth,age,caregiver,car FROM driver\
                        WHERE surname  Like  %s or first_name Like  %s\
                       order by surname, first_name;", (f'%{drivers}%',f'%{drivers}%',))
    driver_list = connection.fetchall()
    return render_template("searchdriverlist.html", driver_list = driver_list,drivers=drivers)

@app.route('/admin/searchrunlist/filter', methods=["POST"])
def searchrunlistfilter():
    drivers=request.form.get('driver') #  Get the search query for drivers from the form data.
    connection = getCursor()

    #select detailed run information for drivers whose names match the search query.
    connection.execute("SELECT * FROM (\
        SELECT dr_id, CONCAT(driver.surname, ' ', driver.first_name) AS drivers, run_num, seconds, cones, wd, course.name, car.model, car.drive_class,\
        round(seconds + (COALESCE(cones, 0) * 5) + (COALESCE(wd, 0) * 10), 2) AS run_totals\
        FROM run\
        LEFT JOIN driver ON run.dr_id = driver.driver_id\
        LEFT JOIN course ON run.crs_id = course.course_id\
        LEFT JOIN car ON driver.car = car.car_num) AS subquery\
        WHERE drivers LIKE %s;", (f'%{drivers}%',))
    driverRun_list = connection.fetchall()
    return render_template("searchrunlist.html", driverRun_list = driverRun_list,drivers=drivers)

@app.route('/admin/editruns', methods=['GET', 'POST'])
def editruns():
    if request.method == "GET":
        connection = getCursor()

        #get the list of all drivers as it has unique driver_id for select options 
        connection.execute("SELECT * FROM driver;")
        driver_result = connection.fetchall()


        connection = getCursor()

        #get run information for all drivers for display table
        connection.execute("SELECT * FROM run;")
        run_result = connection.fetchall()

        return render_template("editruns.html", driver_result=driver_result, run_result=run_result)


    else:
        driverid = request.form.get('selected_driver') #get driverid from select option
    
        try:
            driverid = int(driverid)

            
            try:
                connection = getCursor()
                connection.execute("SELECT * FROM driver;")
                driver_result = connection.fetchall()

                # If a valid driver ID is provided, get information for that driver from select option bar
                connection = getCursor()
                connection.execute("SELECT * FROM run\
                                    WHERE dr_id=%s;", (driverid,))
                run_result = connection.fetchall()
                return render_template("editruns.html", driverid=driverid, run_result=run_result, driver_result=driver_result)
            
            except:
                new_driver_id=driverid
        
                return render_template('adddriverrun.html', new_driver_id=new_driver_id)

        
        except ValueError:
            #if an invalid driver ID is provided then go this except
            connection = getCursor()
            connection.execute("SELECT * FROM driver;")
            driver_result = connection.fetchall()

            connection = getCursor()
            connection.execute("SELECT * FROM run;")
            run_result = connection.fetchall()
            return render_template("editruns.html", driverid=driverid,driver_result=driver_result, run_result=run_result)

@app.route('/admin/editruns2', methods=['GET', 'POST'])
def editruns2():
    if request.method == "GET":
        # get the course table from database for select option as it has unique course_id
        connection = getCursor()
        connection.execute("SELECT * FROM course;")
        courseList = connection.fetchall()

       
        connection = getCursor()
        # get all the course information from the database for dispaly table
        connection.execute("SELECT * FROM run;")
        course_result = connection.fetchall()
        return render_template("editruns2.html",courseList=courseList,course_result=course_result)
    
    else:
       
        # get courseid from select bar
        courseid = request.form.get('selected_course')
        
        try:
             # get the course table from database for select option as it has unique course_id
            connection = getCursor()
            connection.execute("SELECT * FROM course;")
            getcourseid = connection.fetchall()

            connection = getCursor()

            ##get run information for the selected course if user select a courseid from option bar
            connection.execute("SELECT * FROM run where crs_id = %s;",(courseid,))
            course_result = connection.fetchall()
           
            return render_template("editruns2.html",courseid=courseid,courseList=getcourseid,course_result=course_result)

        except:
            # if where the course selection or retrieval fails, but it appears not working when clicking 'select a course'
            connection = getCursor()
            connection.execute("SELECT * FROM course;")
            getcourseid = connection.fetchall()

            #get all course information from the database if it is not selected
            connection = getCursor()
            connection.execute("SELECT * FROM run;")
            course_result = connection.fetchall()

            return render_template("editruns2.html",courseid=courseid,courseList=getcourseid,course_result=course_result)          

@app.route('/editrun_name', methods=["GET","POST"])
def editrun_name():
    if request.method == "GET":
        driverid = session.get('driverid') # get driverid from 'editruns.html'  "Edit this driver's run details" button
        
        try:
            # get the driver ID from the session.
            connection = getCursor()
            connection.execute("SELECT * FROM run where dr_id=%s;", (driverid,))
            run_result = connection.fetchall()
            return render_template("editrunbyname.html",driverid=driverid,run_result=run_result)
        except:
            # in cases where no runs are available for the driver.
            new_driver_id=driverid
            new_driver_id=new_driver_id
            flash('Please add new runs for this driver first', 'error')
            return redirect('/admin/adddriverrun/{}'.format(new_driver_id))

    else:
        driverid = session.get('driverid')# get driverid from 'editruns.html'  "Edit this driver's run details" button
        connection = getCursor()
        #display the run information of this driver
        connection.execute("SELECT * FROM run where dr_id=%s;", (driverid,))
        run_result = connection.fetchall()

        # Get run data from the form.Thses are a list of values for each type, so use "getlist".
        Driverid=request.form.getlist("driverid")
        courseID=request.form.getlist("courseid")
        runNum=request.form.getlist("run_num")
        seconds=request.form.getlist("seconds")
        cones=request.form.getlist("cones")
        wd=request.form.getlist("wd")
        

       #get all the values from Driverid list by for loop
        current_Driverid=[]
        for i in range(len(Driverid)):
            current_Driverid.append(Driverid[i])

        #get all the values from courseID list by for loop
        current_courseID=[]
        for i in range(len(courseID)):
            current_courseID.append(courseID[i])

        #get all the values from runNum list by for loop
        current_runNum=[]
        for i in range(len(runNum)):
            current_runNum.append(runNum[i])
             
        #get all the values from seconds list by for loop
        current_seconds=[]
         # Process and validate the seconds values.
        for i in range(len(seconds)):
            if seconds[i]:
                try:
                    seconds[i] = float(seconds[i])
                except ValueError:
                    seconds[i] = None
            else:
                seconds[i] = None       
            current_seconds.append(seconds[i])
        
        #get all the values from cones list by for loop
        current_cones=[]
        for i in range(len(cones)):
             # Process and validate the cones values.
            if cones[i]:
                try:
                    cones[i] = int(cones[i])
                except ValueError:
                    cones[i] = None
            else:
                cones[i] = None
            current_cones.append(cones[i])
        
        #get all the values from wd list by for loop
        current_wd=[]
        for i in range(len(wd)):
            # Process and set the wd values.
            if not wd[i]:
                wd[i]=0    
            current_wd.append(wd[i])

        
        connection = getCursor()
        sql = "UPDATE run SET seconds = %s, cones = %s, wd = %s WHERE (dr_id = %s) and (crs_id = %s) and (run_num = %s)"
        data = [(current_seconds[0], current_cones[0], current_wd[0], current_Driverid[0], current_courseID[0], current_runNum[0]),
                (current_seconds[1], current_cones[1], current_wd[1], current_Driverid[1], current_courseID[1], current_runNum[1]),
                (current_seconds[2], current_cones[2], current_wd[2], current_Driverid[2], current_courseID[2], current_runNum[2]),
                (current_seconds[3], current_cones[3], current_wd[3], current_Driverid[3], current_courseID[3], current_runNum[3]),
                (current_seconds[4], current_cones[4], current_wd[4], current_Driverid[4], current_courseID[4], current_runNum[4]),
                (current_seconds[5], current_cones[5], current_wd[5], current_Driverid[5], current_courseID[5], current_runNum[5]),
                (current_seconds[6], current_cones[6], current_wd[6], current_Driverid[6], current_courseID[6], current_runNum[6]),
                (current_seconds[7], current_cones[7], current_wd[7], current_Driverid[7], current_courseID[7], current_runNum[7]),
                (current_seconds[8], current_cones[8], current_wd[8], current_Driverid[8], current_courseID[8], current_runNum[8]),
                (current_seconds[9], current_cones[9], current_wd[9], current_Driverid[9], current_courseID[9], current_runNum[9]),
                (current_seconds[10], current_cones[10], current_wd[10], current_Driverid[10], current_courseID[10], current_runNum[10]),
                (current_seconds[11], current_cones[11], current_wd[11], current_Driverid[11], current_courseID[11], current_runNum[11])
                ]
        # Update the run data in the database.
        for item in data:
            connection.execute(sql, item)

        # get the updated run data for the driver.
        connection.execute("SELECT * FROM run WHERE dr_id = %s;", (current_Driverid[0],))
        new_run_list = connection.fetchall()

        return render_template("editrunbynamelist.html",run_result=run_result,new_run_list=new_run_list)

@app.route('/editrun_course', methods=["GET","POST"])
def editrun_course():
    if  request.method == "GET":
        # need get three parameters from the get url 
        drivertID=request.args.get('driverID')
        drivertID=int(drivertID)
        courseID=request.args.get('courseID')
        runNumber=request.args.get('runNumber')
        runNumber=int(runNumber)

        # put the three parameter to sql to grab the data of these three specific filed data 
        connection = getCursor()
        connection.execute("SELECT * FROM run where dr_id=%s and crs_id=%s and run_num=%s ;",(drivertID,courseID,runNumber,))
        course_result = connection.fetchall()
        return render_template("editrunbycourse.html",course_result=course_result)
    else:
         # Get parameters from the form.
        driverID=request.form.get('driverid')
        driverID=int(driverID)
        courseID=request.form.get('courseid')
        runNumber=request.form.get('run_number')

        #get value and check value type before passing it to sql
        Seconds=request.form.get('Seconds')
        try:
            Seconds = float(Seconds)
        except ValueError:
            Seconds = None
        
        Cones=request.form.get('Cones')
        try:
            Cones = float(Cones)
        except ValueError:
            Cones = None

        WD=request.form.get('WD')
        try:
            WD = float(WD)
        except ValueError:
            WD = None

        connection = getCursor()
        # Update the run data in the database for specific run
        connection.execute("UPDATE run SET seconds = %s, cones = %s, wd = %s  WHERE (dr_id = %s) and (crs_id = %s) and (run_num = %s);",(Seconds,Cones,WD,driverID,courseID,runNumber,))
        return redirect('/admin/editruns2')

@app.route('/admin/adddriver', methods=['GET', 'POST'])
def adddriver():
    if  request.method == "GET":

        # Get a list of all existing drivers as we need the driverid
        connection = getCursor()
        connection.execute("SELECT * FROM driver;")  
        driverList = connection.fetchall()  

        connection = getCursor()
        # Get a list of caregivers who have no age information or who are not junior drivers.
        connection.execute("SELECT * FROM driver where age is null;")  
        caregiverList = connection.fetchall()      
        return render_template("adddriver.html",driverList=driverList,caregiverList=caregiverList) 


    else: # user click "12-16 yrs" or "17-25 yrs" or "Over 25 yrs"  button in the dialog after clicking "Add New Driver" button.
        connection = getCursor()
        #get driver list as it needs driver_id to validate later
        connection.execute("SELECT * FROM driver;") 
        driverList = connection.fetchall()

        connection = getCursor()
        # Get a list of caregivers who have no age information or who are not junior drivers.This is to get id for caregiver options
        connection.execute("SELECT * FROM driver where age is null;")  
        caregiverList = connection.fetchall()        

        #to confirm how old is the new driver as they enter different amount of data
        age_confirmation = request.form.get('age_confirmation')
        if age_confirmation == "young": 
            # If the user clicks "12-16 yrs" in the dialog, it sets the age_confirmation variable to "young".
            # Then, it renders the adddriverform.html template to gather additional information.
            return render_template("adddriverform.html",caregiverList=caregiverList,age_confirmation=age_confirmation)  
        
        elif age_confirmation == "youngadult":  
            # If the user clicks "17-25 yrs" in the dialog, it sets the age_confirmation variable to "youngadult".
            # Then, it renders the adddriverform.html template to gather additional information.
            return render_template("adddriverform.html",age_confirmation=age_confirmation)
        
        elif age_confirmation == "adult":  
            
            # If the user clicks "Over 25 yrs" in the dialog, it sets the age_confirmation variable to "youngadult".
            # Then, it renders the adddriverform.html template to gather additional information.
            return render_template("adddriverform.html",age_confirmation=age_confirmation)  

        else:
            # This part is executed when the user has provided the necessary driver information in the add new driverform from(adddriverform.html).
            driverID =request.form.get('driver_id')
            driverID=int(driverID)

            # Checking for empty values and replacing them with "None" as needed.
            # Extract and validate user input.
            firstName = request.form.get('first_name')
            if firstName == "":
                firstName = "None"
            surname = request.form.get('surname')
            if surname == "":
                surname = "None"

            dobget = request.form.get('dob')
            # check the date of birth range, and make sure input value in the right range.
            if  dobget is not None and dobget != "None":
                try:
                    dob = datetime.strptime(dobget, '%Y-%m-%d')
                    current_date = datetime.now()

                    #age is automatically calculated, also get caregiver value to check if there is age right for each range.
                    age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))
                    caregiver = request.form.get('caregiver')
                    if 12 <= age <= 16 and (caregiver != "None" or caregiver is not None): 
                            age=age
                            caregiver=caregiver

                    elif 17 <= age < 25 and (caregiver == "None" or caregiver is None):
                            age=age    
                            if caregiver == "" or "None":
                                caregiver = None  
                    else:
                        flash('You entered an invailid value')
                        return redirect('/admin/adddriver')
                        
                except ValueError:  # in case user input an invalue date of birth
                        flash('You entered an invailid value')
                        return redirect('/admin/adddriver')

            else:
                dob=dobget
                dob = None
                age=request.form.get('age')
                if age == "" or "None":
                    age = None  
                caregiver = request.form.get('caregiver')
                if caregiver == "" or "None":
                    caregiver = None  

    
            car = request.form.get('car')
        
            ## Check if the provided driver ID already exists in the database.
            connection = getCursor()
            connection.execute("SELECT driver_id FROM driver;")
            sql_driver_id = connection.fetchall()
            sql_driver_id=list(sql_driver_id)
            driver_id_list = [row[0] for row in sql_driver_id]

            if driverID not in driver_id_list:
                # Inserting the driver's information into the database
                connection = getCursor()
                connection.execute("INSERT INTO driver\
                                (driver_id, first_name, surname, date_of_birth, age, caregiver, car) \
                                VALUES (%s, %s, %s, %s, %s, %s, %s);", (driverID, firstName, surname, dob, age, caregiver, car,))
                new_driver_id=driverID
                connection.execute("SELECT * FROM driver WHERE driver_id = %s;", (new_driver_id,))
                new_driver_list=connection.fetchall()
                return render_template("adddriverlist.html",age=age,new_driver_id=new_driver_id,new_driver_list=new_driver_list,sql_driver_id=sql_driver_id)
            
             # Inform the user that the provided driver ID already exists.
            else:
                flash('This ID already exists', 'error')
                return redirect('/admin/adddriver')
            
@app.route('/admin/adddriverrun/<new_driver_id>', methods=['GET', 'POST'])
def adddriverrun(new_driver_id):
    if  request.method == "GET":
        driverid=new_driver_id   #Every driver has a unique id to be added.
        # In this case, get the new driver's ID from the URL and render the adddriverrun.html page.
        return render_template("adddriverrun.html",driverid=driverid)

    else:  
        # Get the new driver's ID from the URL.
        driverid=new_driver_id
        
        # Get the run data for multiple runs from the form.
        Driverid=request.form.getlist("driverid")
        courseID=request.form.getlist("courseid")
        runNum=request.form.getlist("run_num")
        seconds=request.form.getlist("seconds")
        cones=request.form.getlist("cones")
        wd=request.form.getlist("wd")

        # Process and validate run data for each run.
        #get all the values from Driverid list by for loop
        current_Driverid=[]
        for i in range(len(Driverid)):
            current_Driverid.append(Driverid[i])
    
        #get all the values from courseID list by for loop
        current_courseID=[]
        for i in range(len(courseID)):
            current_courseID.append(courseID[i])

        #get all the values from runNum list by for loop
        current_runNum=[]
        for i in range(len(runNum)):
            current_runNum.append(runNum[i])
             
        #get all the values from seconds list by for loop
        current_seconds=[]
        for i in range(len(seconds)):
            if seconds[i]:
                try:
                    seconds[i] = float(seconds[i])
                except ValueError:
                    seconds[i] = None
            else:
                seconds[i] = None       
            current_seconds.append(seconds[i])
   
        #get all the values from cones list by for loop
        current_cones=[]
        for i in range(len(cones)):
            if cones[i]:
                try:
                    cones[i] = int(cones[i])
                except ValueError:
                    cones[i] = None
            else:
                cones[i] = None
            current_cones.append(cones[i])

        #get all the values from wd list by for loop
        current_wd=[]
        for i in range(len(wd)):
            if not wd[i]:
                wd[i]=0    
            current_wd.append(wd[i])
   

        #insert run data for each run.
        connection = getCursor()
        sql = "INSERT INTO run (dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, %s, %s, %s, %s, %s);"

        # Combine run data into a list of tuples.
        data = [(current_Driverid[0], current_courseID[0], current_runNum[0], current_seconds[0], current_cones[0], current_wd[0]),
                (current_Driverid[1], current_courseID[1], current_runNum[1], current_seconds[1], current_cones[1], current_wd[1]),
                (current_Driverid[2], current_courseID[2], current_runNum[2], current_seconds[2], current_cones[2], current_wd[2]),
                (current_Driverid[3], current_courseID[3], current_runNum[3], current_seconds[3], current_cones[3], current_wd[3]),
                (current_Driverid[4], current_courseID[4], current_runNum[4], current_seconds[4], current_cones[4], current_wd[4]),
                (current_Driverid[5], current_courseID[5], current_runNum[5], current_seconds[5], current_cones[5], current_wd[5]),
                (current_Driverid[6], current_courseID[6], current_runNum[6], current_seconds[6], current_cones[6], current_wd[6]),
                (current_Driverid[7], current_courseID[7], current_runNum[7], current_seconds[7], current_cones[7], current_wd[7]),
                (current_Driverid[8], current_courseID[8], current_runNum[8], current_seconds[8], current_cones[8], current_wd[8]),
                (current_Driverid[9], current_courseID[9], current_runNum[9], current_seconds[9], current_cones[9], current_wd[9]),
                (current_Driverid[10], current_courseID[10], current_runNum[10], current_seconds[10], current_cones[10], current_wd[10]),
                (current_Driverid[11], current_courseID[11], current_runNum[11], current_seconds[11], current_cones[11], current_wd[11])]
        # Execute the SQL statement for each run's data.
        for item in data:
            connection.execute(sql, item)

         # get the updated run list for the driver.
        connection.execute("SELECT * FROM run WHERE dr_id = %s;", (driverid,))
        new_run_list = connection.fetchall()
        return render_template("adddriverrunlist.html",driverid=driverid,new_driver_id=new_driver_id,new_run_list=new_run_list)


if __name__ == '__main__':
    app.run(debug=True)
