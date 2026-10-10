# Pursuit Backend

Backend for the Pursuit application.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```

3. Copy `.env.example` to `.env` and fill in the details.

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```
