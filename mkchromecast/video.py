# This file is part of mkchromecast.

"""
Google Cast device has to point out to http://ip:5000/stream
"""

import getpass
import os
import pickle
import subprocess

import mkchromecast
from mkchromecast import colors
from mkchromecast import pipeline_builder
from mkchromecast import stream_infra
from mkchromecast import utils
from mkchromecast.constants import OpMode

def _flask_init() -> None:
    mkcc = mkchromecast.Mkchromecast()

    # TODO(xsdg): Passing args in one-by-one to facilitate refactoring
    # the Mkchromecast object so that it has argument groups instead of just a
    # giant set of uncoordinated and conflicting arguments.
    encode_settings = pipeline_builder.VideoSettings(
        display=mkcc.display,
        fps=mkcc.fps,
        input_file=mkcc.input_file,
        loop=mkcc.loop,
        operation=mkcc.operation,
        resolution=mkcc.resolution,
        screencast=mkcc.screencast,
        seek=mkcc.seek,
        subtitles=mkcc.subtitles,
        user_command=mkcc.command,
        vcodec=mkcc.vcodec,
        youtube_url=mkcc.youtube_url,
    )
    builder = pipeline_builder.Video(encode_settings)
    if mkcc.debug is True:
        print(f":::ffmpeg::: pipeline_builder command: {builder.command}")

    media_type = mkcc.mtype or "video/mp4"
    # Convert command to list[str] if needed
    cmd = builder.command
    if isinstance(cmd, str):
        cmd_list: list[str] = [cmd]
    elif hasattr(cmd, '__fspath__'):
        cmd_list = [str(cmd)]
    else:
        cmd_list = list(cmd)
    
    stream_infra.FlaskServer.init_video(
        chunk_size=mkcc.chunk_size,
        command=cmd_list,
        media_type=media_type
    )


def main() -> None:
    mkcc = mkchromecast.Mkchromecast()
    ip = utils.get_effective_ip(
        mkcc.platform, host_override=mkcc.host, fallback_ip="0.0.0.0")

    if mkcc.backend != "node":
        pipeline = stream_infra.PipelineProcess(_flask_init, ip, mkcc.port, mkcc.platform)
        pipeline.start()
    else:
        print("Starting Node")

        # TODO(xsdg): This implies that the `node` backend is only compatible
        # with INPUT_FILE OpMode, for video.  Double-check what's happening here
        # and then implement that constraint directly in the Mkchromecast class.
        if mkcc.operation != OpMode.INPUT_FILE:
            print(colors.warning(
                "The node video backend requires and only supports the input "
                "file operation (-i argument)."))
            utils.terminate()

        if mkcc.platform == "Darwin":
            PATH = (
                "./bin:./nodejs/bin:/Users/"
                + str(getpass.getuser())
                + "/bin:/usr/local/bin:/usr/local/sbin:"
                + "/usr/bin:/bin:/usr/sbin:"
                + "/sbin:/opt/X11/bin:/usr/X11/bin:/usr/games:"
                + os.environ["PATH"]
            )
        else:
            PATH = os.environ["PATH"]

        if mkcc.debug is True:
            print("PATH = %s." % PATH)

        node_names = ["node"]
        nodejs_dir = ["./nodejs/"]

        # TODO(xsdg): This is not necessarily where mkchromecast is installed,
        # and may point to an unrelated mkchromecast install.
        if mkcc.platform == "Linux":
            node_names.append("nodejs")
            nodejs_dir.append("/usr/share/mkchromecast/nodejs/")

        webcast: list[str] = []
        for name in node_names:
            if utils.is_installed(name, PATH, mkcc.debug):
                for nodejs_path in nodejs_dir:
                    if os.path.isdir(nodejs_path):
                        script_path = nodejs_path + "html5-video-streamer.js"
                        if mkcc.input_file:
                            webcast = [name, script_path, mkcc.input_file]
                        break
                if webcast:
                    break

        if not webcast:
            print(
                colors.warning(
                    "Nodejs is not installed in your system. "
                    "Please, install it to use this backend."
                )
            )
            print(colors.warning("Closing the application..."))
            utils.terminate()
            return

        try:
            subprocess.Popen(webcast)
        except Exception as e:
            print(colors.warning(f"Failed to start node: {e}"))
            print(colors.warning("Closing the application..."))
            utils.terminate()
