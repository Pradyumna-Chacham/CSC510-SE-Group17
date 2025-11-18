## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Shorse321/CSC510Group24.git
cd CSC510Group24/proj2/stackshack
```

### 2. Set Up Virtual Environment

**Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

**Open MySQL Workbench or command line and run:**
```sql
CREATE DATABASE stackshack;
USE stackshack;
```

The tables will be created automatically when you first run the app.

### 5. Configure Environment Variables

Create a `.env` file in the project root:
```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your MySQL credentials:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# MySQL Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=stackshack
```

**Important:** Replace `your_mysql_password` with your actual MySQL password!

### 6. Initialize the Database (if the tables haven't been automatically created)
```bash
python create_tables.py
```

### 7. Create Admin User
```bash
python create_admin.py
```

This creates an admin account with:
- **Username:** `admin`
- **Password:** `admin`

**Change this password after first login in production!**

### 8. Seed Sample Menu Data
```bash
python seed_menu.py
```

This adds sample burger menu ingredients to test the system.

---

## Running the Application

### Start the Server
```bash
python app.py
```
or 
```bash
export FLASK_APP
flask run
```

You should see:
```bash
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### Access the Application

Open your browser and go to:
```bash
http://localhost:5000
```
or bash
```
http://127.0.0.1:5000
```
---

### Test Database Connection
```bash
python test_conn.py
```

Should output: `Connected to MySQL successfully!`

---

## Running the Test Suite

To verify that all components are working correctly, you can run the project's built-in test suite.

1.  Make sure you are in the `proj2/` directory.
2.  Install `pytest` (if not already in `requirements.txt`):
    ```bash
    pip install pytest
    ```
3.  Run the tests using the following command (this sets the correct path for imports):
    ```bash
    PYTHONPATH=./stackshack python -m pytest stackshack/tests
    ```
    or run the below command to get the test case suite results in a html file:
    ```
    python -m pytest stackshack/tests/ --html=test-results.html --self-contained-html
    ```
