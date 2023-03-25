# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List

# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

## My Custom Actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

ALLOWED_CAR_BODY_TYPES = ["saloon", "suv", "hatchback", "estate", "coupe", "cabriolet"]
ALLOWED_CAR_FUELS = ["diesel", "petrol", "electricity"]
ALLOWED_CAR_POWERTRAINS = ["combustion engine", "mild hybrid", "plug-in hybrid", "electric"]
ALLOWED_CAR_TRANSMISSIONS = ["automatic", "manual"]

class ValidateCarForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_car_form"

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

    # validate powertrain slot
    def validate_powertrain(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `powertrain` value."""

        if slot_value.lower() not in ALLOWED_CAR_POWERTRAINS:
            dispatcher.utter_message(
                text=f"I don't recognise that powertrain. Our models are only avaiable as {'/'.join(ALLOWED_CAR_POWERTRAINS)}."
            )
            return {"powertrain": None}
        dispatcher.utter_message(text=f"Ok, you are searching for a {slot_value} car.")
        return {"powertrain": slot_value}

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