# Adaptivity via Planning techniques

Implementation a tool to compose Industrial API services via Planning techniques.

## Use the source code

We assume the user uses a **UNIX-like** machine and that has **Python 3.10** installed.

### Preliminaries

Clone [Fast Downward](https://github.com/aibasel/downward) planner respository and build it:
```sh
git clone https://github.com/aibasel/downward.git
cd downward
./build.py
```


### How to run the code

1. Define the descriptions of the manufacturing actors and run the Industrial APIs (see the instructions [here](../IndustrialAPI/README.md))

5. Set the goal and the contextual informations inside [context.py](context.py). N.B.: some knowledge of automated planning is required.

6. Start the controller:
```sh
python main.py
```
