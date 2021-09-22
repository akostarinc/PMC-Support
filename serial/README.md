## PMC - support utilities

 This folder contains the serial utility for reading the PMC serial port. The utility
is provided as-is; considering it is a prototype.

  The reason for this utility is to demonstrate the capabilities derived from listening
to the serial port of the PMC. It is meant to show you how to intercept / listen to the PMC's
internal data, and how to parse out different fields.

  This example may guide an integrator to implement their version of data polling. Naturally,
any programming language may be used to implement this function, we  simply picked
python for its efficiency.

   The utility is crafted in Python, running under Linux; however the toolkit used
is multi platform. (PyGTK/GObject) It can be ported to Windows / Mac with relative
ease. Please email Akostar if you would like to deploy it on different platforms.

### Screen shot of the utility

![Screen Shot](screen_serial.png)

  One can create accurate logs with an external device.  Also see -- extracting
information by polling the WiFi -- in our operations manual.

 EOF
