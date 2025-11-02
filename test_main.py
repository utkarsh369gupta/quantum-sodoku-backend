"""
Test suite for the solver comparison API.
Run with: pytest test_main.py -v
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_status_endpoint():
    """Test the health check endpoint"""
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

def test_login_endpoint():
    """Test the login endpoint"""
    response = client.post("/api/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "message" in data
    assert data["message"] == "Login successful for user: testuser"

def test_classical_solver_endpoint():
    """Test the classical solver endpoint"""
    puzzle = [[1, 0, 0, 0], [0, 2, 0, 0], [0, 0, 3, 0], [0, 0, 0, 4]]
    response = client.post("/api/run/classical", json={"puzzle": puzzle})
    assert response.status_code == 200
    data = response.json()
    assert "solution" in data
    assert "time" in data
    assert isinstance(data["time"], (int, float))

def test_quantum_solver_endpoint():
    """Test the quantum solver endpoint"""
    puzzle = [[1, 0, 0, 0], [0, 2, 0, 0], [0, 0, 3, 0], [0, 0, 0, 4]]
    response = client.post("/api/run/quantum", json={"puzzle": puzzle})
    assert response.status_code == 200
    data = response.json()
    assert "state" in data
    assert "time" in data
    assert "counts" in data
    assert isinstance(data["time"], (int, float))
    assert isinstance(data["counts"], dict)

def test_compare_endpoint():
    """Test the comparison endpoint"""
    puzzle = [[1, 0, 0, 0], [0, 2, 0, 0], [0, 0, 3, 0], [0, 0, 0, 4]]
    response = client.post("/api/run/compare", json={"puzzle": puzzle})
    assert response.status_code == 200
    data = response.json()
    assert "classical" in data
    assert "quantum" in data
    assert "comparison" in data
    assert "solution" in data["classical"]
    assert "state" in data["quantum"]
    assert "counts" in data["quantum"]

def test_invalid_puzzle_format():
    """Test error handling for invalid puzzle format"""
    response = client.post("/api/run/classical", json={"puzzle": "invalid"})
    assert response.status_code == 422  # Validation error

