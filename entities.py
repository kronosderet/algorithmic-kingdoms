# entities.py — Re-export shim for backward compatibility
# Actual implementations split into: entity_base, unit, building_shapes, building, projectiles
from entity_base import Entity, _process_combat_hit
from unit import Unit
from building_shapes import (_l_system_expand, _l_system_render, _sierpinski,
                             _koch_curve_pts, _koch_snowflake,
                             _TH_BROWN, _TH_GREEN, _BK_MAROON,
                             _RF_GRAY, _TW_STONE, _FORGE_ORANGE, _STEEL_BLUE)
from building import Building
from projectiles import Arrow, Cannonball, Explosion

__all__ = [
    'Entity', '_process_combat_hit',
    'Unit', 'Building',
    'Arrow', 'Cannonball', 'Explosion',
    '_l_system_expand', '_l_system_render', '_sierpinski',
    '_koch_curve_pts', '_koch_snowflake',
    '_TH_BROWN', '_TH_GREEN', '_BK_MAROON',
    '_RF_GRAY', '_TW_STONE', '_FORGE_ORANGE', '_STEEL_BLUE',
]
