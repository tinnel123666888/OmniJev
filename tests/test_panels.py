import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from mso import panels


class PanelInputTests(unittest.TestCase):
    def test_both_images_are_visible_and_missing_cached_input_fails(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(panels, "PANELS_OFF", False):
            root = Path(directory)
            first, second = root / "first.png", root / "second.png"
            Image.new("RGB", (32, 32), "red").save(first)
            Image.new("RGB", (32, 32), "blue").save(second)
            output = panels.compose_path([str(first), str(second)], directory)
            with Image.open(output) as image:
                self.assertGreater(image.width, 64)
                self.assertGreater(image.getpixel((20, 44))[0], 200)
                self.assertGreater(image.getpixel((58, 44))[2], 200)
            second.unlink()
            with self.assertRaises(FileNotFoundError):
                panels.compose_path([str(first), str(second)], directory)

    def test_single_image_is_not_reencoded(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "first.png"
            Image.new("RGB", (32, 32), "red").save(source)
            self.assertEqual(panels.compose_path([str(source)], directory), str(source))


if __name__ == "__main__":
    unittest.main()
