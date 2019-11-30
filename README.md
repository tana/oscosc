# oscosc: OSC oscilloscope
oscosc is an oscilloscope for software.
In other words, oscosc plots numerical data via [Open Sound Control](http://opensoundcontrol.org/).

## Features
- Real-time plotting of multiple numerical values
- Uses Open Sound Control (OSC) for communication
  - Network transparency: Data can be sent from local or remote machine.
  - Multi-platform: Any languages and platforms (with OSC library) can send data.
  - Lightweight: Because a sender needs no graphics rendering, oscosc is suitable for embedded or real-time programs.

## Requirements
- Python (3.6 or later)
- Required python libraries
  - [python-osc](https://github.com/attwad/python-osc)
  - [pyglet](http://pyglet.org/)
  - [PyOpenGL](http://pyopengl.sourceforge.net/)
  - [pyimgui](https://github.com/swistakm/pyimgui)

## Usage
```
python oscosc.py [-p PORT]
```
It receives OSC messages at UDP port specified by the option `-p` (port 12345 when omitted).

The OSC messages must have one floating-point argument (e.g. `/x 1.0`).
If messages are packed into bundles, timestamps of bundles are used.
Otherwise, current time of the local machine is used.

## TODO
- [ ] Sweep mode (more similar to real oscilloscopes)
- [ ] Serial port based communication
