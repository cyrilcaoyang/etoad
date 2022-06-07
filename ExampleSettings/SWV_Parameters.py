# TODO: Implement proper parameter reading and parsing by
#  1. Reading general parameters from a json file, merge with default settings?
#  2. Parse read parameters and generate the actual parameter list as List[tuple] or better architectures
#     Implement that to the method class (specific type or general ABCMetaclass)
#  Maybe implement a specific dataclass for measurement parameters?

SWV_PARAMETERS = [
    ("Ei", float, -0.5),
    ("OCi", bool, True),
    ("Rest_time_Ti", float, 1),
    ("Ef", float, 0.5),
    ("OCf", bool, False),
    ("PH", float, 0.025),  # Value has to be given in V (contrary to documentation)
    ("PW", float, 0.050),  # Value has to be given in s (contrary to documentation)
    ("SH", float, 0.010),  # Value has to be given in V (contrary to documentation)
    ("Begin_measuring_I", float, 0.0),
    ("End_measuring_I", float, 1.0),
    ("I_Range", int, 8)
]