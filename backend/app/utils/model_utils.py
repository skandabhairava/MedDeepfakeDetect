from torch.nn import functional as F
import torch
import cv2
import numpy as np
from PIL import Image

class GradCAMPlusPlus:
    """Improved Grad-CAM with weighted gradients"""
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        target_layer.register_forward_hook(self.save_activation)
        target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output.detach()

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate_cam(self, model_inps) -> tuple[np.ndarray, int, float]:
        self.model.eval()
        self.model.zero_grad()

        logits, _ = self.model(*model_inps)
        pred_class = logits.argmax(dim=1)
        probs = torch.softmax(logits, dim=1)
        confidence = probs[0, pred_class].item()

        score = logits[0, pred_class]
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
        return cam, pred_class.item(), confidence
    
    def generate_overlay(self, spatial_np, cam2_resized) -> np.ndarray:
        heatmap = cv2.applyColorMap(np.uint8(255 * cam2_resized), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB) / 255.0
        overlay = np.clip(0.6 * spatial_np[..., None] + 0.4 * heatmap, 0, 1)
        return overlay
    
    def generate_overlay_complete(self, spatial: torch.Tensor, model_inps, img_size, device):
        spatial_vis = spatial.unsqueeze(0).to(device)
        
        cam, pred_class, confidence = self.generate_cam(model_inps)
        cam_resized = cv2.resize(cam, (img_size, img_size))

        overlay = self.generate_overlay(spatial_vis, cam_resized)
        overlay_uint8 = (overlay * 255).round().astype(np.uint8)
        pil_img = Image.fromarray(overlay_uint8)

        return pred_class, confidence, pil_img

