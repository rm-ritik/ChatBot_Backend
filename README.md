# Function calling coding challenge

## How to run the code.
1. Clone the repository:
```
  git clone https://github.com/rm-ritik/ChatBot_Backend.git
  cd ChatBot_Backend
```
2. Create a virtual environment
```
  python3 -m venv venv
  source venv/bin/activate
```

3. Install dependencies
``` pip install -r requirements.txt ```

4. Set up the environment variables:
  Create a ```.env``` file in the root directory.
  Add the following configuration variables to it:
  ```
    OPENAI_API_KEY="Your OpenAI API Key goes here"
    CAL_API_KEY="Your CAL API Key goes here"
    EVENT_TYPE_ID= #here the event type id corresponding to 60 minute events
  ```

5. Apply migrations
  ```python manage.py migrate```

6. Run the Deployment Server
  ```python manage.py runserver
