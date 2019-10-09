ITEM_TYPES = [
    'String', 'Number', 'Switch', 'Contact', 'Dimmer', 'Rollershutter',
    'Color', 'Contact', 'DateTime', 'Location', 'Player', 'Group']

GROUP_FUNCTIONS = ['AND', 'OR', 'NAND', 'NOR', 'AVG', 'MAX', 'MIN', 'SUM']

from .values import OnOffValue, PercentValue, UpDownValue, HSBValue, QuantityValue

from .map_values import map_openhab_types