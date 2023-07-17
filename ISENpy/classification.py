# classification.py

"""
This file defines classes to represent class member, grades, absences, and planning events, along with their respective reports.
"""

# Class Member
class ClassMember:
    def __init__(self, name, mail, avatar_url):
        self.name = name
        self.mail = mail
        self.avatar_url = avatar_url
    
    def __repr__(self):
        return f"ClassMember(name='{self.name}', mail='{self.mail}', avatar_url='{self.avatar_url}')"

    def __getitem__(self, key):
        if key == 'name':
            return self.name
        elif key == 'mail':
            return self.mail
        elif key == 'avatar_url':
            return self.avatar_url
        else:
            raise KeyError(f"Invalid key: {key}, valid keys are 'name', 'mail', and 'avatar_url'")

class ClassMemberReport:
    def __init__(self, nbMembers, data):
        self.nbMembers = nbMembers
        self.data = data
    
    def __repr__(self):
        return f"ClassMemberReport(nbMembers={self.nbMembers}, data={self.data})"
    
    def __getitem__(self, key):
        if key == 'nbMembers':
            return self.nbMembers
        elif key == 'data':
            return self.data
        else:
            raise KeyError(f"Invalid key: {key}, valid keys are 'nbMembers' and 'data'")


# Grade
class Grade:
    def __init__(self, date, code, name, grade, absence, appreciation, instructors):
        # Constructor to initialize Grade object attributes
        self.date = date
        self.code = code
        self.name = name
        self.grade = grade
        self.absence = absence
        self.appreciation = appreciation
        self.instructors = instructors
        
    def __repr__(self):
        # Returns a string representation of the Grade object
        return f"Grade(date='{self.date}', code='{self.code}', name='{self.name}', grade='{self.grade}', absence='{self.absence}', appreciation='{self.appreciation}', instructors='{self.instructors}')"

    def __getitem__(self, key):
        # Allows accessing attributes using dictionary-like syntax
        if key == 'date':
            return self.date
        elif key == 'code':
            return self.code
        elif key == 'name':
            return self.name
        elif key == 'grade':
            return self.grade
        elif key == 'absence':
            return self.absence
        elif key == 'appreciation':
            return self.appreciation
        elif key == 'instructors':
            return self.instructors
        else:
            raise KeyError(f"Invalid key: {key}, valid keys are 'date', 'code', 'name', 'grade', 'absence', 'appreciation', and 'instructors'")

class GradeReport:
    def __init__(self, grade_average, grades):
        # Constructor to initialize GradeReport object attributes
        self.average = grade_average
        self.grades = grades
    
    def __repr__(self):
        # Returns a string representation of the GradeReport object
        return f"GradeReport(average={self.average}, data={self.grades})"
    
    def __getitem__(self, key):
        # Allows accessing attributes using dictionary-like syntax
        if key == 'average':
            return self.average
        elif key == 'data':
            return self.grades
        else:
            raise KeyError(f"Invalid key: {key}, valid keys are 'average' and 'data'")

# Absence
class Absence:
    def __init__(self, date, reason, duration, schedule, course, instructor, subject):
        # Constructor to initialize Absence object attributes
        self.date = date
        self.reason = reason
        self.duration = duration
        self.schedule = schedule
        self.course = course
        self.instructor = instructor
        self.subject = subject

    def __repr__(self):
        # Returns a string representation of the Absence object
        return f"Absence(date='{self.date}', reason='{self.reason}', duration='{self.duration}', schedule='{self.schedule}', course='{self.course}', instructor='{self.instructor}', subject='{self.subject}')"
    
    def __getitem__(self, key):
        # Allows accessing attributes using dictionary-like syntax
        if key == "date":
            return self.date
        elif key == "reason":
            return self.reason
        elif key == "duration":
            return self.duration
        elif key == "schedule":
            return self.schedule
        elif key == "course":
            return self.course
        elif key == "instructor":
            return self.instructor
        elif key == "subject":
            return self.subject
        else:
            raise KeyError(f"Invalid key: {key}, valid keys are 'date', 'reason', 'duration', 'schedule', 'course', 'instructor', and 'subject'")

class AbsenceReport:
    def __init__(self, nbAbsences, time, data):
        # Constructor to initialize AbsenceReport object attributes
        self.nbAbsences = nbAbsences
        self.time = time
        self.data = data
    
    def __repr__(self):
        # Returns a string representation of the AbsenceReport object
        return f"AbsenceReport(nbAbsences={self.nbAbsences}, time={self.time}, data={self.data})"
    
    def __getitem__(self, key):
        # Allows accessing attributes using dictionary-like syntax
        if key == 'nbAbsences':
            return self.nbAbsences
        elif key == 'time':
            return self.time
        elif key == 'data':
            return self.data
        else:
            raise KeyError(f"Invalid key: {key}, valid keys are 'nbAbsences', 'time', and 'data'")

# Planning
class Event:
    def __init__(self, id, start, end, class_name, type, subject, description, instructors, start_time, end_time, room, class_info):
        # Constructor to initialize Event object attributes
        self.id = id
        self.start = start
        self.end = end
        self.class_name = class_name
        self.type = type
        self.subject = subject
        self.description = description
        self.instructors = instructors
        self.start_time = start_time
        self.end_time = end_time
        self.room = room
        self.class_info = class_info

    def __repr__(self):
        # Returns a string representation of the Event object
        return f"Event(id='{self.id}', start='{self.start}', end='{self.end}', class_name='{self.class_name}', type='{self.type}', subject='{self.subject}', description='{self.description}', instructors='{self.instructors}', start_time='{self.start_time}', end_time='{self.end_time}', room='{self.room}', class_info='{self.class_info}')"

    def __getitem__(self, key):
        # Allows accessing attributes using dictionary-like syntax
        if key == "id":
            return self.id
        elif key == "start":
            return self.start
        elif key == "end":
            return self.end
        elif key == "class_name":
            return self.class_name
        elif key == "type":
            return self.type
        elif key == "subject":
            return self.subject
        elif key == "description":
            return self.description
        elif key == "instructors":
            return self.instructors
        elif key == "start_time":
            return self.start_time
        elif key == "end_time":
            return self.end_time
        elif key == "room":
            return self.room
        elif key == "class_info":
            return self.class_info
        else:
            raise KeyError(f"Invalid key: {key}, valid keys are 'id', 'start', 'end', 'class_name', 'type', 'subject', 'description', 'instructors', 'start_time', 'end_time', 'room', and 'class_info'")

class PlanningReport:
    def __init__(self, events):
        # Constructor to initialize PlanningReport object attributes
        self.data = events
    
    def __repr__(self):
        # Returns a string representation of the PlanningReport object
        return f"PlanningReport(data={self.data})"
    
    def __getitem__(self, key):
        # Allows accessing attributes using dictionary-like syntax
        if key == 'data':
            return self.data
        else:
            raise KeyError(f"Invalid key: {key}, valid key is 'data'")

# School Report
class SchoolReportData:
    def __init__(self, name, id):
        # Constructor to initialize SchoolReportData object attributes
        self.name = name
        self.id = id
    
    def __repr__(self):
        # Returns a string representation of the SchoolReportData object
        return f"SchoolReportData(name='{self.name}', id='{self.id}')"

    def __getitem__(self, key):
        # Allows accessing attributes using dictionary-like syntax
        if key == 'name':
            return self.name
        elif key == 'id':
            return self.id
        else:
            raise KeyError(f"Invalid key: {key}, valid key is 'name' and 'id'")



class SchoolReport:
    def __init__(self, nbReports, data):
        # Constructor to initialize SchoolReport object attributes
        self.nbReports = nbReports
        self.data = data
    
    def __repr__(self):
        # Returns a string representation of the SchoolReport object
        return f"SchoolReport(nbReports={self.nbReports}, data={self.data})"
    
    def __getitem__(self, key):
        # Allows accessing attributes using dictionary-like syntax
        if key == 'nbReports':
            return self.nbReports
        elif key == 'data':
            return self.data
        else:
            raise KeyError(f"Invalid key: {key}, valid key is 'nbReports' and 'data'")