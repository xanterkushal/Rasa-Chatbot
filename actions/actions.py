from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sqlalchemy import create_engine
from fuzzywuzzy import process



import re

import mysql.connector

    
    

    

class ActionFetchCurriculum(Action):
    def name(self) -> Text:
        return "action_fetch_curriculum"
    
    def preprocess_input(self, text: str) -> str:
        # Convert text to lowercase
        return text.lower()
    # ... (other methods)

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get course type and name from tracker
        ctype = self.preprocess_input(tracker.get_slot('ctype'))
        course = self.preprocess_input(tracker.get_slot('course'))

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
                # Query the database with the matched course name
                query = f"SELECT a.curriculum FROM academics a JOIN course c ON a.course_id = c.course_id WHERE LOWER(c.course_name) = '{matched_course}'"
                cursor.execute(query)
                curriculum = cursor.fetchone()

                if curriculum:
                    # Send response if curriculum details are found
                    dispatcher.utter_message(text=f"The curriculum for {ctype} ({matched_course}) is: {curriculum[0]}")
                    return []
            
            # Send a message if curriculum details are not found
            dispatcher.utter_message(text=f"Sorry, the curriculum details for {ctype} ({course}) are not available.")

        except mysql.connector.Error as err:
            # Handle database errors
            dispatcher.utter_message(text=f"Error accessing database: {err}")

        finally:
            # Close cursor and database connection
            if 'mydb' in locals() and mydb.is_connected():
                cursor.close()
                mydb.close()

        return []


    
    
    
    
    

    
    
     


    

