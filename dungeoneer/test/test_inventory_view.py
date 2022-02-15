import unittest
import pygame

from dungeoneer import interfaces
from dungeoneer.inventory import Inventory
from dungeoneer.inventory_view import InventoryView, SlotView
from dungeoneer import inventory_view
from dungeoneer.interfaces import Direction, Item


class TestInventoryView(unittest.TestCase):

    def setUp(self):
        pygame.init()

    def test_construct_withInventory_createsEqualSizedContainer(self):
        inventory = Inventory()
        view = InventoryView(inventory)
        self.assertEqual(len(inventory), len(view))

    def test_construct_withGroup_AddsOneSpriteForEachInventoryItem(self):
        world = interfaces.SpriteGroups()
        view = InventoryView(Inventory(), sprite_groups=[world.hud])
        self.assertEqual(len(world.hud), len(view))

    def test_construct_withEmptyInventory_createsEmptyBoxes(self):
        view = InventoryView(Inventory())
        for slot in view.slot_views:
            image = slot.image
            self.assertEqual(inventory_view.EMPTY_BOX, image)

    def test_construct_withTopDownOrentation_positionsSlotViewsAsColumn(self):
        view = InventoryView(Inventory(), orientation=Direction.TOP_DOWN)
        rects = [slot.rect for slot in view.slot_views]
        x_vals = [r[0] for r in rects]
        y_vals = [r[1] for r in rects]
        # y_vals need to be increasing:
        self.assertEqual(len(y_vals), len(set(y_vals)), "y_vals need to all be different")
        self.assertEqual(y_vals, sorted(y_vals), "y_vals need to be in order")

        self.assertEqual(len(x_vals), x_vals.count(x_vals[0]), "x_vals need to all be the same")

    def test_construct_withLeftToRightOrentation_positionsSlotViewsAsRow(self):
        view = InventoryView(Inventory(), orientation=Direction.LEFT_TO_RIGHT)
        rects = [slot.rect for slot in view.slot_views]
        x_vals = [r[0] for r in rects]
        y_vals = [r[1] for r in rects]
        # x_vals need to be increasing:
        self.assertEqual(len(x_vals), len(set(x_vals)), "y_vals need to all be different")
        self.assertEqual(x_vals, sorted(x_vals), "y_vals need to be in order")

        self.assertEqual(len(y_vals), y_vals.count(y_vals[0]), "x_vals need to all be the same")

    def test_construct_withItemInInventorySlot0_hasImageReflectedInViewSlot(self):
        inventory = Inventory()
        inventory.add_item(Item("sword"), slot=0)
        view = InventoryView(inventory)
        image0, image1 = (sv.image for sv in view.slot_views[:2])
        self.assertNotEqual(image0, image1)

    def test_SlotView_onInventoryUpdate_updatesImage(self):
        inventory = Inventory()
        view = InventoryView(inventory)
        image0 = view.slot_views[0].image
        inventory.add_item(Item("arrow"), slot=0)
        image1 = view.slot_views[0].image
        self.assertNotEqual(image0, image1)


class TestSlotView(unittest.TestCase):

    def setUp(self):
        pygame.init()

    def test_construct_withItem(self):
        SlotView(0, 0)

    # def test_compose_item_image_withMultipleCount_rendersDifferentImageToSingleCount(self):
    #     arrow_slot = SlotView(0, 0, item=Item("arrow", count=1))
    #     multi_slot = SlotView(0, 0, item=Item("arrow", count=2))
    #     image1 = PixelArray(arrow_slot.image)
    #     image2 = PixelArray(multi_slot.image)
    #
    #     diff = image1.compare(image2)
    #     difference_count = np.count_nonzero(np.all(diff == 0))
    #     self.assertNotEqual(0, difference_count)


if __name__ == '__main__':
    unittest.main()
