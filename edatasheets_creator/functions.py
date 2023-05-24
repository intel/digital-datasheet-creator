# ********************** COPYRIGHT INTEL CORPORATION ***********************
#
# THE SOFTWARE CONTAINED IN THIS FILE IS CONFIDENTIAL AND PROPRIETARY
# TO INTEL CORPORATION. THIS PRINTOUT MAY NOT BE PHOTOCOPIED,
# REPRODUCED, OR USED IN ANY MANNER WITHOUT THE EXPRESSED WRITTEN
# CONSENT OF INTEL CORPORATION. ALL LOCAL, STATE, AND FEDERAL
# LAWS RELATING TO COPYRIGHTED MATERIAL APPLY.
#
# Copyright (c), Intel Corporation
#
# ********************** COPYRIGHT INTEL CORPORATION ***********************


"""
    Global Functions
"""

import gettext
import locale
import os
import json

from edatasheets_creator.constants import configconstants
from edatasheets_creator.utility.path_utilities import get_relative_path, validateRealPath


try:

    # application configuration
    settingsFile = configconstants.SETTINGS_LOCATION + '/' + configconstants.SETTINGS_FILE
    settingsFile = get_relative_path(settingsFile)
    appLocale = configconstants.DEFAULT_LOCALE

    # Load Configuration/Settings File
    if validateRealPath(settingsFile):
        with open(settingsFile, 'r') as f:
            configValues = json.load(f)
            appLocale = configValues[configconstants.SETTING_LOCALE]
            f.close()
    else:
        print('Warning:  ' + settingsFile + ' configuration file does not exist. ')

    # i18n Initialization
    i18nLocale = configconstants.DEFAULT_LOCALE

    # get default locale for machine
    current_locale, encoding = locale.getdefaultlocale()

    locale_path = configconstants.LOCALE_DIRECTORY

    # make sure the language is installed
    if len(appLocale) > 0:
        i18nLocale = appLocale
        path = locale_path + i18nLocale
        path = get_relative_path(path)

        # language does not exist so set default
        if not os.path.isdir(path):
            print('Warning:  ' + i18nLocale + ' locale path and language file do not exist.  Defaulting to ' + configconstants.DEFAULT_LOCALE)
            i18nLocale = configconstants.DEFAULT_LOCALE

    # load the messages file for specified language
    translate = gettext.translation(configconstants.MESSAGES_DOMAIN, localedir=locale_path, languages=[i18nLocale], fallback=True)
    translate.install()
    t = translate.gettext

except Exception as e:
    print(e)
