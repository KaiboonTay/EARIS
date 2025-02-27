from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Students, Courses, Studentgrades
from django.contrib import messages
from tablib import Dataset
import csv, io, os
from django.db import IntegrityError
import pandas as pd


# Create your views here.

@api_view(['POST'])
def upload_csv(request):
    #Check for either 'csv_file' or 'excel_file' is in the request
    uploaded_file_key = None

    if 'csv_file' in request.FILES:
        uploaded_file_key = 'csv_file'
    elif 'excel_file' in request.FILES:
        uploaded_file_key = 'excel_file'
    else:
        return Response({"error": "No file is provided."}, status=status.HTTP_400_BAD_REQUEST)
    

    #Get the uploaded file
    uploaded_file = request.FILES[uploaded_file_key]

    #Determine the uploaded extension
    file_extension = os.path.splitext(uploaded_file.name)[-1].lower()

    #Converts Excel to CSV
    if file_extension in ['.xls', '.xlsx']:
        try:
            #Using pandas to convert
            excel_data = pd.read_excel(uploaded_file, skiprows=1)
            print("Excel data preview after skipping title row:", excel_data.head())  # Debugging: check data after skipping rows
            csv_data = excel_data.to_csv(index=False)
            io_string = io.StringIO(csv_data)
        except Exception as e:
            return Response({"error": f"Failed to process Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
    #If extension is csv read striaght away
    elif file_extension == '.csv':
        data_set = uploaded_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)  # skip one row to get the headers

    #File is not CSV or Excel
    else:
        return Response({"error": "Unsupported file format, Please upload either CSV or Excel in xls or xlsx"})

    csv_reader = csv.DictReader(io_string)

    student_duplicates = set()
    course_duplicates = set()
    grade_duplicates = set()
    new_students = set()
    new_courses = set()
    new_grades = set()

    for row in csv_reader:
        StudentId = row.get('Empl ID', '').strip()
        Lastname = row.get('Surname', '').strip()
        FirstName = row.get('First Name', '').strip()
        AcadProgDesc = row.get('Academic Program Descr', '').strip()
        PhoneNo = row.get('Phone No.', '').strip()
        Email = row.get('Email Address', '').strip()
        CatalogueNo = row.get('Catalogue Number', '').strip()
        Subject = row.get('Subject', '').strip()
        ClassDescription = row.get('Class Descr', '').strip()
        Trimester = row.get('Term', '').strip()
        CourseId = Subject + CatalogueNo

        # Check if student already exists
        if Students.objects.filter(studentid=StudentId).exists():
            if StudentId:  # Only add non-empty values
                student_duplicates.add(StudentId)
        else:
            Students.objects.create(
                studentid=StudentId,
                lastname=Lastname,
                firstname=FirstName,
                acadprogdesc=AcadProgDesc,
                phoneno=PhoneNo,
                email=Email
            )
            new_students.add(StudentId)

        # Check if course exists
        if Courses.objects.filter(courseid=CourseId).exists():
            if CourseId:  # Only add non-empty values
                course_duplicates.add(CourseId)
        else:
            Courses.objects.create(
                courseid=CourseId,
                catalogueno=CatalogueNo,
                subject=Subject,
                classdescription=ClassDescription,
            )
            new_courses.add(CourseId)

        # Check if the studentgrades already exists before inserting
        if Studentgrades.objects.filter(courseid=CourseId, studentid=StudentId, trimester=Trimester).exists():
            if StudentId and CourseId:  # Only add non-empty values
                grade_duplicates.add(f"{StudentId}-{CourseId}")
        else:
            Studentgrades.objects.create(
                studentid=Students.objects.get(studentid=StudentId),
                courseid=Courses.objects.get(courseid=CourseId),
                currentscore=None,
                finalgrade=None,
                trimester=Trimester,
                flagstatus=0,
                assessments=None
            )
            new_grades.add(f"{StudentId}-{CourseId}")

    # Convert sets to lists and filter out any empty strings
    return Response({
        "message": "CSV file successfully uploaded and processed.",
        "student_duplicates": [s for s in student_duplicates if s],
        "course_duplicates": [c for c in course_duplicates if c],
        "grade_duplicates": [g for g in grade_duplicates if g],
        "new_students": list(new_students),
        "new_courses": list(new_courses),
        "new_grades": list(new_grades),
    }, status=status.HTTP_201_CREATED)



@api_view(['POST'])
def upload_grades(request):
    #Check for 'csv_file' or 'excel_file' is in the request
    uploaded_file_key = None

    if 'csv_file' in request.FILES:
        uploaded_file_key = 'csv_file'

    elif 'excel_file' in request.FILES:
        uploaded_file_key = 'excel_file'

    else:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)


    uploaded_file = request.FILES[uploaded_file_key]

    #Check for file extension in uploaded file
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    print(f"Uploaded file name: {uploaded_file.name}")
    io_string = None  # Initialize io_string for CSV processing
    
    
   

    # Process Excel file
    if file_extension in ['.xls', '.xlsx']:
        try:
            excel_data = pd.read_excel(uploaded_file,header=0, skiprows=[1, 2])
            print("Excel data after reading:", excel_data)  # Debugging step

            csv_data = excel_data.to_csv(index=False)
            io_string = io.StringIO(csv_data)
            csv_reader = csv.DictReader(io_string)
            headers = csv_reader.fieldnames  # Extract headers dynamically
            

        except Exception as e:
            print(f"Error processing Excel file: {e}")
            return Response({"error": f"Failed to process Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
     
    elif file_extension == '.csv':
        try:
            data_set = uploaded_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            csv_reader = csv.DictReader(io_string)
            headers = csv_reader.fieldnames  # Extract headers dynamically
            next(csv_reader)
            next(csv_reader)
            
            

        except Exception as e:
            print(f"Error processing CSV file: {e}")
            return Response({"error": f"Failed to process CSV file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({"Error": "Uploaded file type is wrong, plese upload only CSV or Excel files "})
    
    

    # Identify dynamic columns for journals and assessments

    
    journal_columns = [col for col in headers if col.startswith("Journal")]
    assessment_columns = [col for col in headers if col.startswith("Assessment") and col.endswith("Unposted Final Score")]
    quiz_columns = [col for col in headers if col.startswith("Quiz")]
    test_columns = [col for col in headers if col.startswith("Test")]

    for row in csv_reader:
        
        StudentId = row.get('SIS User ID', '').strip().lower()
        CurrentScore = row.get('Current Score', '').strip()
        FinalGrade = row.get('Final Score', '').strip()
        Section = row.get('Section', '').strip()
        #Trimester = Section.split(' ')[0] Issue does not match with the other csv file
        CourseId = Section.split(' ')[0]


        student = Studentgrades.objects.filter(courseid=CourseId, studentid=StudentId).first()
        # check if student already exists
        if student:
            try:
                # Dynamically build JSON for journals and assessments
                assessments = {
                    col: float(row.get(col, 0)) if row.get(col) else None
                    for col in journal_columns + assessment_columns + quiz_columns + test_columns
                }

                if CurrentScore and float(CurrentScore) <= 50 and student.flagstatus == 0:
                    flag_status = 2
                elif CurrentScore and float(CurrentScore) > 50 and student.flagstatus == 0:
                    flag_status = 0
                else:
                    flag_status = student.flagstatus

                Studentgrades.objects.filter(courseid=CourseId, studentid=StudentId).update(
                    assessments=assessments,  # Store dynamic data
                    currentscore=float(CurrentScore) if CurrentScore else None,
                    finalgrade=float(FinalGrade) if FinalGrade else None,
                    flagstatus=flag_status
                )

                    
            except IntegrityError:
                return Response({"error": f"Error inserting student {StudentId}. Does not exist."}, 
                                status=status.HTTP_409_CONFLICT)

    return Response({"message": "CSV file successfully uploaded and processed."}, status=status.HTTP_201_CREATED)


def index(request):
    # Serve the React index.html for frontend routes
    return render(request, 'index.html')


