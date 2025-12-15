# This file is part of mkchromecast.

import subprocess
import re
from typing import Optional

_sink_num: Optional[list[int]] = None


def create_sink() -> None:
    """Create a PulseAudio null sink for Mkchromecast."""
    global _sink_num

    sink_name = "Mkchromecast"

    create_sink_cmd = [
        "pactl",
        "load-module",
        "module-null-sink",
        "sink_name=" + sink_name,
        "sink_properties=device.description=" + sink_name,
    ]

    cs = subprocess.Popen(create_sink_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    csoutput, cserror = cs.communicate()
    
    # Parse the module number from output
    if csoutput:
        try:
            module_num = int(csoutput.decode("utf-8").strip())
            _sink_num = [module_num]
        except (ValueError, UnicodeDecodeError):
            _sink_num = None


def remove_sink() -> None:
    """Remove all Mkchromecast PulseAudio sinks."""
    global _sink_num

    if _sink_num is None:
        return

    for num in _sink_num:
        remove_sink_cmd = [
            "pactl",
            "unload-module",
            str(num),
        ]
        subprocess.run(
            remove_sink_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=True,
        )


def check_sink() -> Optional[bool]:
    """Check if Mkchromecast sink exists.
    
    Returns:
        True if sink exists, False if not, None if pactl not found.
    """
    try:
        check_sink_cmd = ["pactl", "list", "sinks"]
        chk = subprocess.Popen(
            check_sink_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        chkoutput, chkerror = chk.communicate()
    except FileNotFoundError:
        return None

    output_str = chkoutput.decode("utf-8") if chkoutput else ""
    return "Mkchromecast" in output_str


def get_sink_list() -> None:
    """Get a list of sinks with a name prefix of Mkchromecast and save to _sink_num.

    Used to clear any residual sinks from previous failed actions. The number
    saved to _sink_num is the module index, which can be passed to pactl.
    """
    global _sink_num

    cmd = ["pactl", "list", "sinks"]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, check=True
    )

    pattern = re.compile(
        r"^Sink\s*#\d+\s*$(?:\n^.*?$)*?\n\s*?Name:\s*?Mkchromecast.*"
        + r"\s*?$(?:\n^.*?$)*?\n^\s*?Owner Module: (?P<module>\d+?)\s*?$",
        re.MULTILINE,
    )
    output_str = result.stdout.decode("utf-8") if result.stdout else ""
    matches = pattern.findall(output_str, re.MULTILINE)

    _sink_num = [int(i) for i in matches]
