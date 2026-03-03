"""Knee X-ray authenticity and arthritis classification model."""

# import random
from torch.nn import functional as F
from typing import Any, Dict
import torch
import torch.nn as nn
from PIL import Image
# import torchvision.transforms as transforms

from .base import BaseModel

import numpy as np
from torchvision.models import convnext_tiny, ConvNeXt_Tiny_Weights
import cv2

class DualDomainFusionModule(nn.Module):
    def __init__(self, in_channels=768):
        super().__init__()
        self.spatial_weight = nn.Parameter(torch.tensor(0.5))
        self.freq_weight = nn.Parameter(torch.tensor(0.5))
        self.cross_attn = nn.MultiheadAttention(
            embed_dim=in_channels, num_heads=4, dropout=0.1, batch_first=True
        )
        self.refine = nn.Sequential(
            nn.Linear(in_channels, in_channels),
            nn.LayerNorm(in_channels),
            nn.GELU()
        )
    
    def forward(self, feat):
        spatial_w = torch.sigmoid(self.spatial_weight)
        freq_w = torch.sigmoid(self.freq_weight)
        total = spatial_w + freq_w
        spatial_w, freq_w = spatial_w / total, freq_w / total
        
        feat_expanded = feat.unsqueeze(1)
        attn_out, _ = self.cross_attn(feat_expanded, feat_expanded, feat_expanded)
        attn_out = attn_out.squeeze(1)
        
        fused = feat + 0.2 * attn_out
        fused = self.refine(fused)
        
        return fused, {'spatial': spatial_w.item(), 'frequency': freq_w.item()}


class MultiTaskDualDomainDetector(nn.Module):
    def __init__(self, freeze_backbone=True, dropout=0.4, num_kl_classes=5):
        super().__init__()
        
        weights = ConvNeXt_Tiny_Weights.IMAGENET1K_V1
        self.backbone = convnext_tiny(weights=weights)
        
        orig_conv = self.backbone.features[0][0]        # pyright: ignore[reportIndexIssue]
        self.backbone.features[0][0] = nn.Conv2d(       # pyright: ignore[reportIndexIssue]
            2, orig_conv.out_channels,                  # pyright: ignore[reportArgumentType]
            kernel_size=orig_conv.kernel_size,          # pyright: ignore[reportArgumentType]
            stride=orig_conv.stride,                    # pyright: ignore[reportArgumentType]
            padding=orig_conv.padding,                  # pyright: ignore[reportArgumentType]
            bias=False
        )
        
        with torch.no_grad():
            pretrained = orig_conv.weight[:, :3, :, :].mean(dim=1, keepdim=True) # pyright: ignore[reportIndexIssue]
            self.backbone.features[0][0].weight.copy_(pretrained.repeat(1, 2, 1, 1)) # pyright: ignore[reportCallIssue, reportIndexIssue]
        
        self.backbone.classifier = nn.Identity() # pyright: ignore[reportAttributeAccessIssue]
        
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
            for param in self.backbone.features[-1].parameters():
                param.requires_grad = True
        
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.fusion = DualDomainFusionModule(in_channels=768)
        
        self.fake_head = nn.Sequential(
            nn.Linear(768, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout * 0.5),
            nn.Linear(64, 1)
        )
        
        self.kl_head = nn.Sequential(
            nn.Linear(768, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, num_kl_classes)
        )
    
    def forward(self, spatial, freq) -> tuple[torch.Tensor, torch.Tensor]:
        x = torch.cat([spatial, freq], dim=1)
        feat_map = self.backbone(x)
        feat_vec = self.gap(feat_map).flatten(1)
        fused_feat, domain_weights = self.fusion(feat_vec)
        
        fake_logits = self.fake_head(fused_feat).squeeze(1)
        kl_logits = self.kl_head(fused_feat)
        
        return fake_logits, kl_logits

class KneeXRayModel(BaseModel):
    """Mock model for knee X-ray authenticity detection and arthritis classification."""
    
    def __init__(self, device: str = "cpu"):
        """Initialize knee X-ray model."""
        super().__init__("knee_xray_model", device)
        
        # Define arthritis severity labels
        # self.arthritis_labels = [
        #     "Normal",
        #     "Mild",
        #     "Moderate", 
        #     "Severe"
        # ]
    
    def load_model(self, model_path: str) -> None:
        """Load model from checkpoint.
        
        Args:
            model_path: Path to model checkpoint
            
        Note:
            This is a mock implementation. Replace with actual model loading:
            ```python
            self.model = torch.load(model_path, map_location=self.device)
            self.model.eval()
            ```
        """
        self.logger.info(f"Loading model from {model_path}")
        
        # Create a simple mock model for demonstration
        self.model = MultiTaskDualDomainDetector()
        self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
        self.model.to(self.device)
        self.model.eval()
        
        self.gradients = None
        self.activations = None

        target_layer = self.model.backbone.features[-1]
        target_layer.register_forward_hook(self.save_activation)
        target_layer.register_full_backward_hook(self.save_gradient)

        self.logger.info("Model loaded successfully")

    def save_activation(self, module, input, output):
        self.activations = output.detach()

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    @staticmethod
    def _compute_fft_features(img):
        """Compute log-magnitude FFT for frequency domain analysis"""
        fft = np.fft.fft2(img)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        log_magnitude = np.log(magnitude + 1)
        return log_magnitude

    def preprocess(self, image: Image.Image) -> tuple[torch.Tensor, ...]:
        """Preprocess X-ray image.
        
        Args:
            image: PIL Image of X-ray
            
        Returns:
            Preprocessed tensor
        """
        
        # Load image
        image = image.convert('L')
        np_image = np.array(image)
        
        # Resize
        img = cv2.resize(np_image, (224, 224))
        
        # === FREQUENCY DOMAIN FEATURES ===
        freq = self._compute_fft_features(img)
        
        # Normalize
        img = img / 255.0
        freq = freq / (freq.max() + 1e-8)
        
        # To tensor
        img = torch.tensor(img, dtype=torch.float32).unsqueeze(0).unsqueeze(0)  # [1, H, W]
        freq = torch.tensor(freq, dtype=torch.float32).unsqueeze(0).unsqueeze(0)  # [1, H, W]
        
        return img, freq

    def predict(self, input_tensors: tuple[torch.Tensor, ...]) -> tuple[torch.Tensor, torch.Tensor]:
        """Run model inference.
        
        Args:
            input_tensor: Preprocessed input tensor
            
        Returns:
            Model output tensor
        """
        self.model.zero_grad()
        # with torch.no_grad():
        authenticity_logits, arthritis_logits = self.model(*input_tensors)

        # return torch.cat([authenticity_logits, arthritis_logits], dim=1)
        return authenticity_logits, arthritis_logits

    def postprocess(self, output: tuple[torch.Tensor, ...]) -> tuple[Dict[str, Any], np.ndarray]:
        """Postprocess model output.
        
        Args:
            output: Raw model output [authenticity_logit, arthritis_logits...]
            
        Returns:
            Processed results dictionary
        """
        # Split outputs
        authenticity_logit = output[0]
        arthritis_logits = output[1]
        # authenticity_logit = output
        
        # Convert to probabilities
        authenticity_prob = torch.sigmoid(authenticity_logit).item()

        arthritis_probs = torch.softmax(arthritis_logits, dim=0)
        arthritis_pred_class = arthritis_logits.argmax(dim=1)
        arthritis_confidence = arthritis_probs[0, arthritis_pred_class].item()

        score = authenticity_logit
        score.backward()

        # Grad-CAM++: Alpha weighting
        gradients = self.gradients
        activations = self.activations

        alpha = gradients.pow(2)
        alpha = alpha / (2 * alpha + (activations * gradients.pow(3)).sum(dim=(2,3), keepdim=True) + 1e-8)
        weights = (alpha * F.relu(gradients)).sum(dim=(2,3), keepdim=True)

        cam = (weights * activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam).squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        # return cam, pred_class.item(), confidence

        # Determine authenticity (real if prob < 0.5)
        is_real = authenticity_prob <= 0.5
        confidence = authenticity_prob if authenticity_prob > 0.5 else 1 - authenticity_prob #max(authenticity_prob, 1 - authenticity_prob)
        
        # Build results
        results = {
            "authenticity": {
                "is_real": is_real,
                "confidence": round(confidence, 3),
            },
            "scan_type": "XRAY"
        }
        
        # Add arthritis classification if image is real
        if is_real:
            arthritis_class = f"{(int(arthritis_pred_class.item())/5) * 100}%"
            # arthritis_confidence = float(arthritis_probs[arthritis_class])
            
            results["arthritis"] = {
                "severity": arthritis_class,
                "confidence": round(arthritis_confidence, 3)
                # "probabilities": {
                #     label: round(float(prob), 3)
                #     for label, prob in zip(self.arthritis_labels, arthritis_probs)
                # }
            }

        return results, cam
