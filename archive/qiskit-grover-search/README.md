# qiskit-grover-search

This project implements Grover's search algorithm using Qiskit. Grover's algorithm is a quantum algorithm that provides a quadratic speedup for unstructured search problems.

## Overview

The Grover search algorithm is designed to search through an unsorted database of $N$ items in $O(\sqrt{N})$ time, which is significantly faster than classical algorithms that require $O(N)$ time.

## Project Structure

```
qiskit-grover-search
├── src
│   ├── main.py          # Entry point for the application
│   ├── circuits         # Contains quantum circuit implementations
│   │   ├── __init__.py
│   │   └── grover.py    # Implementation of the Grover search algorithm
│   ├── utils            # Contains utility functions
│   │   ├── __init__.py
│   │   └── oracle.py    # Oracle function for Grover's algorithm
│   └── tests            # Contains unit tests
│       ├── __init__.py
│       └── test_grover.py # Unit tests for the Grover search implementation
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd qiskit-grover-search
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the Grover search algorithm, execute the `main.py` file:

```bash
python src/main.py
```

This will initialize the quantum circuit and execute the Grover search algorithm based on the specified oracle.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.