# Ground Software

Under construction!

This is the Ground Station Software for Caelus Rocketry.

# Running

**Detailed instructions coming soon**

Prerequisites:
- Docker 
- Python

1. Install the necessary packages for this application

```
pip install -U django channels["daphne"] channels_redis 
```

2. Run Redis server on Docker 

3. Run the Django server using `py manage.py runserver`

4. In another process, run the FS Bridge worker using `py manage.py runworker flight-software`

5. Go to `localhost:8000`