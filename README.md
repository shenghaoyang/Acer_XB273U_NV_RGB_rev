# Acer XB273U NV RGB LED controller reverse engineering

NOTE: This also appears to be the same protocol used by the X25 and XB323QK NV
monitors' RGB LED controllers, just with a different 

## Identifying the controller

Acer appears to have unique (VID, PID) combinations for all their
RGB lighting controllers. The XB273U NV's controller has the combination
(decimal):

VID    | PID
-------|--------
`0x42e`| `0xac0c`

## LED strip properties

- Number of LEDs: 90
- When facing the rear of the monitor, LED index zero corresponds to the LED
  at the left end of the strip.

## Communicating with the controller

The controller enumerates as a USB hid device. It appears to accept OUT reports
of different types - some trigger builtin effects while others allow direct
control of the RGB LEDs.

At the moment, only the direct control report's structure has been reverse
engineered (the author does not think anyonew would like to use the builtin
effects if they have direct software control. Plus, that would take up 
additional reversing time).

The direct control report has the following structure:

- Report type: `0x2a`
- Buffer length: `0x175`s

Offset (Byte) | Content | Description
--------------|---------|------------
0             | `0x0c`  | magic (command lsb?)
1             | `0x02`  | magic (command msb?)
2             | `0x00`  | magic (padding?)
3             | `90`    | Number of LEDs
4             | `0x0f`  | LED strip index
[5,   12]     | `0x00`  | magic (padding?)
[13,  372]    | not fixed | RGB data. up to 120 * (`R,G,B`) byte tuples in range `[0, 255]`.

### Other notes

The controller also seems to be capable of generating LED patterns by itself,
using a range of builtin effects. The reports associated with that
functionality have not been reverse engineered.

See `ctrl_hid_dump` for a raw dump of the HID descriptors.
See `ctrl_lsusb` for lsusb output.
`raw_test.py` is a simple unoptimized script that demonstrates report 
generation.
