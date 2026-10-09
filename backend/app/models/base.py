"""Base model interface for medical image analysis."""
import base64
from io import BytesIO
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
import time
from pathlib import Path
import numpy as np
from PIL import Image
import torch
import cv2

from ..core.logging import get_logger
# from ..utils import model_utils


class BaseModel(ABC):
    """Abstract base class for medical image analysis models."""
    
    def __init__(self, model_name: str, device: str = "cpu"):
        """Initialize model.
        
        Args:
            model_name: Name of the model
            device: Device for inference ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        # self.gradcam_analyser = None
        self.logger = get_logger(f"model.{model_name}")
        
    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """Load model from checkpoint.
        
        Args:
            model_path: Path to model checkpoint
        """
        pass

    # @abstractmethod
    # def load_gradcam(self, model_path: str) -> None:
    #     """Load model into gradcam."""
    #     # self.gradcam_analyser = model_utils.GradCAMPlusPlus(self.model, ...)
    #     pass
    
    @abstractmethod
    def preprocess(self, image: Image.Image) -> tuple[torch.Tensor, ...]:
        """Preprocess image for model input.
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed tensor
        """
        pass
    
    @abstractmethod
    def predict(self, input_tensors: tuple[torch.Tensor, ...]) -> tuple[torch.Tensor, ...]:
        """Run model inference.
        
        Args:
            input_tensor: Preprocessed input tensor
            
        Returns:
            Model output tensor
        """
        pass
    
    @abstractmethod
    def postprocess(self, output: tuple[torch.Tensor, ...]) -> tuple[Dict[str, Any], np.ndarray]:
        """Postprocess model output.
        
        Args:
            output: Raw model output
            
        Returns:
            Processed results dictionary
        """
        pass

    @staticmethod
    def generate_overlay(spatial_np, cam2_resized) -> np.ndarray:
        heatmap = cv2.applyColorMap(np.uint8(255 * cam2_resized), cv2.COLORMAP_JET) # pyright: ignore[reportArgumentType, reportCallIssue]
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB) / 255.0
        overlay = np.clip(0.6 * spatial_np[..., None] + 0.4 * heatmap, 0, 1)
        return overlay
    
    def analyze(self, image_path: str) -> Dict[str, Any]:
        """Complete analysis pipeline.
        
        Args:
            image_path: Path to input image
            
        Returns:
            Analysis results with metadata
        """
        start_time = time.time()
        
        try:
            # Load and validate image
            image = self._load_image(image_path)
            
            # Preprocess
            input_tensors = self.preprocess(image)
            
            # Predict
            output = self.predict(input_tensors)
            
            # Postprocess
            results, cam = self.postprocess(output)

            # generate CAM image
            spatial = input_tensors[0] #0th is always spatial
            # spatial_vis = spatial.unsqueeze(0).to(self.device)

            # Generate CAM image at high resolution (512x512) for clarity
            spatial_vis = cv2.resize(spatial.detach().numpy().squeeze(), (512, 512))
            cam_resized = cv2.resize(cam, (512, 512))
            overlay = self.generate_overlay(spatial_vis, cam_resized)
            overlay_uint8 = (overlay * 255).round().astype(np.uint8)
            pil_img = Image.fromarray(overlay_uint8)

            # --- Statutory Watermark (proportionally scaled in top-right corner) ---
            try:
                import os
                from PIL import ImageDraw, ImageFont

                img_w, img_h = pil_img.size
                lines = [
                    "For Research & Investigational Use Only",
                    "Not for Diagnostic Procedures"
                ]

                # Find available TrueType font for clean anti-aliased rendering
                font_path = None
                for p in [
                    "/usr/share/fonts/google-carlito-fonts/Carlito-Bold.ttf",
                    "/usr/share/fonts/adwaita-sans-fonts/AdwaitaSans-Regular.ttf"
                ]:
                    if os.path.exists(p):
                        font_path = p
                        break

                target_badge_w = int(img_w * 0.34)
                font = None
                if font_path:
                    for sz in range(max(9, int(img_w * 0.035)), 6, -1):
                        f = ImageFont.truetype(font_path, sz)
                        w = max(f.getbbox(l)[2] - f.getbbox(l)[0] for l in lines)
                        if w <= target_badge_w:
                            font = f
                            break
                if font is None:
                    font = ImageFont.load_default()

                # Calculate dimensions
                bboxes = [font.getbbox(l) for l in lines]
                max_text_w = max(b[2] - b[0] for b in bboxes)
                line_h = max(b[3] - b[1] for b in bboxes)
                line_spacing = max(1, int(line_h * 0.2))

                pad_x = max(5, int(img_w * 0.012))
                pad_y = max(3, int(img_h * 0.008))

                badge_w = max_text_w + 2 * pad_x
                badge_h = len(lines) * line_h + (len(lines) - 1) * line_spacing + 2 * pad_y

                margin = max(6, int(img_w * 0.015))
                x1 = img_w - margin
                x0 = x1 - badge_w
                y0 = margin
                y1 = y0 + badge_h

                # Semi-transparent dark pill box in top-right corner
                bg_overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
                bg_draw = ImageDraw.Draw(bg_overlay)
                radius = max(2, int(badge_h * 0.15))
                bg_draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=(0, 0, 0, 175))

                pil_rgba = pil_img.convert("RGBA")
                pil_rgba = Image.alpha_composite(pil_rgba, bg_overlay)
                text_draw = ImageDraw.Draw(pil_rgba)

                for i, line in enumerate(lines):
                    lx = x0 + pad_x
                    ly = y0 + pad_y + i * (line_h + line_spacing)
                    text_draw.text((lx, ly), line, fill=(255, 255, 240, 240), font=font)

                pil_img = pil_rgba.convert("RGB")
            except Exception as wm_err:
                self.logger.warning(f"Could not apply GradCAM watermark: {wm_err}")
            # --- End watermark ---

            buffer = BytesIO()
            pil_img.save(buffer, format='PNG')
            buffer.seek(0)

            # Encode to base64 and return as string
            gradcam_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            # Add metadata
            inference_time = time.time() - start_time
            results.update({
                "model_name": self.model_name,
                "inference_time": round(inference_time, 3),
                "device": self.device,
                "gradcam_base64": gradcam_base64,
                "status": "success"
            })
            
            self.logger.info(
                "analysis_completed",
                model_name=self.model_name,
                inference_time=inference_time,
                image_path=image_path
            )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "analysis_failed",
                model_name=self.model_name,
                error=str(e),
                image_path=image_path
            )
            # raise e
            return {
                "model_name": self.model_name,
                "status": "error",
                "error": str(e),
                "inference_time": round(time.time() - start_time, 3)
            }
    
    def _load_image(self, image_path: str) -> Image.Image:
        """Load and validate image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image
            
        Raises:
            ValueError: If image cannot be loaded
        """
        try:
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            return image
            
        except Exception as e:
            raise ValueError(f"Cannot load image {image_path}: {str(e)}")
