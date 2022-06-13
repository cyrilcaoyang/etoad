# TODO: Implement proper parameter reading and parsing by
#  1. Reading general parameters from a json file, merge with default settings?
#  2. Parse read parameters and generate the actual parameter list as List[tuple] or better architectures
#     Implement that to the method class (specific type or general ABCMetaclass)
#  Maybe implement a specific dataclass for measurement parameters?

OCV_PARAMETERS = [
    ("Rest_time_T", float, 10.0),
    ("Record_every_dE", float, 0.1),
    ("Record_every_dT", float, 0.01),
]