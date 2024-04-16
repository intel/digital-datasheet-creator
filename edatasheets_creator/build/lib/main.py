
"""
    main.py
    -------
    This is the main module of the program
"""

# main.py

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from edatasheets_creator.core import DatasheetCreatorApp
from edatasheets_creator.functions import t

"""
    Main application start
"""

# for frame in inspect.stack():
#     print(frame[1])

app = DatasheetCreatorApp(sys.argv[1:])

print(t("Starting Application"))

# Run application
app.run()
