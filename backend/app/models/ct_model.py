"""CT scan authenticity detection model."""

import torch
import torch.nn as nn
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as models
from typing import Any, Dict

from .base import BaseModel

import cv2
import numpy as np
import skimage.transform as skimg_transform


def resnet18_1ch(pretrained=True):
    model = models.resnet18(weights="IMAGENET1K_V1" if pretrained else None)
    w = model.conv1.weight
    model.conv1 = nn.Conv2d(
        1, 64, kernel_size=7, stride=2, padding=3, bias=False
    )
    model.conv1.weight.data = w.mean(dim=1, keepdim=True)

    return model

def densenet121_1ch(pretrained=True):
    model = models.densenet121(weights="IMAGENET1K_V1" if pretrained else None)
    w = model.features.conv0.weight # pyright: ignore[reportAttributeAccessIssue]
    model.features.conv0 = nn.Conv2d(
        1, 64, kernel_size=7, stride=2, padding=3, bias=False
    )
    model.features.conv0.weight.data = w.mean(dim=1, keepdim=True) # pyright: ignore[reportCallIssue]
    
    return model

class HybridCTNet(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()

        self.spatial = densenet121_1ch(pretrained=True)
        self.srm = resnet18_1ch(pretrained=True)
        self.radon = resnet18_1ch(pretrained=True)

        self.spatial_feat_dim = 1024
        self.sec_feat_dim = 512
        self.spatial.classifier = nn.Identity()
        
        self.radon.fc = nn.Identity()
        self.srm.fc = nn.Identity()        

        self.fusion = nn.Sequential(
            nn.Linear(self.spatial_feat_dim + self.sec_feat_dim*2, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x_spatial, x_srm, x_radon, ablate=None):
        f_spatial = self.spatial(x_spatial)
        f_srm = self.srm(x_srm)
        f_radon = self.radon(x_radon)

        # ablation
        if ablate is None:
            f = torch.cat([f_spatial, f_srm, f_radon], dim=1)
            out = self.fusion(f)
            return out
            
        # if "radon" in ablate:
        #     f_radon = torch.zeros_like(f_radon)
        # if "ct" in ablate:
        #     f_spatial = torch.zeros_like(f_spatial)
        # if "srm" in ablate:
        #     f_srm = torch.zeros_like(f_srm)
        
        f = torch.cat([f_spatial, f_srm, f_radon], dim=1)
        out = self.fusion(f)

        return out

def normalize_0_255(data):
    """Utility to normalize any 2D array to 0-255 uint8"""
    data = data.astype(np.float32)
    min_val, max_val = data.min(), data.max()
    norm = (data - min_val) / (max_val - min_val + 1e-8)
    return (norm * 255).astype(np.uint8)

class CTScanModel(BaseModel):
    """Mock model for CT scan authenticity detection."""
    
    def __init__(self, device: str = "cpu"):
        """Initialize CT scan model."""
        super().__init__("ct_scan_model", device)
        
        # Image preprocessing pipeline for CT scans
        self.transform = self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.ConvertImageDtype(torch.float),
            #transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

        self.classes = ("REMOVED", "REAL", "INJECTED")
    
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
        self.logger.info(f"Loading CT model from {model_path}")
        
        # Create a simple mock model for demonstration
        self.model = HybridCTNet()
        self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
        self.model = self.model.to(self.device) 
        
        self.model.eval()
        self.logger.info("CT model loaded successfully")

    def generate_radon(self, image: np.ndarray):
        theta = np.linspace(0.0, 180.0, max(image.shape), endpoint=False)
        sinogram = skimg_transform.radon(image, theta=theta)
        image_radon = cv2.resize(normalize_0_255(sinogram), (299, 299))

        return image_radon
    
    def get_srm_residual(self, img: np.ndarray):
        # This 3x3 high-pass filter is a standard SRM (Spatial Rich Model) kernel
        # used in forensics to strip away image content and leave noise fingerprints.
        kernel = np.array([[-1, -1, -1],
                        [-1,  8, -1],
                        [-1, -1, -1]])
        res = cv2.filter2D(img.astype(np.float32), -1, kernel)
        return normalize_0_255(np.abs(res))
    
    def preprocess(self, image: Image.Image) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Preprocess CT scan image.
        
        Args:
            image: PIL Image of CT scan
            
        Returns:
            Preprocessed tensor
        """
        image = image.convert('L')
        np_image = np.array(image)
        np_image = cv2.resize((np_image), (299, 299), interpolation=cv2.INTER_LANCZOS4)


        # Apply transforms
        image_srm = self.get_srm_residual(np_image)
        image_radon = self.generate_radon(np_image)

        # converting to tensor and adding batch info
        tensor = self.transform(np_image).unsqueeze(0).to(self.device) # pyright: ignore[reportAttributeAccessIssue]
        tensor_srm = self.transform(image_srm).unsqueeze(0).to(self.device) # pyright: ignore[reportAttributeAccessIssue]
        tensor_radon = self.transform(image_radon).unsqueeze(0).to(self.device) # pyright: ignore[reportAttributeAccessIssue]
        
        return tensor, tensor_srm, tensor_radon
    
    def predict(self, input_tensors: tuple[torch.Tensor, ...]) -> torch.Tensor:
        """Run model inference.
        
        Args:
            input_tensor: Preprocessed input tensor
            
        Returns:
            Model output tensor
        """
        with torch.no_grad():
            # Mock inference with some randomness
            output = self.model(*input_tensors)
            return output
    
    def postprocess(self, output: torch.Tensor) -> Dict[str, Any]:
        """Postprocess model output.
        
        Args:
            output: Raw model output [authenticity_logit]
            
        Returns:
            Processed results dictionary
        """
        # Convert logit to probability
        idx2label = ["Deepfake - Removed", "Real", "Deepfake - Injected"]

        preds = output.argmax(dim=1)
        probs = torch.softmax(output, dim=1)
        confidence = probs[0, preds].item()

        pred_output = preds[0].item()
        # pred_string = idx2label[pred_output] # pyright: ignore[reportArgumentType, reportCallIssue]
        
        # Determine authenticity (real if prob > 0.5)
        is_real = pred_output == 1
        
        results = {
            "authenticity": {
                "is_real": is_real,
                "confidence": round(confidence, 3),
                "removed_injected": idx2label[pred_output] # pyright: ignore[reportArgumentType, reportCallIssue] 
            },
            "scan_type": "CT",
        }
        
        return results
