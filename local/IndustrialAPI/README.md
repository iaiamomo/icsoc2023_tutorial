# Industrial APIs

This tool aims at representing industrial actors (e.g., devices, machines, humans) as **Industrial APIs**. Additionally

Follow the following **template** to generate the actors descriptions. The template represents a human designer. The different aspects of the actor are represented as attributes and features. <em>Features</em> represent a state with properties (e.g., <code>status</code>), while <em>attributes</em> (e.g., <code>type</code>, <code>actions</code>, <code>transitions</code>) represent functionalities and values that do not change or that change less frequently than the <em>features</em> property values.
```json
{
  "id": "designerusa",
  "attributes": {
      "type": "Service",
      "_comment": "static properties"
  },
  "features": {
      "_comment": "dynamic properties"
  }
}
```

## How to launch the Industrial API
1. Run the server that represents a middleware exposing HTTP server and a websocket server:
```sh
python app.py
```

3. Run the services (which communicate with the server through websocket):
```sh
python launch_devices.py
```

