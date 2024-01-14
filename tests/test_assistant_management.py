import os
import unittest
from chat import AssistantManager
from dotenv import load_dotenv

class TestAssistantManagerIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = os.path.join(base_dir, '../.env')
        load_dotenv(dotenv_path=dotenv_path, override=True)
        print('Setting up test...')

    def setUp(self):
        self.manager = AssistantManager(api_key=os.getenv('OPENAI_API_KEY'))

    def test_get_assistants(self):
        # Call the method
        response = self.manager.get_assistants()

        self.assertIsInstance(response, list)
        for assistant in response:
            self.assertIsInstance(assistant, object)
            self.assertTrue(hasattr(assistant, 'id'))
            self.assertTrue(hasattr(assistant, 'object'))
            self.assertTrue(hasattr(assistant, 'created_at'))
            self.assertTrue(hasattr(assistant, 'name'))
            self.assertTrue(hasattr(assistant, 'description'))
            self.assertTrue(hasattr(assistant, 'model'))
            self.assertTrue(hasattr(assistant, 'instructions'))
            self.assertTrue(hasattr(assistant, 'tools'))
            self.assertTrue(hasattr(assistant, 'file_ids'))
            self.assertTrue(hasattr(assistant, 'metadata'))



    # Add more test methods as needed...

if __name__ == '__main__':
    unittest.main()