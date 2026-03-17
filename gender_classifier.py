import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import cv2

class GenderClassifier:
    def __init__(self, weights_path, device=None):
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.mobilenet_v3_small()
        in_features = self.model.classifier[3].in_features
        self.model.classifier[3] = nn.Linear(in_features, 2)

        state_dict = torch.load(weights_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device).eval()

        self.classes = ["F", "M"]
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, frame, boxes):
        results = []
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0 or crop.shape[0] == 0 or crop.shape[1] == 0:
                results.append({"label": "?", "confidence": 0.0})
                continue
            img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
            img_t = self.transform(img).unsqueeze(0).to(self.device)
            with torch.no_grad():
                output = self.model(img_t)
                prob = torch.softmax(output, dim=1)
                conf, pred = torch.max(prob, 1)
            results.append({"label": self.classes[pred.item()], "confidence": float(conf.item())})
        return results