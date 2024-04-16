{
    "$id": "https://github.com/edatasheets/digital-datasheets/blob/main/part-spec/ic_io/high speed mux.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "high speed mux",
    "type": "object",
    "properties": {
        "muxRatio": {
            "description": "ratio of inputs to outputs",
            "$ref": "../common/ratio.json#/ratio"
        },
        "inputInterfaces": {
            "description": "list of interfaces high speed mux is designed for",
            "examples": [
                "HDMI2.0",
                "DP HBR2"
            ],
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "maxDataRate": {
            "description": "maximum data rate supported by high speed mux",
            "comment": "units of Hz",
            "$ref": "../common/unit.json#/unit"
        },
        "insertionLoss": {
            "description": "insertion loss through high speed mux",
            "comment": "units of dB",
            "type": "number"
        },
        "currentConsumption": {
            "description": "current used by device in various power modes",
            "$ref": "../common/currentConsumption.json#/currentConsumption"
        }
    }
}
