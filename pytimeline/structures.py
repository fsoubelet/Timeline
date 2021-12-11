import json
import tkinter

from pathlib import Path
from tkinter import font
from typing import Dict, List, Tuple, Union

import pendulum
import svgwrite

from loguru import logger
from pendulum import DateTime, Duration
from svgwrite.container import Marker

from pytimeline.utils import assert_input_validity

# TODO: document accepted formats (https://pendulum.eustace.io/docs/#string-formatting)
DATE_FORMAT: str = "MMM DD, YYYY - HH:mmA"


class Colors:
    black = "#000000"
    gray = "#C0C0C0"


class Callout:
    width = 10
    height = 15
    increment = 10


class Timeline:
    def __init__(self, filename: Union[str, Path]) -> None:
        filename = Path(filename)
        logger.info(f"Loading timeline configuration from '{filename.absolute()}'")
        with filename.open("r") as f:
            self.data = json.load(f)
            assert_input_validity(self.data)

        # ----- Parameters ----- #
        self.markers: Dict[str, Tuple[Marker, Marker]] = {}
        self.text_fudge = (3, 1.5)
        self.width = self.data["width"]
        self.tick_format = self.data.get("tick_format", DATE_FORMAT)
        self.max_label_height = 0  # max height of all axis labels, used for final height computation

        # ----- Drawing ----- #
        logger.debug("Preparing SVG drawing object")
        self.drawing = svgwrite.Drawing()
        self.drawing["width"] = self.width
        self.g_axis = self.drawing.g()

        logger.debug("Parsing dates")
        self.start_date: DateTime = pendulum.parse(self.data["start"], strict=False)
        self.end_date: DateTime = pendulum.parse(self.data["end"], strict=False)
        padding: Duration = 0.1 * (self.end_date - self.start_date)
        self.date0: DateTime = self.start_date - padding
        self.date1: DateTime = self.end_date + padding
        self.total_seconds: int = (self.date1 - self.date0).in_seconds()

        # ----- Tkinter ----- #
        logger.debug("Initializing tkinter for fonts")
        self.tk_root = tkinter.Tk()
        self.fonts = {}

    def build(self):
        logger.info("Building timeline")
        y_era = 10  # draw era label and markers at this height

        self._create_main_axis()
        y_callouts = self._create_callouts()  # keep track of the callouts' heights
        y_axis = y_era + Callout.height - y_callouts  # axis position to avoid overlap with eras
        height = (
            y_axis + self.max_label_height + 4 * self.text_fudge[1]
        )  # height so that eras, callouts, axis & labels just fit
        self._create_eras(y_era, y_axis, height)
        self._create_era_axis_labels()
        self.g_axis.translate(0, y_axis)  # translate the axis group and add it to the drawing
        self.drawing.add(self.g_axis)
        self.drawing["height"] = height  # finally set the height on the drawing

    def save(self, filename: Union[str, Path]) -> None:
        logger.info(f"Saving timeline to disk at '{filename.absolute()}'")
        self.drawing.saveas(filename)

    def to_string(self) -> str:
        return self.drawing.tostring()

    def _create_eras(self, y_era, y_axis, height):
        if "eras" not in self.data:
            return

        logger.info("Drawing eras")
        markers = {}
        for era in self.data["eras"]:
            name = era[0]
            t0 = pendulum.parse(era[1], strict=False)
            t1 = pendulum.parse(era[2], strict=False)
            logger.debug(f"Creating era '{name}'")
            fill_color = era[3] if len(era) > 3 else Colors.gray

            start_marker, end_marker = self._get_markers(fill_color)

            logger.trace(f"Creating boundary lines")
            percent_width0 = (t0 - self.date0).in_seconds() / self.total_seconds
            percent_width1 = (t1 - self.date0).in_seconds() / self.total_seconds
            x0 = int(percent_width0 * self.width + 0.5)
            x1 = int(percent_width1 * self.width + 0.5)
            rectangle = self.drawing.add(self.drawing.rect((x0, 0), (x1 - x0, height)))
            rectangle.fill(fill_color, None, 0.15)

            line0 = self.drawing.add(
                self.drawing.line((x0, 0), (x0, y_axis), stroke=fill_color, stroke_width=0.5)
            )
            line1 = self.drawing.add(
                self.drawing.line((x1, 0), (x1, y_axis), stroke=fill_color, stroke_width=0.5)
            )
            line0.dasharray([5, 5])
            line1.dasharray([5, 5])

            logger.trace(f"Creating horizontal arrows and text")
            harrow = self.drawing.add(
                self.drawing.line((x0, y_era), (x1, y_era), stroke=fill_color, stroke_width=0.75)
            )
            harrow["marker-start"] = start_marker.get_funciri()
            harrow["marker-end"] = end_marker.get_funciri()
            self.drawing.add(
                self.drawing.text(
                    name,
                    insert=(0.5 * (x0 + x1), y_era - self.text_fudge[1]),
                    stroke="none",
                    fill=fill_color,
                    font_family="Helevetica",
                    font_size="6pt",
                    text_anchor="middle",
                )
            )

    def _get_markers(self, color: str) -> Tuple[Marker, Marker]:
        logger.trace(f"Getting markers for color '{color}'")
        if color in self.markers:
            return self.markers[color]

        start_marker: Marker = self.drawing.marker(insert=(0, 3), size=(10, 10), orient="auto")
        start_marker.add(self.drawing.path("M6,0 L6,7 L0,3 L6,0", fill=color))
        self.drawing.defs.add(start_marker)

        end_marker = self.drawing.marker(insert=(6, 3), size=(10, 10), orient="auto")
        end_marker.add(self.drawing.path("M0,0 L0,7 L6,3 L0,0", fill=color))
        self.drawing.defs.add(end_marker)

        self.markers[color] = (start_marker, end_marker)
        return start_marker, end_marker

    def _create_main_axis(self) -> None:
        logger.info("Drawing main axis line")
        self.g_axis.add(self.drawing.line((0, 0), (self.width, 0), stroke=Colors.black, stroke_width=3))

        logger.info("Adding tickmarks")
        self._add_axis_label(self.start_date, self.start_date.format(DATE_FORMAT), tick=True)
        self._add_axis_label(self.end_date, self.end_date.format(DATE_FORMAT), tick=True)

        if "num_ticks" in self.data:
            num_ticks = int(self.data["num_ticks"])
            logger.trace(f"Dividing period in {num_ticks} ticks")
            seconds = (self.end_date - self.start_date).in_seconds()
            for j in range(1, num_ticks):
                tickmark_date: DateTime = self.start_date.add(seconds=j * seconds / num_ticks)
                self._add_axis_label(tickmark_date, tickmark_date.format(DATE_FORMAT), tick=True)

    def _create_era_axis_labels(self) -> None:
        if "eras" not in self.data:
            return

        for era in self.data["eras"]:
            logger.trace(f"Creating axis labels for era '{era[0]}'")
            t0 = pendulum.parse(era[1], strict=False)
            t1 = pendulum.parse(era[2], strict=False)
            self._add_axis_label(t0, t0.format(DATE_FORMAT), tick=False, fill=Colors.black)
            self._add_axis_label(t1, t1.format(DATE_FORMAT), tick=False, fill=Colors.black)

    def _add_axis_label(self, dt: DateTime, label: str, **kwargs):
        logger.trace(f"Adding axis label '{label}'")
        percent_width: float = (dt - self.date0).in_seconds() / self.total_seconds
        if percent_width < 0 or percent_width > 1:
            return

        dy = 5
        x = int(percent_width * self.width + 0.5)

        add_tick = kwargs.get("tick", True)
        if add_tick:
            stroke = kwargs.get("stroke", Colors.black)
            self.g_axis.add(self.drawing.line((x, -dy), (x, dy), stroke=stroke, stroke_width=2))

        self.g_axis.add(
            self.drawing.text(
                label,
                insert=(x, -2 * dy),
                stroke="none",
                fill=kwargs.get("fill", Colors.gray),
                font_family="Helevetica",
                font_size="6pt",
                text_anchor="end",
                writing_mode="tb",
                transform=f"rotate(180, {x:d}, 0)",
            )
        )
        h = self._get_text_metrics("Helevetica", 6, label)[0] + 2 * dy
        self.max_label_height = max(self.max_label_height, h)

    def _create_callouts(self) -> float:
        if "callouts" not in self.data:
            return

        logger.info("Adding callouts")
        callouts_data: List[str] = self.data["callouts"]
        min_y = float("inf")
        sorted_dates: List[DateTime] = []
        inv_callouts: Dict[DateTime, Tuple[str, str]] = {}  # {date: (name, color)}

        for callout in callouts_data:
            event_name: str = callout[0]
            event_date: DateTime = pendulum.parse(callout[1], strict=False)
            event_color: str = callout[2] if len(callout) > 2 else Colors.black
            sorted_dates.append(event_date)
            if event_date not in inv_callouts:
                inv_callouts[event_date] = []
            inv_callouts[event_date].append((event_name, event_color))
        sorted_dates.sort()

        # Adding callouts one by one, making sure they don't overlap
        prev_x = [float("-inf")]
        prev_level = [-1]
        for event_date in sorted_dates:
            event_name, event_color = inv_callouts[event_date].pop()  # (str, str)
            percent_width: float = (event_date - self.date0).in_seconds() / self.total_seconds
            if percent_width < 0 or percent_width > 1:
                continue
            x = int(percent_width * self.width + 0.5)
            # figure out what 'level" to make the callout on
            k = 0
            i = len(prev_x) - 1
            left = x - (
                self._get_text_metrics("Helevetica", 6, event_name)[0] + Callout.width + self.text_fudge[0]
            )
            while left < prev_x[i] and i >= 0:
                k = max(k, prev_level[i] + 1)
                i -= 1
            y = 0 - Callout.height - k * Callout.increment
            min_y = min(min_y, y)
            # self.drawing.add(self.drawing.circle((left, y), stroke='red', stroke_width=2))
            path_data = f"M{x:d},0 L{x:d},{y:d} L{(x-Callout.width):d},{y:d}"
            self.g_axis.add(self.drawing.path(path_data, stroke=event_color, stroke_width=1, fill="none"))
            self.g_axis.add(
                self.drawing.text(
                    event_name,
                    insert=(
                        x - Callout.width - self.text_fudge[0],
                        y + self.text_fudge[1],
                    ),
                    stroke="none",
                    fill=event_color,
                    font_family="Helevetica",
                    font_size="6pt",
                    text_anchor="end",
                )
            )
            self._add_axis_label(event_date, event_date.format(DATE_FORMAT), tick=False, fill=Colors.black)
            self.g_axis.add(
                self.drawing.circle((x, 0), r=4, stroke=event_color, stroke_width=1, fill="white")
            )
            prev_x.append(x)
            prev_level.append(k)
        return min_y

    def _get_text_metrics(self, family: str, size: int, text: str) -> Tuple[int, int]:
        key = (family, size)
        if key in self.fonts:
            font = self.fonts[key]
        else:
            font = tkinter.font.Font(self.tk_root, family=family, size=size)
            self.fonts[key] = font
        assert font is not None
        w, h = (font.measure(text), font.metrics("linespace"))
        return w, h
