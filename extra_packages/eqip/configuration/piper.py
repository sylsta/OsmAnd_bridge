import logging
import os
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

# from warg import is_windows # avoid dependency import not standard python pkgs.
CUR_OS = sys.platform
IS_WIN = any(CUR_OS.startswith(i) for i in ["win32", "cygwin"])
IS_MAC = CUR_OS.startswith("darwin")

logger = logging.getLogger(__name__)

def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b""):  # b'\n'-separated lines
        logger.info("got line from subprocess: %r", line)


def catching_callable(*args, **kwargs):
    try:
        logger.info(f"{list(args)}, {list(kwargs.items())}")

        # subprocess.check_call(*args, **kwargs)
        # output = subprocess.check_output(*args, **kwargs)
        # subprocess.run(*args,**kwargs)

        from subprocess import PIPE, STDOUT, Popen

        process = Popen(*args, **kwargs, stdout=PIPE, stderr=STDOUT)
        with process.stdout:
            log_subprocess_output(process.stdout)
        exitcode = process.wait()  # 0 means success
        if exitcode:
            logger.info("Success")

    except subprocess.CalledProcessError as e:
        output = (e.stderr, e.stdout, e)
        logger.warning(output)



SP_CALLABLE = catching_callable  # subprocess.call
DEFAULT_PIP_INDEX = os.environ.get("PIP_INDEX_URL", "https://pypi.org/pypi/")

class UpgradeStrategyEnum(Enum):
    """
    eager - all packages will be upgraded to the latest possible version.
    It should be noted here that pip’s current
    resolution algorithm isn’t even aware of packages other than those specified on the command line, and those
    identified as dependencies.
    This may or may not be true of the new resolver.

    only-if-needed - packages are only upgraded if they are named in the pip command or a requirement file (i.e.
    they are direct requirements), or an upgraded parent needs a later version of the dependency than is currently
    installed.

    to-satisfy-only (undocumented, please avoid) - packages are not upgraded (not even direct requirements) unless the
    currently installed version fails to satisfy a requirement (either explicitly specified or a dependency).

    This is actually the “default” upgrade strategy when --upgrade is not set, i.e. pip install AlreadyInstalled and pip
    install --upgrade --upgrade-strategy=to-satisfy-only AlreadyInstalled yield the same behaviour.
    """

    eager = "eager"
    to_satisfy_only = "to-satisfy-only"
    only_if_needed = "only-if-needed"


def get_qgis_python_interpreter_path() -> Optional[Path]:
    """

    :return: The path of the qgis python interpreter
    :rtype: Optional[Path]
    """
    interpreter_path = Path(sys.executable)
    if IS_WIN:  # For OSGeo4W
        try_path = interpreter_path.parent / "python.exe"
        if not try_path.exists():
            try_path = interpreter_path.parent / "python3.exe"
            if not try_path.exists():
                logger.error(f"Could not find python {try_path}")
                return None
        return try_path

    elif IS_MAC:  # /Applications/QGIS.app/Contents/MacOS/bin/python3
        try_path = interpreter_path.parent / "bin" / "python"
        if not try_path.exists():
            try_path = interpreter_path.parent / "bin" / "python3"
            if not try_path.exists():
                logger.error(f"Could not find python {try_path}")
                return None
        return try_path

    # QString QStandardPaths::findExecutable(const QString &executableName, const QStringList &paths = QStringList())

    return interpreter_path


def install_requirements_from_file(
    requirements_path: Path,
    upgrade: Optional[bool] = None,
    upgrade_strategy: UpgradeStrategyEnum = UpgradeStrategyEnum.only_if_needed,
) -> None:
    """
    Install requirements from a requirements.txt file.

    :param upgrade:
    :param upgrade_strategy:
    :param requirements_path: Path to requirements.txt file.
    :rtype: None
    """
    if not isinstance(requirements_path, Path):
        requirements_path = Path(requirements_path)

    requirements_file_parent_directory = str(requirements_path.parent.as_posix())

    # if False:
    #     if "\\" in requirements_file_parent_directory:
    #         print("found \\ in requirements")
    #         requirements_file_parent_directory = (
    #             requirements_file_parent_directory.replace("\\", "/")
    #         )

    os.environ["REQUIREMENTS_FILE_PARENT_DIRECTORY"] = (
        requirements_file_parent_directory
    )

    # if upgrade is None:
    #     try:
    #         from jord.qt_utilities import check_state_to_bool
    #
    #         upgrade = check_state_to_bool(
    #             read_project_setting(
    #                 "AUTO_UPGRADE",
    #                 defaults=DEFAULT_PROJECT_SETTINGS,
    #                 project_name=PROJECT_NAME,
    #             )
    #         )
    #     except Exception as e:
    #         if VERBOSE:
    #             logger.info(f"{e}")

    req_path_str = str(requirements_path)

    args = ["install", "-r", req_path_str]

    if True:  # No progress bar
        args += ["--progress-bar", "off"]

    if True:
        args += ["--user"]

    if upgrade:
        args += ["--upgrade"]

    if True:
        args += ["--ignore-installed"]

    # if False:
    #     args += ["--force-reinstall"]

    if upgrade_strategy:
        args += ["--upgrade-strategy", upgrade_strategy.value]

    IGNORE = """
  other options:

  --index-url
--extra-index-url
--no-index
--find-links

  --force-reinstall
  --ignore-installed
  --no-deps
  --ignore-requires-python
  --require-hashes
  --editable
  --pre # Prereleases
  """

    # if False:
    #     import pip
    #
    #     pip.main(args)
    #
    # elif False:
    #     SP_CALLABLE(["pip"] + args)
    #
    # elif True:
    install_pip_if_not_present()

    cmd = [str(get_qgis_python_interpreter_path()), "-m", "pip", *args]

    logger.info(f"Executing {cmd=}")

    if is_pip_installed():
        SP_CALLABLE(cmd)

    else:
        logger.info("PIP IS STILL MISSING!")

def install_pip_if_not_present(always_upgrade: bool = True):
    if not is_pip_installed() or always_upgrade:
        logger.info(
            f"Bootstrapping pip because {is_pip_installed()=} or {always_upgrade=}"
        )


        SP_CALLABLE(
            [
                str(get_qgis_python_interpreter_path()),
                "-m",
                "ensurepip",
                "--upgrade",
            ]
        )

def is_pip_installed():
    pip_present = True
    try:
        import pip
    except ImportError:
        pip_present = False

    logger.info(f"{pip_present=}")

    return pip_present

