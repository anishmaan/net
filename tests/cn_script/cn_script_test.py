import unittest
from PIL import Image
import numpy as np

import importlib
utils = importlib.import_module('extensions.sd-webui-controlnet.tests.utils', 'utils')
utils.setup_test_env()

from scripts import external_code, processor
from scripts.controlnet import prepare_mask, Script
from modules import processing


class TestPrepareMask(unittest.TestCase):
    def test_prepare_mask(self):
        p = processing.StableDiffusionProcessing()
        p.inpainting_mask_invert = True
        p.mask_blur = 5

        mask = Image.new('RGB', (10, 10), color='white')

        processed_mask = prepare_mask(mask, p)

        # Check that mask is correctly converted to grayscale
        self.assertTrue(processed_mask.mode, "L")

        # Check that mask colors are correctly inverted
        self.assertEqual(processed_mask.getpixel((0, 0)), 0)  # inverted white should be black

        p.inpainting_mask_invert = False
        processed_mask = prepare_mask(mask, p)

        # Check that mask colors are not inverted when 'inpainting_mask_invert' is False
        self.assertEqual(processed_mask.getpixel((0, 0)), 255)  # white should remain white

        p.mask_blur = 0
        mask = Image.new('RGB', (10, 10), color='black')
        processed_mask = prepare_mask(mask, p)

        # Check that mask is not blurred when 'mask_blur' is 0
        self.assertEqual(processed_mask.getpixel((0, 0)), 0)  # black should remain black


class TestScript(unittest.TestCase):
    def test_bound_check_params(self):
        def param_required(module: str, param: str) -> bool:
            configs = processor.preprocessor_sliders_config[module]
            config_index = ('processor_res', 'threshold_a', 'threshold_b').index(param)
            return config_index < len(configs) and configs[config_index] is not None

        for module in processor.preprocessor_sliders_config.keys():
            for param in ('processor_res', 'threshold_a', 'threshold_b'):
                with self.subTest(param=param, module=module):
                    unit = external_code.ControlNetUnit(
                        module=module,
                        **{param: -100},
                    )
                    Script.bound_check_params(unit)
                    if param_required(module, param):
                        self.assertGreaterEqual(getattr(unit, param), 0)
                    else:
                        self.assertEqual(getattr(unit, param), -100)


if __name__ == "__main__":
    unittest.main()
