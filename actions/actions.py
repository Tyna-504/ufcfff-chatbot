from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import sqlite3
from fuzzywuzzy import process

ALLOWED_CAR_BODY_TYPES = ["saloon", "suv", "hatchback", "estate", "coupe", "cabriolet"]
ALLOWED_CAR_ENGINES = ["combustion engine", "mild hybrid", "plug-in hybrid", "electric"]
ALLOWED_CAR_FUELS = ["diesel", "petrol"]
ALLOWED_CAR_TRANSMISSIONS = ["automatic", "manual"]

class ValidateCarForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_car_form"
    
    # Skip asking for 'fuel' and 'transmission' if engine is electric
    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        engine_value = tracker.get_slot("engine")
        updated_slots = domain_slots.copy()
        if engine_value == "electric":
            # If the user wants electric, do not request the 'fuel' and 'transmission' slots
            updated_slots.remove("fuel")
            updated_slots.remove("transmission")
        return updated_slots

    # Validate body_type slot
    def validate_body_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """ Validate `body_type` value """

        if slot_value.lower() not in ALLOWED_CAR_BODY_TYPES:
            dispatcher.utter_message(
                text=f"I don't recognise this body type. We only offer body types: {'/'.join(ALLOWED_CAR_BODY_TYPES)}."
                )
            return {"body_type": None}
        dispatcher.utter_message(text=f"Ok, you are searching for a {slot_value} car.")
        return {"body_type": slot_value}

    # Validate engine slot
    def validate_engine(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """ Validate `engine` value """

        if slot_value.lower() not in ALLOWED_CAR_ENGINES:
            dispatcher.utter_message(
                text=f"I don't recognise that engine. Our models are only avaiable as {'/'.join(ALLOWED_CAR_ENGINES)}."
            )
            return {"engine": None}
        dispatcher.utter_message(text=f"Ok, you are searching for a {slot_value} car.")
        return {"engine": slot_value}

    # Validate fuel slot
    def validate_fuel(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """ Validate `fuel` value """

        if slot_value.lower() not in ALLOWED_CAR_FUELS:
            dispatcher.utter_message(
                text=f"I don't recognise that fuel type. Our models are only avaiable as {'/'.join(ALLOWED_CAR_FUELS)}."
            )
            return {"fuel": None}
        dispatcher.utter_message(text=f"Ok, you are searching for a {slot_value} car.")
        return {"fuel": slot_value}

    # Validate transmission slot
    def validate_transmission(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """ Validate `transmission` value """

        if slot_value.lower() not in ALLOWED_CAR_TRANSMISSIONS:
            dispatcher.utter_message(
                text=f"I don't recognise that transmission. Our models are only avaiable as automatic or manual."
            )
            return {"transmission": None}
        dispatcher.utter_message(text=f"Ok, you are searching for a {slot_value} car.")
        return {"transmission": slot_value}
    
# Custom action to handle asking about required slots (form interruption)
class DispatchCarExplanations(Action):
    def name(self) -> Text:
        return "dispatch_car_explanations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        """
        Retrieves the current intent from the tracker, dispatches appropriate message to the user.
        Handles form interruption for when user is asking about the requested slots.
        """
        
        # Get the current intent
        current_intent = tracker.latest_message['intent']['name']

        # Use a switch statement to dispatch different messages based on the intent
        if current_intent == 'ask_body_type':
            dispatcher.utter_message(
                text=f"""We offer the following body types: {'/'.join(ALLOWED_CAR_BODY_TYPES)}.""")
        elif current_intent == 'ask_engine':
            dispatcher.utter_message(
                text=f"""We offer the following engines: {'/'.join(ALLOWED_CAR_ENGINES)}.""")
        elif current_intent == 'ask_fuel':
            dispatcher.utter_message(
                text=f"""We offer the following fuel types: {'/'.join(ALLOWED_CAR_FUELS)}.""")
        elif current_intent == 'ask_transmission':
            dispatcher.utter_message(
                text=f"""We offer the following transmissions: {'/'.join(ALLOWED_CAR_TRANSMISSIONS)}. Please note that all models currently in production are automatic only.""")
        return []        
    
# Custom action for connecting to db and returning results
class DbQuerying:

    # Define function that creates connection with the db
    def create_connection(db_file):
        """
        Create a database connection to the SQLite database specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print(e)
        return conn

    # Define funcrion for fuzzy matching
    def get_closest_value(conn, slot_name, slot_value): 
        """
        Given a db column and text input, find the closest match for the input in the column
        """

        # Get a list of all distinct values from target column
        fuzzy_match_cur = conn.cursor() # create second cursor
        fuzzy_match_cur.execute(f"""SELECT DISTINCT {slot_name} FROM mercedesmodels""")

        column_values = fuzzy_match_cur.fetchall()

        top_match = process.extractOne(slot_value, column_values)

        return(top_match[0])

    # Define function that queries db using one slot and print out results
    def select_by_slot(conn, slot_name, slot_value):
        """
        Query rows in the mercedesmodels table given a certain slot
        :param conn: the Connection object
        :return: array of rows
        """
        cur = conn.cursor()
        cur.execute(f'''SELECT * FROM mercedesmodels WHERE {slot_name}="{slot_value}"''')
        # note: mercedesmodels can be as a variable if we had multiple tables
        
        rows = cur.fetchall()
        return(rows)

# Custom action for querying the db - recommendations
class QueryCar(Action):
    def name(self) -> Text:
        return "query_car"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        """
        Runs a query using all slots. Finds a match for all if possible, otherwise a match for the
        only body_type, engine, fuel, transmission, in that order. Output is utterance directly to the
        user with all matching rows, in a bullet point format.
        """
        
        # Establish connection
        conn = DbQuerying.create_connection(db_file="./car_db/modelDB.db")
        
        # Retrieve slot values and get matching results
        slots = {
            "body_type": tracker.get_slot("body_type"),
            "engine": tracker.get_slot("engine"),
            "fuel": tracker.get_slot("fuel"),
            "trans": tracker.get_slot("transmission")
        }  # dictionary to store slot values

        query_results_intersection = None  # initialize intersection results to None

        # Loop through each slot and retrieve slot value and query results
        for slot_name, slot_value in slots.items():
            if slot_value:  # skip if slot value is empty
                query_results = DbQuerying.select_by_slot(conn=conn, slot_name=slot_name, slot_value=slot_value)
                if query_results_intersection is None:
                    query_results_intersection = set(query_results)
                else:
                    query_results_intersection &= set(query_results)

        # Convert query results to list
        if query_results_intersection is not None:
            query_results_intersection = list(query_results_intersection)

        # Return no match if no right info in the db
        no_match_text = "I couldn't find exactly what you wanted, but you might like these models."

        # Return info for intersection, or fallback to individual slots or nothing
        if query_results_intersection and len(query_results_intersection) > 0:
            return_text = QueryCar.rows_info_as_text_recommend(query_results_intersection)
        elif any(len(slot_results) > 0 for slot_results in slots.values()):
            # If there's no intersection, check if any individual slot has results and fallback to that slot's results
            combined_results = []
            for slot_name, slot_value in slots.items():
                if slot_value:
                    combined_results.extend(DbQuerying.select_by_slot(conn=conn, slot_name=slot_name, slot_value=slot_value))
            return_text = no_match_text + QueryCar.rows_info_as_text_recommend(combined_results)
        else:
            return_text = QueryCar.rows_info_as_text_recommend(query_results_intersection)


        #add fuzzy matching
        #slot_value = DbQuerying.get_closest_value(conn=conn, slot_name=slot_name, slot_value=slot_value)[0]

        dispatcher.utter_message(text=str(return_text))  
        return[]       
        
    # Define function to turn query results into text
    def rows_info_as_text_recommend(rows):
        """
        Return all the rows passed in as a human-readable text. 
        If there are no rows, return no match.
        """
        if len(list(rows)) < 1:
            return "There are no models matching your query."
        else:
            # get model_class, model, body_type, make
            model_list = [f"{row[2]} {row[3]} {row[4]} by {row[1]}" for row in rows]
            model_list_text = "\n".join([f"- {model}" for model in model_list])
            return f"Try the following models:\n{model_list_text}"
        
# Custom action for querying the db - model class
class QueryModelClass(Action):

    def name(self) -> Text:
        return "query_model_class"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Runs a query using only the model_class column with fuzzy matching. 
        Outputs an utterance to the user w/ the relevent information
        """
        conn = DbQuerying.create_connection(db_file="./car_db/modelDB.db")


        slot_value = tracker.latest_message['entities'][0]['value'] #get entity 'car_model_class'
        slot_name = "model_class"
        
        # add fuzzy matching
        slot_value = DbQuerying.get_closest_value(conn=conn, slot_name=slot_name,slot_value=slot_value)[0]

        get_query_results = DbQuerying.select_by_slot(conn=conn,slot_name=slot_name,slot_value=slot_value)
        return_text = QueryModelClass.rows_info_as_text_class(get_query_results)
        dispatcher.utter_message(text=str(return_text))
        return[]
    
    # Define function to turn query results into text
    def rows_info_as_text_class(rows):
        """
        Return all the rows passed in as a human-readable text. 
        If there are no rows, return no match.
        """
        if len(list(rows)) < 1:
            return "There are no models for the specified model class."
        else:
            # get model, body_type, make
            model_list = [f"{row[3]} {row[4]} by {row[1]}" for row in rows]
            model_list_text = "\n".join([f"- {model}" for model in model_list])
            return f"We offer the following models for the given class:\n{model_list_text}"
        
# Custom action for querying the db - model
class QueryModel(Action):

    def name(self) -> Text:
        return "action_query_model"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Runs a query using only the model column with fuzzy matching. 
        Outputs an utterance to the user w/ the relevent information
        """
        conn = DbQuerying.create_connection(db_file="./car_db/modelDB.db")


        slot_value = tracker.get_slot("model_name")
        slot_name = "model"
        
        # add fuzzy matching
        slot_value = DbQuerying.get_closest_value(conn=conn, slot_name=slot_name,slot_value=slot_value)[0]

        get_query_results = DbQuerying.select_by_slot(conn=conn,slot_name=slot_name,slot_value=slot_value)
        return_text = QueryModel.rows_info_as_text_model(get_query_results)
        dispatcher.utter_message(text=str(return_text))
        return[]
    
    # Define function to turn query results into text
    def rows_info_as_text_model(rows):
        """
        Return all the rows passed in as a human-readable text. 
        If there are no rows, return no match.
        """
        if len(list(rows)) < 1:
            return "There are no models matching your query."
        else:
            model_list = []
            for row in rows:
                if row[10] == "electric":
                    model_list.append(f"""The {row[3]} is a {row[4]}, powered by an {row[10]} engine. It has {row[12]} doors and {row[11]} seats, and {row[13]} {row[14]} transmission.""")
                else:
                    model_list.append(f"""The {row[3]} is a {row[4]} powered by {row[8]} litre {row[6]} {row[7]} cylinder {row[9]} {row[10]}. It has {row[12]} doors and {row[11]} seats, and {row[13]} {row[14]} transmission.""")
            model_list_text = "\n".join([f"- {model}" for model in model_list])
            if len(rows) > 1:
                return f"""This model is available in multiple body types:\n{model_list_text}"""
            else:
                return model_list_text
                
# Custom action to clear the model_name slot after using it
class ResetSlotAction(Action):
    def name(self) -> Text:
        return "action_reset_slot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("model_name", None)]