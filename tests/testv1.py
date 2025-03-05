import unittest
from fastapi.testclient import TestClient
from core.main import app
import json
import os

# Create a test client
client = TestClient(app)

# Test data for dynamic endpoints
test_cases = {
    "write_sales_pitch": {
        "endpoint": "/v1/write/sales_pitch",
        "payload": {"text": "Revolutionary AI tool!"},
        "expected": "Compelling sales pitch based on: Revolutionary AI tool!"
    },
    "generate_image": {
        "endpoint": "/v1/generate/image",
        "payload": {"text": "Sunset over mountains"},
        "expected": "Generated an image based on: Sunset over mountains"
    },
    "trade_crypto": {
        "endpoint": "/v1/trade/crypto",
        "payload": {"text": "Buy 1 BTC"},
        "expected": "Executed crypto trade based on: Buy 1 BTC"
    },
    "suggest_movies": {
        "endpoint": "/v1/suggest/movies",
        "payload": {"text": "Sci-fi recommendations"},
        "expected": ["Inception", "Interstellar", "The Matrix"]
    }
}

# Load URFN registry
URFN_REGISTRY_FILE = "urfn_Registry.json"
with open(URFN_REGISTRY_FILE, "r") as f:
    urfn_registry = json.load(f)

class TestAPI(unittest.TestCase):

    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_dynamic_endpoints(self):
        """Test dynamic endpoints based on URFNs."""
        for urfn, case in test_cases.items():
            with self.subTest(urfn=urfn):
                response = client.post(case["endpoint"], json=case["payload"])
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json().get("result"), case["expected"])

    def test_missing_urfn(self):
        """Test missing URFN in the registry."""
        response = client.post("/v1/unknown/function", json={"text": "Test"})
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity for undefined endpoint

    def test_invalid_module_in_registry(self):
        """Test invalid module configuration in URFN registry."""
        # Temporarily modify the registry
        urfn_registry["invalid_module_test"] = {
            "module": "non_existent_module",
            "function": "non_existent_function"
        }
        with open(URFN_REGISTRY_FILE, "w") as f:
            json.dump(urfn_registry, f)

        # Test endpoint for invalid module
        response = client.post("/v1/invalid/module", json={"text": "Test"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Function loading error", response.json().get("detail", ""))

        # Restore original registry
        del urfn_registry["invalid_module_test"]
        with open(URFN_REGISTRY_FILE, "w") as f:
            json.dump(urfn_registry, f)

    def test_invalid_function_in_registry(self):
        """Test invalid function configuration in URFN registry."""
        # Temporarily modify the registry
        urfn_registry["write_sales_pitch"]["function"] = "non_existent_function"
        with open(URFN_REGISTRY_FILE, "w") as f:
            json.dump(urfn_registry, f)

        # Test endpoint for invalid function
        response = client.post("/v1/write/sales_pitch", json={"text": "Test"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Function loading error", response.json().get("detail", ""))

        # Restore original registry
        urfn_registry["write_sales_pitch"]["function"] = "generate_sales_pitch"
        with open(URFN_REGISTRY_FILE, "w") as f:
            json.dump(urfn_registry, f)

    def test_invalid_payload(self):
        """Test invalid payload structure."""
        response = client.post("/v1/write/sales_pitch", json={"invalid_key": "Test"})
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity

if __name__ == "__main__":
    unittest.main()
