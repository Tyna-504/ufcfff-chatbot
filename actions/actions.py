# This files contains your custom actions which can be used to run custom Python code.
# See this guide on how to implement these action: https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import sqlite3

ALLOWED_CAR_BODY_TYPES = ["saloon", "suv", "hatchback", "estate", "coupe", "cabriolet"]
ALLOWED_CAR_engineS = ["combustion engine", "mild hybrid", "plug-in hybrid", "electric"]
ALLOWED_CAR_FUELS = ["diesel", "petrol"]
ALLOWED_CAR_TRANSMISSIONS = ["automatic", "manual"]

class ValidateCarForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_car_form"
    
    # skip asking for 'fuel' and 'transmission' if engine is electric
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

    # validate body_type slot
    def validate_body_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """ Validate `body_type` value """

        if slot_value.lower() not in ALLOWED_CAR_BODY_TYPES:
            dispatcher.utter_message(text=f"Sorry, we only offer body types: saloon/SUV/hatchback/estate/coupe/cabriolet.")
            return {"body_type": None}
        dispatcher.utter_message(text=f"Ok, you are searching for a {slot_value} car.")
        return {"body_type": slot_value}

    # validate engine slot
    def validate_engine(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """ Validate `engine` value """

        if slot_value.lower() not in ALLOWED_CAR_engineS:
            dispatcher.utter_message(
                text=f"I don't recognise that engine. Our models are only avaiable as {'/'.join(ALLOWED_CAR_engineS)}."
            )
            return {"engine": None}
        dispatcher.utter_message(text=f"Ok, you are searching for a {slot_value} car.")
        return {"engine": slot_value}

    # validate fuel slot
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

    # validate transmission slot
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

# action for querying the db
class QueryCar(Action):
    def name(self) -> Text:
        return "query_car"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        """

        """
        
        conn = QueryCar.create_connection(db_file="./car_db/modelDB.db")
        
        slot_value = tracker.get_slot("body_type")
        slot_name = "body_type"

        get_query_results = QueryCar.select_by_slot(conn, slot_name, slot_value)
        dispatcher.utter_message(text=str(get_query_results))  
        return[]

    # define function that creates connection with the db
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

    # define function that queries db using one slot and print out results
    def select_by_slot(conn, slot_name, slot_value):
        """
        Query rows in the mercedesmodels table given a certain slot
        :param conn: the Connection object
        :return:
        """
        cur = conn.cursor()
        cur.execute(f"""SELECT * FROM mercedesmodels WHERE {slot_name}='{slot_value}'""")
        
        rows = cur.fetchall()

        if len(list(rows)) < 1:
            return "There are no models matching your query."
        else:
            model_list = [f"{row[2]} {row[3]} {row[4]} by {row[1]}" for row in rows]
            model_list_text = "\n".join([f"- {model}" for model in model_list])
            return f"Try the following models:\n{model_list_text}"