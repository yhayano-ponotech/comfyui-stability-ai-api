# ComfyUI Stability AI API Custom Nodes

A collection of custom nodes for using the [Stability AI API](https://platform.stability.ai/) in ComfyUI.

## Features

This custom node package provides the following functionality:

### Image Generation Nodes
- **StabilityImageUltra**: High-quality image generation
- **StabilityImageCore**: Standard image generation
- **StabilityImageSD3**: Image generation using Stable Diffusion 3.0

### Image Editing Nodes
- **StabilityEdit**: Multi-functional image editing
  - erase: Remove content in masked area
  - inpaint: Regenerate content in masked area
  - outpaint: Extend image in any direction
  - search-and-replace: Replace specified objects
  - search-and-recolor: Change colors of specified objects
  - remove-background: Automatically remove background

### Upscale Nodes
- **StabilityUpscaleFast**: Fast upscaling
- **StabilityUpscaleConservative**: Conservative upscaling
- **StabilityUpscaleCreative**: Creative upscaling (AI detail enhancement)

### Control Nodes
- **StabilityControlSketch**: Generate images from sketches
- **StabilityControlStructure**: Generate images while maintaining structure
- **StabilityControlStyle**: Generate images by referencing styles

### Others
- **StabilityImageToVideo**: Generate videos from images

## Installation

1. Clone this repository into your ComfyUI's `custom_nodes` directory:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/ponotech/comfyui-stability-ai-api.git
```

2. Install dependencies:
```bash
cd comfyui-stability-ai-api
pip install -r requirements.txt
```

3. Create a `config.ini` file and set your Stability AI API key:
```ini
[stability]
api_key = your_api_key_here
```

## Usage

1. Start ComfyUI
2. Add nodes from the "Stability AI" category in the workflow editor
3. Configure node parameters and execute

## Important Notes

- Image size constraints:
  - Minimum edge length: 64px
  - Total pixels: 4096-9437184 px
  - Aspect ratio: between 1:2.5 and 2.5:1
- [Stability AI](https://platform.stability.ai/) account and API key required
- Check [Stability AI pricing page](https://platform.stability.ai/pricing) for API usage fees

## License

This project is released under the [MIT License](LICENSE).