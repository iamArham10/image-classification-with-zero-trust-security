### User roles and responsiblities

- Super admin
    - super admin is the main person that will be one at the start (hardcoded) he will be able to manage other admins and also will have the capaiblities of admin, he will manage security concerns like see logs of requests like activities of other users. He’ll also be able to manage other entities like admin, student, teacher, courses.
- admin
    - can see attendance logs, generate reports can manage (create, edit, update) teachers, students, courses. Register students in a specific course, assign teachers to a specific course. will create student, teacher id’s, and courses.
- teacher
    - a teacher will be able to start a session of a attendance of a specific course and during that camera will be one and all of the students registered in that specific course, if they come on front of the camera their attendance will be marked.
    - Generate reports attendance of a course, etc
    - can also manually mark attendance during a course attendance session.
- student
    - is able to apply to be registered to the specific available course and that will be accepted by the admin.
    - can generate their attendance report on a specific course.
    - can also like add their facial data like they’ll have a button to click to add their facial featuers, and camera will open and take their pictures like let’s say 20 of them and then after that their adding facial data request will go to the admin and he’ll by looking at the picture quality and like variations either accept it or decline it.

### User cases by role

- super admin
    - At start I’ll have a hardcoded super admin that will log in to the system, will be able to see activities of all other users like other teachers, other students, other admins for security purposes. A password and email/username will be required.
    - He’ll be able to have all of the features of admin.
    - He can make other admins as super admin.
    - He can create admin id’s, etc.
- admin
    - first when admin id is created he’ll login and he’ll not have any permission he’ll be required to first verify his email that will be added by super admin and also have to authenticate through google authenticator and then his account will be valid and be able to perform actions.
    - Admin is able to manage (CRUD) students, teachers, courses, assign teachers to courses, and validate students request to join a course, is able to validate students request facial data submission.
    - Admin is able to generate reports of courses attendance, etc.
- teacher
    - a teacher will also first have to login using account given by admin/superadmin and then he’ll validate through google authenticator everytime too. And then after that he’ll be able to start a session where students can register, he’ll also be able to generate reports, during a session he’ll be able to mark any students attendance manually.
    - a teacher will only see the courses he’s registered.
    - a teacher will only be able to perform his action after validating through google authenticator.
- student
    - a student for his account will also have to validate through google authenticator too. He’ll be able to apply to register to a course.
    - he’ll able to generate his reports for his attendance for a specific course.
    - he’ll be able to register his facial data.
    - a student will only be able to perform his action after validating through google authenticator.

### Authentication requirements

- super admin
    - first super admin account is already created hardcoded. Then he can create other admin accounts and give them the persmission to be super admin too.
    - whenever a other superadmin/admin logins they’ll have to verify through google authenticator.
    - super admin session will be expired after every 15 minutes, so if there’s no activity for 15 minutes their token will be expired and they’ll have to login again.
- admin
    - when first time admin or given permission by superadmin to be a superadmin they’ll have to add google authenticator, And then after that whenever they login they’ll have to authenticate through that google authenticator.
    - session will expire after every 15 minutes of no activity.
    - if an account is lost super admin will be able to reset password for that account using google authenticator, fix lost google authenticator stuff will be done by super admin
- same above procedures for teachers and students including password reset policies.

### Facial Recognition Specifications

- A teacher will come in to the class with his laptop he’ll be able to start a session for a specific coruse give number of hours and the camera will start, all of the facial data of students registered on that specific course will be loaded and when a student comes in front of the camera his face will be registered and liveness detection like smile will be used and compared and attendance will be marked after that.
- A teacher can mark manual attendance of a student only during a session.
- A students facial embeddings will be stored in a database that will be loaded according to the requried course. and also his facial images will be stored encrypted and a specific key will be associated to a specific user that will be stored in any AWS KWs, hashicorp, etc will be used to unecrypt the facial image of a student, only front image of student will be stored so that as profile picture etc. facial embeddings will only be stored in a database encrypted.

### Attendance Tracking Details

- sessions are created by the specific teacher.
- notification is sent to the student for his absence.
- reports are generated by teacher, student for a specific course for their own attendance etc.

### Zero Trust Implementation Requirements

- a webcam from the browser will be used for session attendance and also when students will be registering their facial data.
- verification will be done after every 15 minutes of in activity, not during a session (think about that yourself).
- ip address, device information, activity will be collected for each activity of user student, admin, teacher.
- a super admins, teacher, admins will only be able to log in, teachers through a specific ip’s.
- Re authentication will be required after major change.
- Short lived JWT tokens will be used.
- Token rotation will be used, so when super admin tries to create a super admin, a specific token that is right now in .env will be used and it’ll then after rotated and saved in .env file for further use.
- contextual data will be used in tokens (location, device, time constraints).
- Limit attendance marking based on session.
- Loggings will be used and only a specific things will be used.
- security measure will be used against DDOS attacks or any kind of other attacks like cookies will no be used to protect again other types of attacks like other website navigating through api.
- Rate limiting will be used on security apis
- failed login locks will be used that prevents from logging again and again.
- API’s in course creation, teacher, etc will be slowed to help against attacks.

### UI/UX Requirements

- clean UI white and dark purple colored, simple UI.

### API Requirements

### Technology Constraints

- only browser tech stack fastapi and react