DEFS = {
    "木棍": {
        "kind": "item",
        "attrs": {
            "weight":        {"base": 1.0, "variance": 0.5},
            "size":          {"base": 2,   "variance": 1},
            "sharpness":     {"base": 1,   "variance": 1},
            "flammability":  {"fixed": 8},
            "hardness":      {"fixed": 3},
            "material":      {"fixed": "木"},
        },
    },
    "玻璃瓶": {
        "kind": "item",
        "attrs": {
            "weight":        {"base": 0.4, "variance": 0.1},
            "size":          {"fixed": 2},
            "sharpness":     {"fixed": 2},
            "flammability":  {"fixed": 0},
            "hardness":      {"fixed": 2},
            "material":      {"fixed": "玻璃"},
        },
    },
    "治疗药水": {
        "kind": "item",
        "attrs": {
            "weight":        {"fixed": 0.5},
            "size":          {"fixed": 1},
            "sharpness":     {"fixed": 0},
            "flammability":  {"fixed": 0},
            "hardness":      {"fixed": 1},
            "material":      {"fixed": "玻璃"},
            "drinkable":     {"fixed": True},
            "heal":          {"fixed": 10},
        },
    },
    "野狼": {
        "kind": "character",
        "attrs": {
            "hp":      {"fixed": 20},
            "max_hp":  {"fixed": 20},
            "attack":  {"fixed": 6},
            "defense": {"fixed": 1},
        },
    },
    "流浪剑客": {
        "kind": "character",
        "attrs": {
            "hp":      {"fixed": 35},
            "max_hp":  {"fixed": 35},
            "attack":  {"fixed": 10},
            "defense": {"fixed": 3},
        },
    },
}