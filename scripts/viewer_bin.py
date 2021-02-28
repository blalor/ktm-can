# Copyright (C) 2018 Kristian Sloth Lauszus.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Contact information
# -------------------
# Kristian Sloth Lauszus
# Web      :  http://www.lauszus.com
# e-mail   :  lauszus@gmail.com

## derived from 👆. shows each byte as individual bits, making it easier to see
## changes when doing live discovery.

import argparse
import logging
import sys
import time
from collections import OrderedDict

import can
from can import __version__

logger = logging.getLogger("can.serial")

try:
    import curses
    from curses.ascii import ESC as KEY_ESC, SP as KEY_SPACE
except ImportError:
    # Probably on windows
    logger.warning(
        "You won't be able to use the viewer program without " "curses installed!"
    )
    curses = None  # type: ignore


class CanViewer:
    def __init__(self, stdscr, bus, testing=False):
        self.stdscr = stdscr
        self.bus = bus

        # Initialise the ID dictionary, start timestamp, scroll and variable for pausing the viewer
        self.ids = {}
        self.start_time = None
        self.scroll = 0
        self.paused = False

        self.COL_WIDTHS = OrderedDict()
        self.COL_WIDTHS["ID"]    = 12
        for x in range(0, 8):
            self.COL_WIDTHS[f"D{x:d}"] = 9

        # Get the window dimensions - used for resizing the window
        self.y, self.x = self.stdscr.getmaxyx()

        # Do not wait for key inputs, disable the cursor and choose the background color automatically
        self.stdscr.nodelay(True)
        curses.curs_set(0)
        curses.use_default_colors()

        # Used to color error frames red
        curses.init_pair(1, curses.COLOR_RED, -1)

        if not testing:  # pragma: no cover
            self.run()

    def run(self):
        # Clear the terminal and draw the header
        self.draw_header()

        while 1:
            # Do not read the CAN-Bus when in paused mode
            if not self.paused:
                # Read the CAN-Bus and draw it in the terminal window
                msg = self.bus.recv(timeout=1.0 / 1000.0)
                if msg is not None:
                    self.draw_can_bus_message(msg)
            else:
                # Sleep 1 ms, so the application does not use 100 % of the CPU resources
                time.sleep(1.0 / 1000.0)

            # Read the terminal input
            key = self.stdscr.getch()

            # Stop program if the user presses ESC or 'q'
            if key == KEY_ESC or key == ord("q"):
                break

            # Clear by pressing 'c'
            elif key == ord("c"):
                self.ids = {}
                self.start_time = None
                self.scroll = 0
                self.draw_header()

            # Sort by pressing 's'
            elif key == ord("s"):
                # Sort frames based on the CAN-Bus ID
                self.draw_header()
                for i, key in enumerate(sorted(self.ids.keys())):
                    # Set the new row index, but skip the header
                    self.ids[key]["row"] = i + 1

                    # Do a recursive call, so the frames are repositioned
                    self.draw_can_bus_message(self.ids[key]["msg"], sorting=True)

            # Pause by pressing space
            elif key == KEY_SPACE:
                self.paused = not self.paused

            # Scroll by pressing up/down
            elif key == curses.KEY_UP:
                # Limit scrolling, so the user do not scroll passed the header
                if self.scroll > 0:
                    self.scroll -= 1
                    self.redraw_screen()
            elif key == curses.KEY_DOWN:
                # Limit scrolling, so the maximum scrolling position is one below the last line
                if self.scroll <= len(self.ids) - self.y + 1:
                    self.scroll += 1
                    self.redraw_screen()

            # Check if screen was resized
            resized = curses.is_term_resized(self.y, self.x)
            if resized is True:
                self.y, self.x = self.stdscr.getmaxyx()
                if hasattr(curses, "resizeterm"):  # pragma: no cover
                    curses.resizeterm(self.y, self.x)
                self.redraw_screen()

        # Shutdown the CAN-Bus interface
        self.bus.shutdown()

    def draw_can_bus_message(self, msg, sorting=False):
        # Use the CAN-Bus ID as the key in the dict
        key = msg.arbitration_id

        # Sort the extended IDs at the bottom by setting the 32-bit high
        if msg.is_extended_id:
            key |= 1 << 32

        new_id_added, length_changed = False, False
        if not sorting:
            # Check if it is a new message or if the length is not the same
            if key not in self.ids:
                new_id_added = True
                # Set the start time when the first message has been received
                if not self.start_time:
                    self.start_time = msg.timestamp

            elif msg.dlc != self.ids[key]["msg"].dlc:
                length_changed = True

            if new_id_added or length_changed:
                # Increment the index if it was just added, but keep it if the length just changed
                row = len(self.ids) + 1 if new_id_added else self.ids[key]["row"]

                # It's a new message ID or the length has changed, so add it to
                # the dict
                # The first index is the row index, the second is a copy of the
                # CAN-Bus frame
                self.ids[key] = {"row": row, "msg": msg}
            else:
                # Copy the CAN-Bus frame - this is used for sorting
                self.ids[key]["msg"] = msg

        # Format the CAN-Bus ID as a hex value
        arbitration_id_string = "0x{0:0{1}X}".format(
            msg.arbitration_id, 8 if msg.is_extended_id else 3
        )

        # Use red for error frames
        if msg.is_error_frame:
            color = curses.color_pair(1)
        else:
            color = curses.color_pair(0)

        # Now draw the CAN-Bus message on the terminal window
        row_ind = self.ids[key]["row"]
        cols = OrderedDict()
        cols["ID"] = arbitration_id_string

        for i, b in enumerate(msg.data):
            hdr = f"D{i}"
            cols[hdr] = "{:08b}".format(b)

        col_ind = 0
        for hdr, col_val in cols.items():
            self.draw_line(row_ind, col_ind, col_val, color)
            col_ind += self.COL_WIDTHS[hdr]

        return self.ids[key]

    def draw_line(self, row, col, txt, *args):
        if row - self.scroll < 0:
            # Skip if we have scrolled passed the line
            return
        try:
            self.stdscr.addstr(row - self.scroll, col, txt, *args)
        except curses.error:
            # Ignore if we are trying to write outside the window
            # This happens if the terminal window is too small
            pass

    def draw_header(self):
        self.stdscr.erase()

        col_ind = 0
        for hdr, wd in self.COL_WIDTHS.items():
            self.draw_line(0, col_ind, hdr, curses.A_BOLD)
            col_ind += wd

    def redraw_screen(self):
        # Trigger a complete redraw
        self.draw_header()
        for key in self.ids:
            self.draw_can_bus_message(self.ids[key]["msg"])


# noinspection PyProtectedMember
class SmartFormatter(argparse.HelpFormatter):
    def _get_default_metavar_for_optional(self, action):
        return action.dest.upper()

    def _format_usage(self, usage, actions, groups, prefix):
        # Use uppercase for "Usage:" text
        return super()._format_usage(usage, actions, groups, "Usage: ")

    def _format_args(self, action, default_metavar):
        if action.nargs != argparse.REMAINDER and action.nargs != argparse.ONE_OR_MORE:
            return super()._format_args(action, default_metavar)

        # Use the metavar if "REMAINDER" or "ONE_OR_MORE" is set
        get_metavar = self._metavar_formatter(action, default_metavar)
        return "%s" % get_metavar(1)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)

        # Modified so "-s ARGS, --long ARGS" is replaced with "-s, --long ARGS"
        else:
            parts = []
            default = self._get_default_metavar_for_optional(action)
            args_string = self._format_args(action, default)
            for i, option_string in enumerate(action.option_strings):
                if i == len(action.option_strings) - 1:
                    parts.append("%s %s" % (option_string, args_string))
                else:
                    parts.append("%s" % option_string)
            return ", ".join(parts)

    def _split_lines(self, text, width):
        # Allow to manually split the lines
        if text.startswith("R|"):
            return text[2:].splitlines()
        return super()._split_lines(text, width)

    def _fill_text(self, text, width, indent):
        if text.startswith("R|"):
            # noinspection PyTypeChecker
            return "".join(indent + line + "\n" for line in text[2:].splitlines())
        else:
            return super()._fill_text(text, width, indent)


def parse_args(args):
    # Python versions >= 3.5
    kwargs = {}
    if sys.version_info[0] * 10 + sys.version_info[1] >= 35:  # pragma: no cover
        kwargs = {"allow_abbrev": False}

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        "python -m can.viewer",
        description="A simple CAN viewer terminal application written in Python",
        epilog="R|Shortcuts: "
        "\n        +---------+-------------------------+"
        "\n        |   Key   |       Description       |"
        "\n        +---------+-------------------------+"
        "\n        | ESQ/q   | Exit the viewer         |"
        "\n        | c       | Clear the stored frames |"
        "\n        | s       | Sort the stored frames  |"
        "\n        | SPACE   | Pause the viewer        |"
        "\n        | UP/DOWN | Scroll the viewer       |"
        "\n        +---------+-------------------------+",
        formatter_class=SmartFormatter,
        add_help=False,
        **kwargs
    )

    optional = parser.add_argument_group("Optional arguments")

    optional.add_argument(
        "-h", "--help", action="help", help="Show this help message and exit"
    )

    optional.add_argument(
        "--version",
        action="version",
        help="Show program's version number and exit",
        version="%(prog)s (version {version})".format(version=__version__),
    )

    # Copied from: https://github.com/hardbyte/python-can/blob/develop/can/logger.py
    optional.add_argument(
        "-b",
        "--bitrate",
        type=int,
        help="""Bitrate to use for the given CAN interface""",
    )

    optional.add_argument("--fd", help="Activate CAN-FD support", action="store_true")

    optional.add_argument(
        "--data_bitrate",
        type=int,
        help="""Bitrate to use for the data phase in case of CAN-FD.""",
    )

    optional.add_argument(
        "-c",
        "--channel",
        help="""Most backend interfaces require some sort of channel.
                          For example with the serial interface the channel might be a rfcomm device: "/dev/rfcomm0"
                          with the socketcan interfaces valid channel examples include: "can0", "vcan0".
                          (default: use default for the specified interface)""",
    )

    optional.add_argument(
        "-f",
        "--filter",
        help="R|Space separated CAN filters for the given CAN interface:"
        "\n      <can_id>:<can_mask> (matches when <received_can_id> & mask == can_id & mask)"
        "\n      <can_id>~<can_mask> (matches when <received_can_id> & mask != can_id & mask)"
        "\nFx to show only frames with ID 0x100 to 0x103 and 0x200 to 0x20F:"
        "\n      python -m can.viewer -f 100:7FC 200:7F0"
        "\nNote that the ID and mask are alway interpreted as hex values",
        metavar="{<can_id>:<can_mask>,<can_id>~<can_mask>}",
        nargs=argparse.ONE_OR_MORE,
        default="",
    )

    optional.add_argument(
        "-i",
        "--interface",
        dest="interface",
        help="R|Specify the backend CAN interface to use.",
        choices=sorted(can.VALID_INTERFACES),
    )

    # Print help message when no arguments are given
    if not args:
        parser.print_help(sys.stderr)
        import errno

        raise SystemExit(errno.EINVAL)

    parsed_args = parser.parse_args(args)

    can_filters = []
    if parsed_args.filter:
        # print('Adding filter/s', parsed_args.filter)
        for flt in parsed_args.filter:
            # print(filter)
            if ":" in flt:
                _ = flt.split(":")
                can_id, can_mask = int(_[0], base=16), int(_[1], base=16)
            elif "~" in flt:
                can_id, can_mask = flt.split("~")
                can_id = int(can_id, base=16) | 0x20000000  # CAN_INV_FILTER
                can_mask = int(can_mask, base=16) & 0x20000000  # socket.CAN_ERR_FLAG
            else:
                raise argparse.ArgumentError(None, "Invalid filter argument")
            can_filters.append({"can_id": can_id, "can_mask": can_mask})

    return parsed_args, can_filters


def main():  # pragma: no cover
    parsed_args, can_filters = parse_args(sys.argv[1:])

    config = {"single_handle": True}
    if can_filters:
        config["can_filters"] = can_filters
    if parsed_args.interface:
        config["interface"] = parsed_args.interface
    if parsed_args.bitrate:
        config["bitrate"] = parsed_args.bitrate
    if parsed_args.fd:
        config["fd"] = True
    if parsed_args.data_bitrate:
        config["data_bitrate"] = parsed_args.data_bitrate

    # Create a CAN-Bus interface
    bus = can.Bus(parsed_args.channel, **config)
    # print('Connected to {}: {}'.format(bus.__class__.__name__, bus.channel_info))

    curses.wrapper(CanViewer, bus)


if __name__ == "__main__":
    # Catch ctrl+c
    try:
        main()
    except KeyboardInterrupt:
        pass
