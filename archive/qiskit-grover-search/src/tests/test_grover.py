import unittest
from circuits.grover import GroverCircuit

class TestGroverCircuit(unittest.TestCase):

    def setUp(self):
        self.grover = GroverCircuit()

    def test_circuit_initialization(self):
        self.assertIsNotNone(self.grover.circuit)

    def test_execute_search(self):
        result = self.grover.execute_search()
        self.assertIn('found', result)

if __name__ == '__main__':
    unittest.main()