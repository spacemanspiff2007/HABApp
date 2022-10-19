from enum import Enum as _Enum
import typing


def _get_str_enum_values(obj: typing.Type[_Enum]) -> typing.Set[str]:
    return {_member.value for _member in obj}


class ItemType(str, _Enum):
    STRING = 'String'
    NUMBER = 'Number'
    SWITCH = 'Switch'
    CONTACT = 'Contact'
    DIMMER = 'Dimmer'
    ROLLERSHUTTER = 'Rollershutter'
    COLOR = 'Color'
    DATETIME = 'DateTime'
    LOCATION = 'Location'
    PLAYER = 'Player'
    GROUP = 'Group'
    IMAGE = 'Image'
    CALL = 'Call'


ITEM_TYPES: typing.Final = _get_str_enum_values(ItemType)


class ItemDimensions(str, _Enum):
    ACCELERATION = 'Acceleration'
    ANGLE = 'Angle'
    AREAL_DENSITY = 'ArealDensity'
    CATALYTIC_ACTIVITY = 'CatalyticActivity'
    DATA_AMOUNT = 'DataAmount'
    DATA_TRANSFER_RATE = 'DataTransferRate'
    DENSITY = 'Density'
    DIMENSIONLESS = 'Dimensionless'
    ELECTRIC_CAPACITANCE = 'ElectricCapacitance'
    ELECTRIC_CHARGE = 'ElectricCharge'
    ELECTRIC_CONDUCTANCE = 'ElectricConductance'
    ELECTRIC_CONDUCTIVITY = 'ElectricConductivity'
    ELECTRIC_CURRENT = 'ElectricCurrent'
    ELECTRIC_INDUCTANCE = 'ElectricInductance'
    ELECTRIC_POTENTIAL = 'ElectricPotential'
    ELECTRIC_RESISTANCE = 'ElectricResistance'
    ENERGY = 'Energy'
    FORCE = 'Force'
    FREQUENCY = 'Frequency'
    ILLUMINANCE = 'Illuminance'
    INTENSITY = 'Intensity'
    LENGTH = 'Length'
    LUMINOUS_FLUX = 'LuminousFlux'
    LUMINOUS_INTENSITY = 'LuminousIntensity'
    MAGNETIC_FLUX = 'MagneticFlux'
    MAGNETIC_FLUX_DENSITY = 'MagneticFluxDensity'
    MASS = 'Mass'
    POWER = 'Power'
    PRESSURE = 'Pressure'
    RADIATION_DOSE_ABSORBED = 'RadiationDoseAbsorbed'
    RADIATION_DOSE_EFFECTIVE = 'RadiationDoseEffective'
    RADIOACTIVITY = 'Radioactivity'
    SOLID_ANGLE = 'SolidAngle'
    SPEED = 'Speed'
    TEMPERATURE = 'Temperature'
    TIME = 'Time'
    VOLUME = 'Volume'
    VOLUMETRIC_FLOW_RATE = 'VolumetricFlowRate'


ITEM_DIMENSIONS: typing.Final = _get_str_enum_values(ItemDimensions)


class GroupItemFunctions(str, _Enum):
    AND = 'AND'
    AVG = 'AVG'
    MAX = 'MAX'
    MIN = 'MIN'
    NAND = 'NAND'
    NOR = 'NOR'
    OR = 'OR'
    SUM = 'SUM'


GROUP_ITEM_FUNCTIONS: typing.Final = _get_str_enum_values(GroupItemFunctions)
