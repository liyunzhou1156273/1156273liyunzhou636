***Bankside Rakaia Motorkhana Mavens-Competition Event Web Application with Python***

# Web Application Structure:

- This project from BRMM car club involves the development of a small web application to assist in managing drivers, cars, courses, and runs for a single competitive Motorkhana event. 
- The application will serve as a tool to streamline the organization of this motorsport event, allowing for efficient management and coordination of event-related data.
- The web application follows a typical Flask structure with routes, functions, and templates. Here's a brief outline of the structure and how routes, functions, and templates relate:

## Routes and Functions:
1. Login Route: / 
- Function: login()
- Description: Handles user login. Users can log in as regular users or administrators. The POST request checks user credentials and redirects to the appropriate dashboard. Uses the login.html template.
### User routes and functions
2. Home Route: /home
- Function: home()
- Description: Provides access to the main dashboard after a successful login. Uses the base.html template to render content, and data can be passed for display.
3. List Drivers Route: /listdrivers
- Function: listdrivers()
- Description: Lists all drivers, including their details. Retrieves data from the database, such as driver names and car information, and passes it to the driverlist.html template.
4. Run Details Route: /rundetails
- Function: rundetails()
- Description: Allows users to view detailed run statistics for a specific driver. Retrieves information about a driver's runs and associated data and uses the rundetails.html template for presentation.
5. List All Details Route: /listalldetails
- Function: listalldetails()
- Description: Has both GET and POST methods. The GET method retrieves data on all drivers and their respective run details. The POST method allows users to select a specific driver to see their run details. Passes data to the allrundetails.html template.
6. List Overall Route: /listoverall
- Function: listoverall()
- Description: Provides an overall ranking of drivers based on their performance. Retrieves data from the database, calculates overall scores, and displays the results using the overallresults.html template.
7. Show Graph Route: /showgraph
- Function: showgraph()
- Description: Generates a graph displaying the top-performing drivers. Retrieves data on the best drivers and their scores and passes this information to the top5graph.html template.

### Admin routes + functions + Data Passing
8. Admin Route: /admin
- Function: admin()
- Description: Allows administrators to access the admin panel. Uses the admin.html template to provide administrative functionality.
9. List Junior Driver Route: /admin/listjuniordriver
- Function: listjuniordriver()
- Description: Lists junior drivers (aged 12-24) and their details. Retrieves relevant data from the database and passes it to the juniordriverlist.html template.
10. Search Driver List Route: /admin/searchdriverlist
- Function: searchdriverlist()
- Description: Lists all drivers and their details. Users can search for specific drivers. Data is passed to the searchdriverlist.html template for rendering.
11. Search Run List Route: /admin/searchrunlist
- Function: searchrunlist()
- Description: Lists all run details for drivers. Users can search for specific drivers. The data is passed to the searchrunlist.html template for rendering.
12. Search Driver List Filter Route: /admin/searchdriverlist/filter
- Function: searchdriverlistfilter()
- Description: Handles filtering drivers based on user search queries. Retrieves filtered driver data and passes it to the searchdriverlist.html template for display.
13. Search Run List Filter Route: /admin/searchrunlist/filter
- Function: searchrunlistfilter()
- Description: Admins can filter run details based on search queries. Filtered run data is passed to the searchrunlist.html template for rendering.
14. Edit Runs 2 Route: /admin/editruns2
- Function: editruns2()
- Description: Provides functionality to edit run records for drivers. Utilizes the editruns2.html template and can filter and display runs based on the selected course.
15. Edit Runs Route: /admin/editruns
- Function: editruns()
- Description: Administrators can edit run records for a specific driver using this route. The editruns.html template is employed for this purpose. The route handles both GET and POST requests to display run records and handle modifications。
16. Edit Run by Name Route: /editrun_name
- Function: editrun_name()
- Description: Enables administrators to edit run records for a specific driver. Retrieves the driver's current run records, allows administrators to make modifications, and updates the database. Uses the editrunbyname.html template for presentation.
17. Edit Run by Course Route: /editrun_course
- Function: editrun_course()
- Description: This route is used for editing run records for a specific driver on a particular course. When accessed via GET request, it retrieves specific parameters (driverID, courseID, and runNumber) from the URL and queries the database to fetch the corresponding run data for that specific course and driver. The data is passed to the editrunbycourse.html template for rendering.
18. Add Driver Form Route: /admin/adddriverform
- Function: adddriverform()
- Description: This route is used to gather additional information when adding a new driver. It provides a form for specifying the driver's age range, caregiver, and car details. The data is passed to the adddriverform.html template.
19. Add Driver List Route: /admin/adddriverlist
- Function: adddriverlist()
- Description: After successfully adding a new driver, this route displays the driver's information, including their age, ID, and details. It retrieves the added driver's data from the database and uses the adddriverlist.html template for rendering.
20. Add Driver Run Route: /admin/adddriverrun/<new_driver_id>
- Function: adddriverrun(new_driver_id)
- Description: This route allows administrators to add run records for a new driver. The driver's ID is provided as a parameter. Administrators can input details for each run, such as course ID, run number, seconds, cones, and WD (which stands for something). The route handles both GET and POST requests. When new run records are added, they are stored in the database. The adddriverrun.html template is used for input, and the adddriverrunlist.html template displays the list of added run records for the new driver.

## Templates:
```
web-app/
│
├── login/
│ ├── user/
│ │ ├── base.html
│ │ ├── home.html
│ │ ├── driverlist.html
│ │ ├── rundetails.html
│ │ ├── allrundetails.html
│ │ ├── overallresults.html
│ │ ├── top5graph.html
│ ├── admin/
│ │ ├── listjuniordriver.html
│ │ ├── searchdriverlist.html
│ │ ├── searchrunlist.html
│ │ ├── searchdriverlistfilter.html
│ │ ├── searchrunlistfilter.html
│ │ ├── editruns2.html
│ │ ├── editruns.html
│ │ ├── editrunbyname.html
│ │ ├── editrunbycourse.html
│ │ ├── adddriverform.html
│ │ ├── adddriverlist.html
│ │ ├── adddriverrun.html
```


# Assumptions and Design Decisions:

## Assumptions:
- Route Hierarchy: The routes have been organized hierarchically to reflect the user roles. Regular user routes, such as /home, /listdrivers, and /rundetails, are distinct from admin routes, like /admin/listjuniordriver and /admin/editruns. This hierarchy allows for separation of user and admin functionalities.
- Edit by course: I assume users can select a course, and the table below displays run details associated with the selected course. But at the beginning, I assume it needs to be edited for the whole course at a time. It seems not making sense.
- Edit by name: I assume that 12 runs for a specific driver can be edited and added at one time. This can be well displayed but it can be changed to edit or add one run at a time for a driver.
- Add a new driver while the user forgets to add 12 new runs. I assume user still can add new runs while editing, so it can redirect to add new runs pages with value ID. 
- Log Out Option: The navigation menu includes a "Log out" link, indicating that users can log out of their accounts. I assume this is a standard practice for user authentication and session management.
- 

## Design Decisions:
- Selected Driver Highlight in selecting driver in Driver Run Details(User page) : If the user has previously selected a driver and the page has been reloaded, the "if" condition checks whether the current driver in the loop matches the previously selected "driverid." If a match is found, that driver is set as the "selected" option in the dropdown menu. This ensures that the previously selected driver remains selected for a consistent user experience.
- Age Ranges in adding new driver: The age ranges considered in the form are "young," "youngadult," and "adult." It's assumed that these age ranges define different age groups for drivers, possibly impacting the information required for registration.
- Date of Birth Input in adding new driver: For drivers in the "young" and "youngadult" categories, the form includes a date of birth input field. It's assumed that users in these age groups need to provide their birthdate.
- Disabled Fields(Edit runs by course ): The "Driver ID," "Course ID," and "Run Number" fields are initially populated with data retrieved from the database and are disabled. Users cannot modify these values when editing run records.
- Hidden Fields(Edit runs by course ): Three hidden input fields ("driverid," "courseid," and "run_number") are included in the form. These fields store the original values for "Driver ID," "Course ID," and "Run Number." These values are submitted with the form to ensure the server can identify and locate the specific run record in the database for updating.
- Editable Fields(Edit runs by course ): Users are allowed to input new data for the "Seconds," "Cones," and "Wrong Direction" (abbreviated as "WD") fields. These fields accept numerical values and can be edited by users to update the corresponding run record.
- Data Validation: In the Python route (editrun_course), the values submitted through the form are retrieved. The server-side code validates the input values for "Seconds," "Cones," and "WD." These values are checked to ensure they are in the correct format, specifically as floating-point numbers. If the input is not a valid number, it is set to None.
- Edit by name: While it can be achieved by using the method of using <input> like 'Edit by course'. I want to edit 12 runs at a time no matter how many data you update in this form. While this approach can work well for a specific number of records, it may not be easily scalable or flexible if I need to handle a dynamic or variable number of run records.
- Modal Dialog for Adding a Driver: I have a button labeled "Add New Driver," and when clicked, it opens a modal dialog for adding a new driver. This dialog confirms the age of the driver. The user is presented with options to select the driver's age range as this responds to the html form in adddriverform.html.
- Age Confirmation Form: Inside the modal dialog, you have a form with buttons for different age ranges. It seems like the user can confirm the age of the new driver by clicking one of these buttons, which presumably triggers a submission of the form. 
- Edit run for a new driver who is without new runs. If there's no runs for a specific driver (indicated by an exception), it sets new_driver_id with the value of driverid and rendering the "adddriverrun.html" template,for adding runs for a new driver first.
- Edit Button: In the last column of each row, there is an "Edit" button. Clicking this button appears to send the user to an edit page with more detailed information about the selected run. The URL for the edit page is dynamically generated based on the values of Driver ID, Course ID, and Run Number from the current row.


# Database Questions:
### o　What SQL statement creates the car table and defines its three fields/columns? 
```shell
CREATE TABLE IF NOT EXISTS car
(
car_num INT PRIMARY KEY NOT NULL,
model VARCHAR(20) NOT NULL,
drive_class VARCHAR(3) NOT NULL
);
```
### o　Which line of SQL code sets up the relationship between the car and driver tables?
```shell
FOREIGN KEY (car) REFERENCES car(car_num)
ON UPDATE CASCADE
ON DELETE CASCADE
```
### o　Which 3 lines of SQL code insert the Mini and GR Yaris details into the car table?
```shell
INSERT INTO car VALUES
(11,'Mini','FWD'),
(17,'GR Yaris','4WD'),
```
### o　Suppose the club wanted to set a default value of ‘RWD’ for the driver_class field. What specific change would you need to make to the SQL to do this?
```shell
CREATE TABLE IF NOT EXISTS car
(
  car_num INT PRIMARY KEY NOT NULL,
  model VARCHAR(20) NOT NULL,
  drive_class VARCHAR(3) NOT NULL DEFAULT 'RWD'  -- Added DEFAULT constraint
);
```
***o　Suppose logins were implemented. Why is it important for drivers and the club admin to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app facilities were available to everyone.***
I think 

# Image Sources:

The web application uses the following images for background:
- /static/admin.png: This image is used as the background for the admin interface.
- /static/login.jpg: This image serves as the background for the login page.
- /static/racing.jpg: It is used as the background image for the  public user pages.
