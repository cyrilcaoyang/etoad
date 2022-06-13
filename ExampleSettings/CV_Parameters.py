# TODO: Implement proper parameter reading and parsing by
#  1. Reading general parameters from a json file, merge with default settings?
#  2. Parse read parameters and generate the actual parameter list as List[tuple] or better architectures
#     Implement that to the method class (specific type or general ABCMetaclass)
#  Maybe implement a specific dataclass for measurement parameters?

CV_PARAMETERS = [
    ("Voltage_step", float, 0.0, 0),  # E_i
    ("Scan_Rate", float, 0.05, 0),
    ("vs_initial", bool, False, 0),
    ("Voltage_step", float, 0.5, 1),  # E_1
    ("Scan_Rate", float, 0.05, 1),
    ("vs_initial", bool, False, 1),
    ("Voltage_step", float, 0.0, 2),  # E_2
    ("Scan_Rate", float, 0.05, 2),
    ("vs_initial", bool, False, 2),
    ("Voltage_step", float, 0.0, 3),  # E_i  (again??)
    ("Scan_Rate", float, 0.05, 3),
    ("vs_initial", bool, False, 3),
    ("Voltage_step", float, 0.0, 4),  # E_f
    ("Scan_Rate", float, 0.05, 4),
    ("vs_initial", bool, False, 4),
    ("Scan_number", int, 2),
    ("Record_every_dE", float, 0.01),
    ("Average_over_dE", bool, True),
    ("N_Cycles", int, 5),
    ("Begin_measuring_I", float, 0),
    ("End_measuring_I", float, 1)
]