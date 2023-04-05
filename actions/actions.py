# This files contains your custom actions which can be used to run custom Python code.
# See this guide on how to implement these action: https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

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
        """Validate `body_type` value."""

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
        """Validate `engine` value."""

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
        """Validate `fuel` value."""

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
        """Validate `transmission` value."""

        if slot_value.lower() not in ALLOWED_CAR_TRANSMISSIONS:
            dispatcher.utter_message(
                text=f"I don't recognise that transmission. Our models are only avaiable as automatic or manual."
            )
            return {"transmission": None}
        dispatcher.utter_message(text=f"Ok, you are searching for a {slot_value} car.")
        return {"transmission": slot_value}
    
# class UtterCarSlots(Action):

#     def name(self) -> Text:
#         return "utter_car_slots"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any]
#         ) -> List[Dict[Text, Any]]:
        
#         engine_value = tracker.get_slot("engine")
#         body_type_value = tracker.get_slot("body_type")
#         fuel_value = tracker.get_slot("fuel")
#         transmission_value = tracker.get_slot("transmission")
        
#         if engine_value == "electric":
#             response = f"I am searching for an electric {body_type_value} Mercedes."
#         else:
#             response = f"I am searching for a {body_type_value} Mercedes with {fuel_value} {engine_value} engine and {transmission_value} transmission."
        
#         dispatcher.utter_message(response)
#         return []