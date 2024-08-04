# Setup

1. First, you will need to install:
- [python](https://www.python.org/downloads)
- [git](https://git-scm.com/downloads)

2. Now, clone this repository onto your computer by running
```shell
git clone https://github.com/CaelusRocketry/gs2
```

3. `cd` into the new directory and create a virtual environment (venv) by running 
```shell
python -m venv venv
# activate venv
venv/Scripts/activate
```

4. Once you are in your virtualenv, install all dependencies by running
```shell
pip install -r requirements.txt
```

5. `cd` into the `groundstation/` directory and rename `example_config.json` to `config.json`. This file will serve as the configuration for the **Ground Station**. To edit Django related settings, refer to `settings.py`.
 
6. In `config.json`, determine your flight software environment (`"xbee" | "sim"`) and configure the corresponding telemetry settings. Refer to [CONFIG.md](/docs/CONFIG.md) for a more detailed explanation of the configuration.

7. **Django:** `cd` out of the groundstation folder and run `python manage.py migrate` to initialize your database. In `groundstation/settings.py`, if you don't want to use `whitenoise`, edit the `DEBUG` variable to equal `True`.
    - **Note:** `DEBUG=True` will have a performance impact on the application. To use `whitenoise`, run `python manage.py collectstatic`. 
 
8. Assuming the flight software is fully functional and running, start up the Ground Station server by running
```shell
daphne groundstation.asgi:application
```  
> If you don't want to use Daphne's production server, you can always use Django's local development server by running
> ```shell
> python manage.py runserver
> ```

Head over to https://127.0.0.1:8000 and you should be all set!