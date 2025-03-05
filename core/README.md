
### 🚀 **Example API Calls**

**1. Write an Email:**
```bash
curl -X POST "http://127.0.0.1:8000/v1/write/E-mail" -H "Content-Type: application/json" -d '{"text": "We have a great offer for you!"}'
```

**2. Generate an Image:**
```bash
curl -X POST "http://127.0.0.1:8000/v1/generate/Image" -H "Content-Type: application/json" -d '{"text": "A futuristic cityscape at sunset."}'
```

**3. Suggest Movies:**
```bash
curl -X POST "http://127.0.0.1:8000/v1/suggest/Movies" -H "Content-Type: application/json" -d '{"context": "Sci-fi and action"}'
```

**4. Trade Crypto:**
```bash
curl -X POST "http://127.0.0.1:8000/v1/trade/Crypto" -H "Content-Type: application/json" -d '{"text": "Buy Bitcoin"}'
```

---

### 🛠 **Run the API Locally**

1. Install FastAPI and Uvicorn:
   ```bash
   pip install fastapi uvicorn
   ```

2. Run the API server:
   ```bash
   uvicorn core.main:app --reload
   ```

3. Access the API docs at:
   ```
   http://127.0.0.1:8000/docs
   ```

---

### 🧪 **Testing the API**

Install pytest:
```bash
pip install pytest
```

Create a test file `tests/test_api.py`:
```python
from fastapi.testclient import TestClient
from core.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

Run tests:
```bash
pytest
```

---

### 📋 **Next Steps**

- Add more endpoints following the same structure.
- Extend existing endpoints with more options and functionalities.
- Optimize for performance and security.

---

### 🛠 **Contributing**

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Create a Pull Request.

---

**Happy Coding!** 🚀
