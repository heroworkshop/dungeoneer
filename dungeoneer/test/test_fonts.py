import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from dungeoneer import fonts


def fake_font_call(name, size):
    return name, size


class TestFonts(unittest.TestCase):
    def setUp(self):
        patcher = patch("pygame.font.get_fonts", return_value=["fontb"], autospec=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    @patch("pygame.font.SysFont", new=fake_font_call)
    def test_make_font_withMatchingFont_returnsSystemFontSpecified(self):
        result = fonts.make_font(("Font A", "Font B"), 14)
        self.assertEqual(("fontb", 14), result)

    @patch("pygame.font.Font", new=fake_font_call)
    def test_make_font_withMissingFont_returnsDefaultFont(self):
        result = fonts.make_font(("Font A", "Font C"), 14)
        self.assertEqual((None, 14), result)


class TestCaptions(unittest.TestCase):
    def test_fade_in_caption_withUpdate_rendersCaption(self):
        mock_screen = MagicMock()
        mock_font = MagicMock()
        caption = fonts.FadeInCaption("My Caption", mock_font, mock_screen, (100, 100))
        caption.update()
        mock_font.render.assert_called_once()
        mock_screen.blit.assert_called_once()

    def test_fade_in_caption_withHigherStep_rendersFewerFrames(self):
        mock_screen = MagicMock()
        mock_font = MagicMock()
        caption = fonts.FadeInCaption("My Caption", mock_font, mock_screen, (100, 100))
        while caption.update():
            pass
        slow_count = mock_screen.blit.call_count
        mock_screen.reset_mock()
        mock_font.reset_mock()
        caption = fonts.FadeInCaption("My Caption", mock_font, mock_screen, (100, 100), step=2)
        while caption.update():
            pass
        self.assertLess(mock_screen.blit.call_count, slow_count)



if __name__ == '__main__':
    unittest.main()
