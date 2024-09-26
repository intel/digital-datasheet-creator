"""
Key datasheet field name constants/definitions.
"""

DATASHEET_TITLE_FIELD = "title"
DATASHEET_NAMESPACE_FIELD = "namespace"
DATASHEET_DESCRIPTION_FIELD = "description"
DATASHEET_INPUT_FILE_FIELD = "inputFile"
DATASHEET_CREATION_DATE_FIELD = "generatedOn"
DATASHEET_CREATION_BY_FIELD = "generatedBy"
DATASHEET_GUID_FIELD = "guid"
DATASHEET_PLATFORM_ABBREVIATION_FIELD = "platformAbbreviation"
DATASHEET_SKU_FIELD = "sku"
DATASHEET_REVISION_FIELD = "revision"
DATASHEET_HEADING = 'heading'
DATASHEET_LISTING = 'listing'
DATASHEET_TABLES = 'Tables'
DATASHEET_TABLE = 'table'
DATASHEET_TABLES_LOWER = 'tables'
DATASHEET_NOTES = 'notes'
DATASHEET_NAMESPACE = 'namespace'
DATASHEET_LIST = 'list'
DATASHEET_SERIAL_NUMBER = 'SN'
DATASHEET_FIGURE = 'fig'
DATASHEET_SURFACE_FORM = 'surfaceForm'
DATASHEET_KNOWN_RULES = {"note", "traceWidth", "intra-pair", "zSe-Default", "zDiff-Default", "aSe", "aDiff", "traceSpacing", "k"}
DATASHEET_RULES_LIST = ["note", "traceWidth", "intra-pair", "zSe-Default", "zDiff-Default", "aSe", "aDiff", "traceSpacing", "k"]
DATASHEET_SIGNALS = ['catocs', 'cstoca', 'cstocs', 'catoca', 'dqtodq', 'dqtodqofsamebyte', 'byteTobyte', 'rdqspairtodqofsamebyte', 'dqtoca', 'DQ to CS',
                     'WCK to CA', 'WCK to CS ', 'WCK to CLK', 'K CA to CS', 'K CA to CS', 'clktoca', 'clktocs', 'K CA to CA',
                     'K CS to CS', 'K CS to CA', 'K CLK to CS', 'K CLK to CS', 'K DQ to DQ of same byte', 'K Byte to Byte', 'K RDQS pair to DQ of same byte',
                     'K WCK to CA', 'K WCK to CS', 'K WCK to CLK', 'dqsPairToDqOfSameByte', 'wckToDq', 'kDqsPairToDqOfSameByte', 'kClkToCa']
DATASHEET_RULES_LIST_MAPPING = {"traceWidth": "traceWidth", "intra-pair": "intraPair", "zDiff-Default": "impedance", "aSe": "losses", "note": "note",
                                "zSe-Default": "impedance", "aDiff": "losses", "traceSpacing": "traceSpacing", "k": "k"}
DATASHEET_SIGNAL_NAME = 'signal'
DATASHEET_SIGNALS_NAME = 'signals'
DATASHEET_CHANNELS_NAME = 'channels'
DATASHEET_PCB_LAYER_COUNT = 'pcblayercount'
DATASHEET_SIGNAL_TYPE = 'signalType'
DATASHEET_TRACE_SPACING_NAME = 'traceSpacing'
DATASHEET_K_VALUE_NAME = 'k'
DATASHEET_NOT_AVAILABLE = 'NA'
DATASHEET_ROUTING_LAYER = 'routinglayers'
DATASHEET_TOPOLOGY = 'topology'
DATASHEET_INTERFACE = 'interface'
DATASHEET_INTERFACE_TYPE = 'interfaceType'
DATASHEET_MEMORY = 'memory'
DATASHEET_A_SE = 'aSe'
DATASHEET_Z_SE_DEFAULT = 'zSe-Default'
DATASHEET_A_DIFF = 'aDiff'
DATASHEET_Z_DIFF_DEFAULT = 'zDiff-Default'
DATASHEET_INTRA_PAIR = 'intra-pair'
DATASHEET_VARIANT = 'variant'
DATASHEET_HEADER_KEYS = ['pcbtype', 'pcbthickness', 'pcblayercount', 'category', 'variant',
                         'interface', 'topology', 'channels', 'trace', 'tlinetype', 'routinglayers', 'signals',
                         'pingroup/location', 'tracewidth', 'intra-pair', 'zse',
                         'zdiff', 'ase', 'adiff']
DATASHEET_DEFAULT_TITLE = "Datasheet"
DATASHEET_DEFAULT_TITLE_LOWER = "datasheet"
DATASHEET_DEFAULT_DESCRIPTION = "Describes a part"
DATASHEET_DEFAULT_INPUT_FILE_FIELD = "Unknown"
DATASHEET_RULE_VALUE = 'value'
DATASHEET_RULE_UNIT = 'unitOfMeasure'
DATASHEET_RULE_NAME = 'parameter'
DATASHEET_NAMESPACE = "https://www.intel.com/design"
DATASHEET_CREATOR = "Intel e-Datasheet Creator"
DATASHEET_GENERAL_TITLE = "Intel e-Datasheet"

DATASHEET_DEFAULT_MAX_ROWS = 23
DATASHEET_DEFAULT_DATASTART = 2

DATASHEET_CONNECTOR_KEYWORD = 'connector'
DATASHEET_BALLMAP_KEYWORD = 'ballmap'
DATASHEET_PINS_KEYWORD = 'Pins'
DATASHEET_TERMINAL_IDENTIFIER_KEYWORD = 'terminalIdentifier'
DATASHEET_FUNCTION_PROPERTIES_KEYWORD = 'functionProperties'
DATASHEET_NUMBER_OF_SUPPORTED_FUNCTIONS = "numberOfSupportedFunctions"
DATASHEET_EXTERNAL_COMPONENTS = 'externalComponents'
DATASHEET_POWER_SUPPLY_PROTECTION = 'powerSupplyProtection'
DATASHEET_POWER_COMPONENT_DEFINITIONS = 'powerComponentDefinitions'
DATASHEET_INSTANCE_DEFINITION = 'instanceDefinition'
DATASHEET_INSTANCE_DEF_EXTERNAL_FILE = 'instanceDef_externalFileMap'
DATASHEET_COMPONENT_PROTECTION_THRESHOLD = 'componentProtectionThresholds'
DATASHEET_PART_PIN_PATHS = 'partPinPaths'
DATASHEET_PIN_PATHS = 'pinPaths'
DATASHEET_COMPONENT_PIN_NAMES = 'componentPinNames'
DATASHEET_COMPONENT_ID = 'componentID'
DATASHEET_ORDERABLE_MPN = 'orderableMPN'
DATASHEET_COMPLIANCE_LIST = 'complianceList'
DATASHEET_CORE_PROPERTIES = 'coreProperties'
DATASHEET_DIODE_P_TOT = 'pTot'
DATASHEET_DIODE_VF = 'vf'
DATASHEET_DIODE_IR = 'ir'
DATASHEET_DIODE_VCL = 'vcl'
DATASHEET_DIODE_VZ = 'vz'
DATASHEET_CONDITIONAL_PROPERTY = 'conditionalProperty'
DATASHEET_GRAPH = 'graph'
DATASHEET_POWER_FET_PROPERTIES = 'powerFetProperties'
DATASHEET_POWER_FET_PROPERTIES_PARAMETERS = ['singlePowerFetPair', 'inputPowerFetPair', 'outputPowerFetPair']
DATASHEET_INTEGRATED_FET = 'integratedFetProperties'
DATASHEET_CONDITIONAL_PROPERTY_KEY_OWNERS = ['pTot', 'vf', 'ir', 'vcl', 'vz', 'phaseJitter', 'efficiency', 'outputPower', 'thd+n', 'gyroSensitivity', 'collectorBaseCutOffCurrent', 'emitterBaseCutOffCurrent',
                                             'dcCurrentGain', 'collectorEmitterSaturationVolt', 'baseEmitterSaturationVoltage', 'delayTime', 'riseTime', 'storageTime', 'fallTime', 'collectorCapacitance',
                                             'emitterCapacitance', 'transitionFrequency', 'iv', 'iDss', 'iGss', 'forwardTransconductance', 'rdson', 'rg', 'ciss', 'coss', 'crss', 'qg', 'qgd', 'qgs', 'qrr',
                                             'tdON', 'tdOFF', 'trr', 'onResistance', 'enableTime', 'rampTime', 'offTime']
DATASHEET_ARRAY_STRINGS = ['interface', 'inputInterfaces', 'outputInterfaces', 'componentList', 'inputPowerSource', 'batteryConfig', 'batteryCellChemistry', 'batteryChargerProtections']
DATASHEET_GRAPH_KEY_OWNERS = ['ifVsVf', 'icVsHfe', 'icVsVce', 'ibVsVce', 'pdVsTemp', 'idVsVds', 'idVsVgs', 'powerEfficiency', 'powerSupplyRejectionRatio', 'rmsOutputNoise']
DATASHEET_CONDITIONS = 'conditions'
DATASHEET_DATA = 'data'
DATASHEET_CURVE = 'curve'
DATASHEET_X_DATA = 'xData'
DATASHEET_Y_DATA = 'yData'
DATASHEET_TYP_VALUE = "Typ Value"
DATASHEET_PIN_EXTERNAL_COMPONENTS_START = "Component Type"
DATASHEET_SCHEMA_MAPPING = {'Pins': 'pins', 'pins': 'pins', 'Package': 'package', 'package': 'package', "componentID": "componentID", "componentid": "componentID", "externalComponents": "externalComponents", "level shifter": "level_shifter",
                            'currentConsumption': 'currentConsumption', 'coreProperties': 'coreProperties', 'externalFileMap': 'externalFileMap', 'externalfilemap': 'externalFileMap', 'diode': 'diode',
                            'ifVsVf': 'ifVsVf', 'pTot': 'pTot', 'vcl': 'vcl', 'vz': 'vz', 'vf': 'vf', 'ir': 'ir', 'partPinPaths': 'partPinPaths', 'adc': 'adc', 'dac': 'dac',
                            'switch': 'switch', 'clock': 'clock', 'oscillator': 'oscillator', 'phaseJitter': 'phaseJitter', 'bridge_chip': 'bridge_chip',
                            'highspeed_mux': 'highspeed_mux', 'redriver': 'redriver', 'retimer': 'retimer', 'usb_bc12': 'usb_bc12', 'usbc_pdcontroller': 'usbc_pdcontroller',
                            'componentProtectionThresholds': 'componentProtectionThresholds', 'powerSupplyProtection': 'powerSupplyProtection', 'usbc_portcontroller': 'usbc_portcontroller',
                            'speaker_amplifier': 'speaker_amplifier', 'outputPower': 'outputPower', 'efficiency': 'efficiency', 'thd+n': 'thd+n', 'tpm': 'tpm', 'eeprom': 'eeprom',
                            'flash_memory': 'flash_memory', 'rom': 'rom', 'commonModeAttenuation': 'commonModeAttenuation', 'capacitorDerating': 'capaciorDerating', 'ferrite_bead': 'ferrite_bead',
                            'saturationCurve': 'saturationCurve', 'resonantFrequencyCurve': 'resonantFrequencyCurve', 'resistorDerating': 'resistorDerating', 'gyroSensitivity': 'gyroSensitivity',
                            'collectorBaseCutOffCurrent': 'collectorBaseCutOffCurrent', 'emitterBaseCutOffCurrent': 'emitterBaseCutOffCurrent', 'dcCurrentGain': 'dcCurrentGain',
                            'collectorEmitterSaturationVolt': 'collectorEmitterSaturationVoltage', 'baseEmitterSaturationVoltage': 'baseEmitterSaturationVoltage', 'delayTime': 'delayTime',
                            'riseTime': 'riseTime', 'storageTime': 'storageTime', 'fallTime': 'fallTime', 'collectorCapacitance': 'collectorCapacitance', 'emitterCapacitance': 'emitterCapacitance',
                            'transitionFrequency': 'transitionFrequency', 'icVsHfe': 'icVsHfe', 'icVsVce': 'icVsVce', 'ibVsVce': 'ibVsVce', 'pdVsTemp': 'pdVsTemp', 'iv': 'iv', 'iDss': 'iDss',
                            'iGss': 'iGss', 'idVsVds': 'idVsVds', 'idVsVgs': 'idVsVgs', 'forwardTransconductance': 'forwardTransconductance', 'rdson': 'rdson', 'rg': 'rg', 'ciss': 'ciss', 'coss': 'coss',
                            'crss': 'crss', 'qg': 'qg', 'qgd': 'qgd', 'qgs': 'qgs', 'qrr': 'qrr', 'tdON': 'tdON', 'tdOFF': 'tdOFF', 'trr': 'trr', 'instanceDef_externalFileMap': 'instanceDefinition',
                            'powerComponentDefinitions': 'powerComponentDefinitions', 'integratedFetProperties': 'integratedFetProperties', 'powerEfficiency': 'powerEfficiency', 'onResistance': 'onResistance',
                            'enableTime': 'enableTime', 'rampTime': 'rampTime', 'offTime': 'offTime', 'powerSupplyRejectionRatio': 'powerSupplyRejectionRatio', 'rmsOutputNoise': 'rmsOutputNoise',
                            'singlePowerFetPair': 'singlePowerFetPair', 'inputPowerFetPair': 'inputPowerFetPair', 'outputPowerFetPair': 'outputPowerFetPair'}
DATASHEET_SCHEMA_PROPERTY_MAPPING = {'string': 'str', 'number': 'int', 'array': 'list', 'object': 'dict', 'boolean': 'bool'}
DATASHEET_UNIT_LIST = ['length', 'width', 'height', 'pitch', 'vihMin', 'vihMax', 'vilMax', 'vilMin', 'vol', 'voh', 'absVmax', 'absVmin', 'vmax', 'imax', 'inputLeakage', 'outputLeakage', 'dcResistance', 'internalPullUp', 'internalPullDown',
                       'inputvoltage', 'outputvoltage', 'quiescentCurrent', 'shutdownCurrent', 'activeCurrent', 'sleepCurrent', 'idleCurrent']
DATASHEET_EMPTY_MACRO_UNIT = 'Typ Value: , Si_Unit: , Unit Name: , min Value: , max Value: , Unit factor: , Relative Value Reference: , Relative Value Modifier: , Relative Value Operator: , Value Defined: '
DATASHEET_GROUPING = {'clock': 'clock', 'oscillator': 'clock', 'componentID': 'common', 'componentProtectionThresholds': 'common', 'conditionalProperty': 'common', 'coreProperties': 'common',
                      'currentConsumption': 'common', 'externalFile': 'common', 'graph': 'common', 'package': 'common', 'pinPaths': 'common', 'pinSpec': 'common', 'powerFetProperties': 'common',
                      'ratio': 'common', 'register': 'common', 'unit': 'common', 'adc': 'data_converter', 'dac': 'data_converter', 'connector': 'hardware', 'switch': 'hardware', 'bridge_chip': 'ic_io',
                      'highspeed_mux': 'ic_io', 'level_shifter': 'ic_io', 'redriver': 'ic_io', 'retimer': 'ic_io', 'usb_bc12': 'ic_io', 'usbc_pdcontroller': 'ic_io', 'usbc_portcontroller': 'ic_io', 'microcontroller': 'ic_microcontroller',
                      'audio_codec': 'ic_misc', 'speaker_amplifier': 'ic_misc', 'tpm': 'ic_misc', 'wlan_module': 'ic_misc', 'wwan_module': 'ic_misc', 'logic_gate': 'logic', 'dram': 'memory', 'eeprom': 'memory',
                      'flash_memory': 'memory', 'rom': 'memory', 'capacitor': 'passives', 'common_mode_choke': 'passives', 'ferrite_bead': 'passives', 'inductor': 'passives', 'resistor': 'passives',
                      'battery_charger': 'power', 'displaybacklight_driver': 'power', 'linear_regulator': 'power', 'load_switch': 'power', 'pmic': 'power', 'switching_regulator': 'power',
                      'bjt': 'semiconductor', 'diode': 'semiconductor', 'led': 'semiconductor', 'mosfet': 'semiconductor', 'accelerometer': 'sensor', 'gyroscope': 'sensor', 'magnetic_sensor': 'sensor',
                      'thermal_sensor': 'sensor', 'sd_card': 'storage', 'ssd': 'storage', 'valueOptions': 'common', 'values': 'common'}
DATASHEET_COMPONENT_KEYS = ['componentID', 'coreProperties', 'pins', 'package', 'externalfilemap', 'componentid']
DATASHEET_ROOT_SCHEMA_NAME = 'component'
DATASHEET_PART_TYPE = 'partType'
DATASHEET_COMPONENT_TYPE = 'componentType'
DATASHEET_CONFIGURATION = 'configuration'
DATASHEET_COMPONENT_COMMON_MAPPING = {'pins': 'pinSpec', 'package': 'package', 'Pins': 'pinSpec', 'functionProperties': 'pinSpec', 'vihMin': 'pinSpec', 'vihMax': 'pinSpec', 'vilMax': 'pinSpec', 'vilMin': 'pinSpec',
                                      'vol': 'pinSpec', 'voh': 'pinSpec', 'absVmax': 'pinSpec', 'absVmin': 'pinSpec', 'vmax': 'pinSpec', 'imax': 'pinSpec', 'inputLeakage': 'pinSpec', 'outputLeakage': 'pinSpec',
                                      'dcResistance': 'pinSpec', 'voltageOptions': 'pinSpec', 'internalPullUp': 'pinSpec', 'internalPullDown': 'pinSpec', 'externalComponents': 'pinSpec',
                                      'externalFileMap': 'component', 'pins-Externalcomponents': 'pinSpec', 'length': 'package', 'width': 'package', 'height': 'package', 'valueOptions': 'values'}
DATASHEET_DEFAULT_KEYS = ['$id', '$schema', 'title', '$defs', 'type', 'properties', 'required', 'additionalProperties']
DATASHEET_EXTERNAL_FILE_MAP_KEYS = ['coreProperties', 'additionalCoreProperties', 'pins', 'package']
DATASHEET_VALUE_KEYS = ['typValue', 'siUnit', 'unitName', 'minValue', 'maxValue', 'unitFactor', 'relativeValueReference', 'relativeValueModifier', 'relativeValueOperator', 'valueDefined', 'conditions']
DATASHEET_EXTERNAL_PINS = ['pins-Externalcomponents', 'pins-Partpinpaths']
DATASHEET_NAME_KEY = 'name_key'
DATASHEET_VALUES_PARAMETER = 'values'
DATASHEET_VALUE_OPTIONS_PARAMETER = 'valueOptions'
