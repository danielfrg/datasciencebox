from __future__ import absolute_import, division, print_function

import sys
import logging
import logging.handlers

# Hide messages if we log before setting up handler
logging.root.manager.emittedNoHandlerWarning = True

logging.getLogger("paramiko").setLevel(logging.WARNING)


def getLogger():
    return logging.getLogger("datasciencebox")


def setup_logging(log_level=logging.WARNING):
    logger = logging.getLogger("datasciencebox")
    logger.setLevel(log_level)
    logger.propagate = False

    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)

    add_handler = True
    for handle in logger.handlers:
        if getattr(handle, "stream", None) == sys.stdout:
            add_handler = False
            break
    if add_handler:
        logger.addHandler(console_handler)
