# Plugins documentation

## 1.Diff
This plugin takes two JSON files and compares them to check for differences between them. It generates a difference report with HTML format highlighting additions, changes and deletions on the information.

### Inputs:
- file1(string): This corresponds to the absolute file path in the system of the first input file to compare.
- file2(string): This corresponds to the absolute file path in the system of the second input file to compare.

### App plug-in configuration object
```json
    {
        "pluginName": "diff",
        "description":"Generates the html difference report",
        "pluginGUID":"6efd8af2-ea34-49f4-826c-a2ad45595c5f",
        "case":["arg1", "arg2", ""],
        "inputFormats":["json"],
        "outputFormat":"html"
    }

```

## 2.Dita_to_json
This plugin takes a DITA file and returns a JSON file. For this plugin, the functions expect an input XML file, in a DITA format, and after processing stores the output file in the same directory as the input file, except if an output file name is provided, the function takes it as priority and exports it to the provided output directory.

<!-- ### Assumptions

1. The plugin expects the DITA file to have only tables, for now the plugin doesn't support sections in the file. -->

### App plug-in configuration object
```json
    {
        "pluginName": "dita_to_json",
        "description":"Plugin that converts DITA file to JSON.",
        "pluginGUID":"7696d6b4-fb25-4917-8fd9-2958f0f1a47a",
        "case":["arg1", "output", ""],
        "inputFormats":["xml"],
        "outputFormat":"json"
    }
```

## 3.Spreadsheet
This plug-in takes a ".xlsx" file (Excel document), and using a map file, gets the desired information by the user and creates an e-datasheet with that information. If map file is not defined, this plug-in will use a generic map algorithm to parse the input file.

### Inputs:
- inputFileName(string): This correspond to the absolute file path in the system of the input file. This format must be ".xlsx", otherwise the plug-in will launch an exception.
- outputFileName(string): This correspond to the absolute file path in the system of the desired output file name. This format must be ".json".
- mapFileName (string): This corresponds to the absolute file path in the system of the map file. Must be a ".json" file, also this map file must comply with the defined schema in:
```
edatasheets_creator/
 | - schemas/
 |    | - map-schema.json
```
### App plug-in configuration object
```json
    {
        "pluginName": "spreadsheet",
        "description":"Spreadsheet plugin class that implements datasheet generation from an XLSX",
        "pluginGUID":"a8a799ed-969a-4c77-b21b-bf9b77461037",
        "case":["arg1", "output", "map"],
        "inputFormats":["xlsx"],
        "outputFormat":"json"
    }
```