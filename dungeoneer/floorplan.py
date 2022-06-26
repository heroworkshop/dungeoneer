from dungeoneer import game_assets
from dungeoneer.scenery import ScenerySprite
from dungeoneer.spritesheet import SpriteSheet

TILE_HEIGHT = 32
TILE_WIDTH = 32

baby_dungeon_design = ["""
#########~~~###############################
#.....   ~~~      z,z        #            #
#....    ___   #z zZz        #
# zz     ~~~   # z,z,        #
####### #~~# #################
#s______#~~,,,,,,,%,,%%,,,,,,#
#_______#~~,&%%,,,%,,%%,,   >#
#      <#~~,&~&,,,%,,a,,, ,,,#
#  B  z #~~,%%&,,,%,,,,,, ,,,#
#^^^^     ~~,b,,          ,,,#
#^^^^#a###~~ #################
#      #z ~~~                #
#      #   ~~~    #          #
#      #     ~    #          #
#           ~~    #          #
############~~########## #####
#          #~~~              #
#          # ~~~              
#             ~~~            #
#          #   ~~~           #
###############~~~############
#          #   ~~~           #
#          #   ~~~           #
#               ~~~    %     #
#          #   ~~~           #
##############################################
"""]


class SceneryType:
    def __init__(self, sprite_sheet, is_solid=False, animated=True):
        self.sprite_sheet = sprite_sheet
        self.is_solid = is_solid
        self.animated = animated


wood_sheet2 = game_assets.load_image("wood-sheet2.png")
liquids = game_assets.load_image("liquids32.png")
vegetation = game_assets.load_image("vegetation.png")
lava = game_assets.load_image("lava.png")

scenery_types = {"#": SceneryType(SpriteSheet(wood_sheet2, columns=8, rows=16, sub_area=(7, 3, 1, 1)),
                                  is_solid=True),
                 "~": SceneryType(SpriteSheet(liquids, columns=16, rows=12, sub_area=(0, 0, 6, 1))),
                 ".": SceneryType(SpriteSheet(lava, columns=10, rows=1)),
                 "_": SceneryType(SpriteSheet(wood_sheet2, columns=8, rows=16, sub_area=(0, 4, 1, 2)),
                                  animated=False),
                 ",": SceneryType(SpriteSheet(wood_sheet2, columns=8, rows=16, sub_area=(0, 1, 1, 1)),
                                  animated=False),
                 "%": SceneryType(SpriteSheet(vegetation, columns=16, rows=16, sub_area=(1, 3, 1, 1)),
                                  animated=False, is_solid=True),
                 }


def create_objects(design, level, world, offset=(0, 0), tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT):
    ox, oy = offset
    rows = [line for line in design[level].split("\n") if line]
    for row_num, row in enumerate(rows):
        for col_num, ch in enumerate(row):
            x, y = ox + col_num * tile_width, oy + row_num * tile_height
            scenery = scenery_types.get(ch)
            if scenery:
                filmstrip = scenery.sprite_sheet.filmstrip()
                effect = ScenerySprite(x, y, filmstrip, animated=scenery.animated)
                world.effects.add(effect)
                if scenery.is_solid:
                    world.solid.add(effect)
    return col_num, row_num
