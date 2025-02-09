from .stability_nodes import StabilityImageUltra, StabilityImageCore, StabilityImageSD3
from .stability_nodes import StabilityUpscaleFast, StabilityUpscaleConservative, StabilityUpscaleCreative
from .stability_nodes import StabilityEdit, StabilityImageToVideo

NODE_CLASS_MAPPINGS = {
    "StabilityImageUltra": StabilityImageUltra,
    "StabilityImageCore": StabilityImageCore, 
    "StabilityImageSD3": StabilityImageSD3,
    "StabilityUpscaleFast": StabilityUpscaleFast,
    "StabilityUpscaleConservative": StabilityUpscaleConservative,
    "StabilityUpscaleCreative": StabilityUpscaleCreative,
    "StabilityEdit": StabilityEdit,
    "StabilityImageToVideo": StabilityImageToVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StabilityImageUltra": "Stability Ultra Image Generation",
    "StabilityImageCore": "Stability Core Image Generation",
    "StabilityImageSD3": "Stability SD3 Image Generation",
    "StabilityUpscaleFast": "Stability Fast Upscaler",
    "StabilityUpscaleConservative": "Stability Conservative Upscaler",
    "StabilityUpscaleCreative": "Stability Creative Upscaler",
    "StabilityEdit": "Stability Image Editor",
    "StabilityImageToVideo": "Stability Image to Video"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']