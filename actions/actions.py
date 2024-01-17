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
        # Convert text to lowercase
        return text.lower()

    def fetch_academic_info(self, course_name: str, requested_info: str, cursor) -> str:
        # Query the database with the matched course name and requested info
        query = f"SELECT {requested_info} FROM academics a JOIN course c ON a.course_id = c.course_id " \
                f"WHERE LOWER(c.course_name) = '{course_name}'"
        cursor.execute(query)
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

                # Fetch all course names from the database
                cursor.execute("SELECT LOWER(course_name) FROM course")
                all_course_names = [row[0] for row in cursor.fetchall()]

                # Use fuzzy matching to find closest course names
                matched_course, score = process.extractOne(course, all_course_names)

                threshold = 70  # Adjust the threshold as needed

                if score >= threshold:
                    # Fetch academic info based on the requested info
                    academic_info = self.fetch_academic_info(matched_course, requested_info, cursor)

                    if academic_info is not None:
                        # Send response if academic details are found
                        response_message = f"The {requested_info} for {ctype} ({matched_course}) is: {academic_info}"
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



    
    
    
    
    

    
    
     


    

