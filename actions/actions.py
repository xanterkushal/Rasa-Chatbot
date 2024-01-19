from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sqlalchemy import create_engine
from fuzzywuzzy import process



import re

import mysql.connector

    
    

    

class ActionFetchAcademicDetails(Action):
    def name(self) -> Text:
        return "action_fetch_academic_details"

    def preprocess_input(self, text: str) -> str:
        # Convert text to lowercase, remove extra spaces and special characters
        text = text.lower()
        text = re.sub(' +', ' ', text)  # Remove extra spaces
        text = re.sub('[^A-Za-z0-9\s]', '', text)  # Remove special characters
        return text.strip()

    def find_closest_match(self, column_names, target_column):
        matched_column, score = process.extractOne(target_column, column_names)
        threshold = 70  # Adjust the threshold as needed
        return matched_column if score >= threshold else None

    def find_closest_course(self, course_names, target_course):
        matched_course, score = process.extractOne(target_course, course_names)
        threshold = 70  # Adjust the threshold as needed
        return matched_course if score >= threshold else None

    def fetch_academic_info(self, course_name: str, requested_info: str, cursor) -> str:
        # Use parameterized query to prevent SQL injection
        query = f"SELECT {requested_info} FROM academics a JOIN course c ON a.course_id = c.course_id " \
                f"WHERE LOWER(c.course_name) = %s"
        cursor.execute(query, (course_name,))
        academic_info = cursor.fetchone()

        return academic_info[0] if academic_info else None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get course type, name, and requested info from tracker
        ctype = self.preprocess_input(tracker.get_slot('ctype'))
        course = self.preprocess_input(tracker.get_slot('course'))
        
        # Check if 'requested_info' slot is set
        requested_info = tracker.get_slot('requested_info')
        if requested_info is not None:
            requested_info = self.preprocess_input(requested_info)

            try:
                # Connect to the database
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="passw0rd",
                    database="my_rasa"
                )

                # Create a cursor to execute SQL queries
                cursor = mydb.cursor()

                # Fetch all column names from the academics table
                cursor.execute("DESCRIBE academics")
                column_names = [row[0].lower() for row in cursor.fetchall()]

                # Fetch all course names from the course table
                cursor.execute("SELECT LOWER(course_name) FROM course")
                course_names = [row[0] for row in cursor.fetchall()]

                # Use fuzzy matching to find closest column name and course name
                matched_info = self.find_closest_match(column_names, requested_info)
                matched_course = self.find_closest_course(course_names, course)

                if matched_info and matched_course:
                    # Fetch academic info based on the matched column name and course name
                    academic_info = self.fetch_academic_info(matched_course, matched_info, cursor)

                    if academic_info is not None:
                        # Send response if academic details are found
                        response_message = f"The {matched_info} for {ctype} ({matched_course}) is: {academic_info}"
                        dispatcher.utter_message(text=response_message)
                        return []

                # Send a message if academic details are not found
                dispatcher.utter_message(text=f"Sorry, the {requested_info} for {ctype} ({course}) are not available.")

            except mysql.connector.Error as err:
                # Handle database errors
                dispatcher.utter_message(text=f"Error accessing database: {err}")

            finally:
                # Close cursor and database connection
                if 'mydb' in locals() and mydb.is_connected():
                    cursor.close()
                    mydb.close()

        else:
            # Handle case where 'requested_info' is not set
            dispatcher.utter_message(text="Sorry, I couldn't understand the request. Please provide a valid requested_info.")

        return []
    



class ActionFetchPlacementInfo(Action):
    def name(self) -> Text:
        return "action_fetch_placement_info"

    def preprocess_input(self, text: str) -> str:
        # Convert text to lowercase, remove extra spaces and special characters
        text = text.lower()
        text = re.sub(' +', ' ', text)  # Remove extra spaces
        text = re.sub('[^A-Za-z0-9\s]', '', text)  # Remove special characters
        return text.strip()

    def find_closest_match(self, column_names, target_column):
        matched_column, score = process.extractOne(target_column, column_names)
        threshold = 70  # Adjust the threshold as needed
        return matched_column if score >= threshold else None

    def find_closest_course(self, course_names, target_course):
        matched_course, score = process.extractOne(target_course, course_names)
        threshold = 70  # Adjust the threshold as needed
        return matched_course if score >= threshold else None

    def fetch_placement_info(self, course_name: str, requested_info: str, cursor) -> str:
        # Use parameterized query to prevent SQL injection
        query = f"SELECT {requested_info} FROM placementinfo p JOIN course c ON p.course_id = c.course_id " \
                f"WHERE LOWER(c.course_name) = %s"
        cursor.execute(query, (course_name,))
        placement_info = cursor.fetchone()

        return placement_info[0] if placement_info else None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get course type, name, and requested info from tracker
        ctype = self.preprocess_input(tracker.get_slot('ctype'))
        course = self.preprocess_input(tracker.get_slot('course'))
        
        # Check if 'requested_info' slot is set
        requested_info = tracker.get_slot('requested_info')
        if requested_info is not None:
            requested_info = self.preprocess_input(requested_info)

            try:
                # Connect to the database
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="passw0rd",
                    database="my_rasa"
                )

                # Create a cursor to execute SQL queries
                cursor = mydb.cursor()

                # Fetch all column names from the placementinfo table
                cursor.execute("DESCRIBE placementinfo")
                column_names = [row[0].lower() for row in cursor.fetchall()]

                # Fetch all course names from the course table
                cursor.execute("SELECT LOWER(course_name) FROM course")
                course_names = [row[0] for row in cursor.fetchall()]

                # Use fuzzy matching to find closest column name and course name
                matched_info = self.find_closest_match(column_names, requested_info)
                matched_course = self.find_closest_course(course_names, course)

                if matched_info and matched_course:
                    # Fetch placement info based on the matched column name and course name
                    placement_info = self.fetch_placement_info(matched_course, matched_info, cursor)

                    if placement_info is not None:
                        # Send response if placement details are found
                        response_message = f"The {matched_info} for {ctype} ({matched_course}) is: {placement_info}"
                        dispatcher.utter_message(text=response_message)
                        return []

                # Send a message if placement details are not found
                dispatcher.utter_message(text=f"Sorry, the {requested_info} for {ctype} ({course}) are not available in placement info.")

            except mysql.connector.Error as err:
                # Handle database errors
                dispatcher.utter_message(text=f"Error accessing database: {err}")

            finally:
                # Close cursor and database connection
                if 'mydb' in locals() and mydb.is_connected():
                    cursor.close()
                    mydb.close()

        else:
            # Handle case where 'requested_info' is not set
            dispatcher.utter_message(text="Sorry, I couldn't understand the request. Please provide a valid requested_info.")

        return []


class ActionFetchFacultyInfo(Action):
    def name(self) -> Text:
        return "action_fetch_faculty_info"

    def preprocess_input(self, text: str) -> str:
        # Convert text to lowercase, remove extra spaces and special characters
        text = text.lower()
        text = re.sub(' +', ' ', text)  # Remove extra spaces
        text = re.sub('[^A-Za-z0-9\s]', '', text)  # Remove special characters
        return text.strip()

    def find_closest_match(self, column_names, target_column):
        matched_column, score = process.extractOne(target_column, column_names)
        threshold = 70  # Adjust the threshold as needed
        return matched_column if score >= threshold else None

    def find_closest_course(self, course_names, target_course):
        matched_course, score = process.extractOne(target_course, course_names)
        threshold = 70  # Adjust the threshold as needed
        return matched_course if score >= threshold else None

    def fetch_faculty_info(self, course_name: str, requested_info: str, cursor) -> str:
        # Use parameterized query to prevent SQL injection
        query = f"SELECT {requested_info}, link FROM facultyinfo f JOIN course c ON f.course_id = c.course_id " \
                f"WHERE LOWER(c.course_name) = %s"
        cursor.execute(query, (course_name,))
        faculty_info = cursor.fetchone()

        return faculty_info if faculty_info else None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get course type, name, and requested info from tracker
        ctype = self.preprocess_input(tracker.get_slot('ctype'))
        course = self.preprocess_input(tracker.get_slot('course'))
        
        # Check if 'requested_info' slot is set
        requested_info = tracker.get_slot('requested_info')
        if requested_info is not None:
            requested_info = self.preprocess_input(requested_info)

            try:
                # Connect to the database
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="passw0rd",
                    database="my_rasa"
                )

                # Create a cursor to execute SQL queries
                cursor = mydb.cursor()

                # Fetch all column names from the facultyinfo table
                cursor.execute("DESCRIBE facultyinfo")
                column_names = [row[0].lower() for row in cursor.fetchall()]

                # Fetch all course names from the course table
                cursor.execute("SELECT LOWER(course_name) FROM course")
                course_names = [row[0] for row in cursor.fetchall()]

                # Use fuzzy matching to find closest column name and course name
                matched_info = self.find_closest_match(column_names, requested_info)
                matched_course = self.find_closest_course(course_names, course)

                if matched_info and matched_course:
                    # Fetch faculty info based on the matched column name and course name
                    faculty_info = self.fetch_faculty_info(matched_course, matched_info, cursor)

                    if faculty_info:
                        # Send response if faculty details are found
                        response_message = f"The {matched_info} for {ctype} ({matched_course}) is: {faculty_info[0]}\nFaculty Link: {faculty_info[1]}"
                        dispatcher.utter_message(text=response_message)
                        return []

                # Send a message if faculty details are not found
                dispatcher.utter_message(text=f"Sorry, the {requested_info} for {ctype} ({course}) are not available in faculty info.")

            except mysql.connector.Error as err:
                # Handle database errors
                dispatcher.utter_message(text=f"Error accessing database: {err}")

            finally:
                # Close cursor and database connection
                if 'mydb' in locals() and mydb.is_connected():
                    cursor.close()
                    mydb.close()

        else:
            # Handle case where 'requested_info' is not set
            dispatcher.utter_message(text="Sorry, I couldn't understand the request. Please provide a valid requested_info.")

        return []

class ActionFetchFuturePathInfo(Action):
    def name(self) -> Text:
        return "action_fetch_future_path_info"

    def preprocess_input(self, text: str) -> str:
        # Convert text to lowercase, remove extra spaces and special characters
        text = text.lower()
        text = re.sub(' +', ' ', text)  # Remove extra spaces
        text = re.sub('[^A-Za-z0-9\s]', '', text)  # Remove special characters
        return text.strip()

    def find_closest_match(self, column_names, target_column):
        matched_column, score = process.extractOne(target_column, column_names)
        threshold = 70  # Adjust the threshold as needed
        return matched_column if score >= threshold else None

    def find_closest_course(self, course_names, target_course):
        matched_course, score = process.extractOne(target_course, course_names)
        threshold = 70  # Adjust the threshold as needed
        return matched_course if score >= threshold else None

    def fetch_future_path_info(self, course_name: str, requested_info: str, cursor) -> str:
        # Use parameterized query to prevent SQL injection
        query = f"SELECT {requested_info} FROM futurepathinfo f JOIN course c ON f.course_id = c.course_id " \
                f"WHERE LOWER(c.course_name) = %s"
        cursor.execute(query, (course_name,))
        future_path_info = cursor.fetchone()

        return future_path_info[0] if future_path_info else None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get course type, name, and requested info from tracker
        ctype = self.preprocess_input(tracker.get_slot('ctype'))
        course = self.preprocess_input(tracker.get_slot('course'))
        
        # Check if 'requested_info' slot is set
        requested_info = tracker.get_slot('requested_info')
        if requested_info is not None:
            requested_info = self.preprocess_input(requested_info)

            try:
                # Connect to the database
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="passw0rd",
                    database="my_rasa"
                )

                # Create a cursor to execute SQL queries
                cursor = mydb.cursor()

                # Fetch all column names from the futurepathinfo table
                cursor.execute("DESCRIBE futurepathinfo")
                column_names = [row[0].lower() for row in cursor.fetchall()]

                # Fetch all course names from the course table
                cursor.execute("SELECT LOWER(course_name) FROM course")
                course_names = [row[0] for row in cursor.fetchall()]

                # Use fuzzy matching to find closest column name and course name
                matched_info = self.find_closest_match(column_names, requested_info)
                matched_course = self.find_closest_course(course_names, course)

                if matched_info and matched_course:
                    # Fetch future path info based on the matched column name and course name
                    future_path_info = self.fetch_future_path_info(matched_course, matched_info, cursor)

                    if future_path_info is not None:
                        # Send response if future path details are found
                        response_message = f"The {matched_info} for {ctype} ({matched_course}) is: {future_path_info}"
                        dispatcher.utter_message(text=response_message)
                        return []

                # Send a message if future path details are not found
                dispatcher.utter_message(text=f"Sorry, the {requested_info} for {ctype} ({course}) are not available in future path info.")

            except mysql.connector.Error as err:
                # Handle database errors
                dispatcher.utter_message(text=f"Error accessing database: {err}")

            finally:
                # Close cursor and database connection
                if 'mydb' in locals() and mydb.is_connected():
                    cursor.close()
                    mydb.close()

        else:
            # Handle case where 'requested_info' is not set
            dispatcher.utter_message(text="Sorry, I couldn't understand the request. Please provide a valid requested_info.")

        return []




    
    
    
    
    

    
    
     


    

