Bankside Rakaia Motorkhana Mavens-Competition Event Web Application with Python.
# Web Application Structure:

This project from BRMM car club involves the development of a small web application to assist in managing drivers, cars, courses, and runs for a single competitive Motorkhana event. 
The application will serve as a tool to streamline the organization of this motorsport event, allowing for efficient management and coordination of event-related data.
The web application follows a typical Flask structure with routes, functions, and templates. Here's a brief outline of the structure and how routes, functions, and templates relate:

## Routes and Functions:

/: The / route, also known as the login route, is designed to handle both user and admin logins. It supports both GET and POST requests.
### User routes
/home: This route corresponds to the user's homepage. It renders the base.html template, which is the base layout for user interface.
/listdrivers: The /listdrivers route is responsible for listing all the drivers in the page.The retrieved driver information is presented using the driverlist.html template.
/rundetails: The /rundetails route allows users to explore and analyze the performance of a specific driver during different runs, including relevant statistics and the overall run score, 
              will be presented using the rundetails.html template.
/listalldetails:This route provides users with a comprehensive view of all drivers and their corresponding run details. This route allows users to explore and analyze the performance of all drivers and their respective runs.
              The retrieved driver and run details are presented in the "allrundetails.html" template.
/listcourses: This route lists all courses. The associated function retrieves course data and renders the courselist.html template.      
/listoverall: This route provides an overview of the overall results for all drivers in the club. It displays the performance of each driver across multiple courses and computes an overall score. 
              Users can easily compare drivers based on their performance in various courses.
/showgraph: This route displays a top 5 drivers graph. The associated function retrieves data and renders the showgraph.html template.

### Admin routes
/admin: This route serves as the entry point for administrators to access specific administrative features and functionalities of the web application. 
        It allows authorized administrators to manage various aspects of the application, including adding, updating, and overseeing driver and run data.
/admin/listjuniordriver: This route is designed to provide administrators with a list of junior drivers.It includes information such as driver ID, 
        name, date of birth, age, caregiver, and car details for each junior driver.The associated function retrieves data and renders the juniordriverlist.html template.
/admin/searchdriverlist:The searchdriverlist.html template plays a crucial role in rendering a list of drivers as part of the /admin/searchdriverlist route. 
            This template ensures that administrators can efficiently search for and view driver information, providing a user-friendly interface for managing the application's driver database. 
/admin/searchrunlist: This route allows administrators to search, retrieve, and view detailed information about runs conducted by drivers. 
          The information will be presented in searchrunlist.html.
/admin/searchdriverlist/filter:This route empowers administrators to quickly locate specific drivers based on their name.The information will be presented in searchdriverlist.htm
/admin/searchrunlist/filter:This route empowers administrators to quickly locate specific runs associated with drivers, The information will be presented in searchrunlist.html.
/admin/editions: This route allows administrators to manage and edit run records associated with specific drivers.  The information will be presented in editruns.html.
/admin/editruns2: This route allows administrators to manage and edit run records associated with specific courses.  The information will be presented in editruns2.html.
/editrun_name:
/editrun_course:
/admin/adddriver:
/admin/adddriverrun/<new_driver_id>:

## Templates:

login.html:

### User pages
base.html:
courselist.html:
driverlist.html:
juniordriverlist.html:
overallresults.html:
rundetails.html:
top5graph.html

### Admin pages
adddriver.html:
adddriverform.html:
adddriverlist.html:
adddriverrun.html:
adddriverrunlist.html
admin.html:
allrundetails.html:
editrunbycourse.html:
editrunbyname.html:
editrunbynamelist.html:
editruns.html:
editruns2.html:
searchdriverlist.html:
searchrunlist.html:


## Data Passing:

Data is retrieved from the database within the route functions.
The data is then passed to the corresponding HTML templates for rendering.

-----
# Assumptions and Design Decisions:

## Assumptions:

Assumed that the database structure is consistent with the provided motorkhana_local.sql file.
Assumed that the web application is designed for authorized users, and access control is enforced.
## Design Decisions:

Chose to use a Flask framework for developing the web application due to its simplicity and flexibility.
Utilized separate routes and templates to keep the code organized and maintainable.
Designed routes with distinct purposes to provide a clear and intuitive user experience.
Used SQL databases to store and retrieve data from the application.

## Design Decisions:



## Multiple Route Separation:

Different routes are created for various functionalities, such as listing junior drivers, searching for drivers, and editing runs. This separation provides clear navigation and simplifies code management.
## Forms and POST Requests:

To handle user input and data updates, the application utilizes HTML forms and POST requests, which allow secure data submission.
## Data Display and Interaction:

Templates are designed for displaying and interacting with data, such as presenting search results and editing run data.
## Admin Privileges:

Admin and non-admin users are segregated to prevent unauthorized access to certain routes and functionalities.
Admins can access routes for data editing, while non-admin users have limited access.
##  Error Handling:

Error handling mechanisms are implemented to provide feedback to users, such as notifying them if a specific ID already exists.
Database Structure:

The application is built on a pre-existing database structure, as specified in the motorkhana_local.sql file.


# Database Questions:

The SQL statement that creates the car table with its three fields/columns is as follows:

# Image Sources:

The web application uses the following images for background:
/static/admin.png: This image is used as the background for the admin interface.
/static/login.jpg: This image serves as the background for the login page.
/static/racing.jpg: It is used as the background image for the  public user pages.
