# Architecture

The Ground Station is composed of different technologies all working together in a cohesive manner. This document attempts to outline these technologies.

## Project Structure

- `groundstation/`
  - `dashboard/`
    - `consumers.py` - contains the WebSocket that the frontend connects to
    - `models.py` - contains Packet models for storing tests in the database
    - `urls.py` - contains url mappings for dashboard routes
    - `views.py` - contains route callbacks
  - `data/`
    - `bridge.py` - manager for flight software (FS) controllers; initializes controllers and starts threads
    - `controllers.py` - contains the FS controllers; connects & listens to their respective communication interfaces
    - `packet.py` - parses and unpacks packets sent by the flight software
  - `static/`
    - `css/` - css-related files 
    - `img/` - logos, P&IDs
    - `js/` - JavaScript frontend files
  - `asgi.py` - creates ASGI app; initializes WebSockets with Channels
  - `settings.py` - Django related settings
  - `example_config.json/config.json` - Ground Station related settings
  - `urls.py` - contains url mappings for entire project

## Technologies 

### Django

[Django](https://www.djangoproject.com/) is the web framework for the Ground Station. As Python is an easy language to learn and Django comes with a plethora of features to assist in development, this allows us to develop quickly and help other developers to learn the software quicker.

### Daphne

[Daphne](https://github.com/django/daphne) is the ASGI server to support Django Channels WebSockets. This allows us to serve a WebSocket that acts as a bridge between the flight software and the site. 

### XBee Python Library

[XBee Python Library](https://xbplib.readthedocs.io/en/latest/), also known as `xbplib` and `digi-xbee`, is the library we use to connect to the XBee devices. The library acts as a wrapper over the low-level `pyserial` library and lets us easily interact with the XBee network in API mode.

### Whitenoise

[Whitenoise](https://whitenoise.readthedocs.io/en/stable/index.html) is a middleware that lets us compress and cache static files in a Django production environment.