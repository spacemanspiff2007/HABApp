ITEM_TYPES = {
    'String', 'Number', 'Switch', 'Contact', 'Dimmer', 'Rollershutter',
    'Color', 'DateTime', 'Location', 'Player', 'Group', 'Image',
}

ITEM_DIMENSIONLESS: str = 'Dimensionless'
ITEM_DIMENSION = {'Length', 'Temperature', 'Pressure', 'Speed', 'Intensity', 'Angle', ITEM_DIMENSIONLESS}

GROUP_FUNCTIONS = {'AND', 'OR', 'NAND', 'NOR', 'AVG', 'MAX', 'MIN', 'SUM'}
