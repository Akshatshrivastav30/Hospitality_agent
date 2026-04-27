from django.test import TestCase
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import HumanMessage to fix the 'tuple' error
from langchain_core.messages import HumanMessage
from Hospitalityspecific import gatekeeper_node

class TripMateAgentTests(TestCase):
    def test_gatekeeper_allows_travel(self):
        """Verify travel queries are flagged as True"""
        # Change the message from a tuple to a HumanMessage object
        state = {
            "messages": [HumanMessage(content="Plan a 2 day trip to Indore")],
            "is_travel_related": None
        }
        result = gatekeeper_node(state)
        self.assertTrue(result["is_travel_related"])

    def test_gatekeeper_blocks_irrelevant(self):
        """Verify non-travel queries are flagged as False"""
        # Change the message from a tuple to a HumanMessage object
        state = {
            "messages": [HumanMessage(content="How do I fix a car?")],
            "is_travel_related": None
        }
        result = gatekeeper_node(state)
        self.assertFalse(result["is_travel_related"])