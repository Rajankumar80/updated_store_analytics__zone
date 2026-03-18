# # # # # import torch
# # # # # import torch.nn as nn
# # # # # from torchvision import transforms, models
# # # # # from PIL import Image
# # # # # import cv2

# # # # # class GenderClassifier:
# # # # #     def __init__(self, weights_path, device=None):
# # # # #         self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
# # # # #         self.model = models.mobilenet_v3_small()
# # # # #         in_features = self.model.classifier[3].in_features
# # # # #         self.model.classifier[3] = nn.Linear(in_features, 2)

# # # # #         state_dict = torch.load(weights_path, map_location=self.device)
# # # # #         self.model.load_state_dict(state_dict)
# # # # #         self.model.to(self.device).eval()

# # # # #         self.classes = ["F", "M"]
# # # # #         self.transform = transforms.Compose([
# # # # #             transforms.Resize((224, 224)),
# # # # #             transforms.ToTensor(),
# # # # #             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
# # # # #         ])

# # # # #     def predict(self, frame, boxes):
# # # # #         results = []
# # # # #         for box in boxes:
# # # # #             x1, y1, x2, y2 = map(int, box)
# # # # #             x1, y1 = max(0, x1), max(0, y1)
# # # # #             x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
# # # # #             crop = frame[y1:y2, x1:x2]
# # # # #             if crop.size == 0 or crop.shape[0] == 0 or crop.shape[1] == 0:
# # # # #                 results.append({"label": "?", "confidence": 0.0})
# # # # #                 continue
# # # # #             img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
# # # # #             img_t = self.transform(img).unsqueeze(0).to(self.device)
# # # # #             with torch.no_grad():
# # # # #                 output = self.model(img_t)
# # # # #                 prob = torch.softmax(output, dim=1)
# # # # #                 conf, pred = torch.max(prob, 1)
# # # # #             results.append({"label": self.classes[pred.item()], "confidence": float(conf.item())})
# # # # #         return results
# # # # # ------------------------------------new-------------------------
# # # # import torch
# # # # import torch.nn as nn
# # # # from torchvision import transforms, models
# # # # from PIL import Image
# # # # import cv2


# # # # class GenderClassifier:
# # # #     """
# # # #     MobileNetV3-Small binary classifier that predicts gender ("M" / "F")
# # # #     from cropped person bounding boxes.

# # # #     Usage
# # # #     -----
# # # #     clf = GenderClassifier("path/to/weights.pth")
# # # #     preds = clf.predict(bgr_frame, boxes_xyxy)
# # # #     # preds[i] → {"label": "M"|"F"|"?", "confidence": float}
# # # #     """

# # # #     CLASSES = ["F", "M"]   # index 0 = Female, 1 = Male

# # # #     def __init__(self, weights_path, device=None):
# # # #         self.device = device or torch.device(
# # # #             "cuda" if torch.cuda.is_available() else "cpu"
# # # #         )

# # # #         # ── Build model skeleton ──────────────────────────────────────────────
# # # #         self.model = models.mobilenet_v3_small()
# # # #         in_features = self.model.classifier[3].in_features
# # # #         self.model.classifier[3] = nn.Linear(in_features, len(self.CLASSES))

# # # #         # ── Load weights ──────────────────────────────────────────────────────
# # # #         state_dict = torch.load(weights_path, map_location=self.device)
# # # #         self.model.load_state_dict(state_dict)
# # # #         self.model.to(self.device).eval()

# # # #         # ── Inference pre-processing ──────────────────────────────────────────
# # # #         self.transform = transforms.Compose([
# # # #             transforms.Resize((224, 224)),
# # # #             transforms.ToTensor(),
# # # #             transforms.Normalize(
# # # #                 mean=[0.485, 0.456, 0.406],
# # # #                 std =[0.229, 0.224, 0.225],
# # # #             ),
# # # #         ])

# # # #     def predict(self, frame, boxes):
# # # #         """
# # # #         Run inference on a batch of bounding-box crops.

# # # #         Parameters
# # # #         ----------
# # # #         frame : np.ndarray
# # # #             Full BGR frame from OpenCV.
# # # #         boxes : array-like of shape (N, 4)
# # # #             Bounding boxes in [x1, y1, x2, y2] format (pixel coords).

# # # #         Returns
# # # #         -------
# # # #         list of dict
# # # #             One dict per box (same order as input), each containing:
# # # #                 "label"      : "M" | "F" | "?" (on invalid crop)
# # # #                 "confidence" : float in [0, 1]
# # # #         """
# # # #         results = []

# # # #         for box in boxes:
# # # #             x1, y1, x2, y2 = map(int, box)

# # # #             # Clamp to frame boundaries
# # # #             x1 = max(0, x1);  y1 = max(0, y1)
# # # #             x2 = min(frame.shape[1], x2);  y2 = min(frame.shape[0], y2)

# # # #             crop = frame[y1:y2, x1:x2]

# # # #             # Guard against degenerate / out-of-frame boxes
# # # #             if crop.size == 0 or crop.shape[0] < 2 or crop.shape[1] < 2:
# # # #                 results.append({"label": "?", "confidence": 0.0})
# # # #                 continue

# # # #             # BGR → RGB → PIL → tensor
# # # #             img   = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
# # # #             img_t = self.transform(img).unsqueeze(0).to(self.device)

# # # #             with torch.no_grad():
# # # #                 logits = self.model(img_t)
# # # #                 prob   = torch.softmax(logits, dim=1)
# # # #                 conf, pred = torch.max(prob, 1)

# # # #             results.append({
# # # #                 "label":      self.CLASSES[pred.item()],
# # # #                 "confidence": float(conf.item()),
# # # #             })

# # # #         return results
# # # # ------------------------optimized code-------------
# # # import torch
# # # import torch.nn as nn
# # # from torchvision import transforms, models
# # # from PIL import Image
# # # import cv2
# # # import numpy as np


# # # class GenderClassifier:
# # #     """
# # #     MobileNetV3-Small binary classifier with true batched inference.

# # #     All crops for a frame are stacked into a single tensor and run through
# # #     the network in one forward pass — eliminating the per-crop overhead of
# # #     the original loop.  On CUDA the model also runs in fp16.
# # #     """

# # #     CLASSES = ["F", "M"]

# # #     def __init__(self, weights_path, device=None):
# # #         self.device = device or torch.device(
# # #             "cuda" if torch.cuda.is_available() else "cpu"
# # #         )
# # #         self.use_fp16 = self.device.type == "cuda"

# # #         # ── Model ─────────────────────────────────────────────────────────────
# # #         self.model = models.mobilenet_v3_small()
# # #         in_features = self.model.classifier[3].in_features
# # #         self.model.classifier[3] = nn.Linear(in_features, len(self.CLASSES))

# # #         state_dict = torch.load(weights_path, map_location=self.device)
# # #         self.model.load_state_dict(state_dict)
# # #         self.model.to(self.device)
# # #         if self.use_fp16:
# # #             self.model.half()
# # #         self.model.eval()

# # #         # ── Pre-processing (CPU side) ─────────────────────────────────────────
# # #         self.transform = transforms.Compose([
# # #             transforms.Resize((224, 224)),
# # #             transforms.ToTensor(),
# # #             transforms.Normalize(
# # #                 mean=[0.485, 0.456, 0.406],
# # #                 std =[0.229, 0.224, 0.225],
# # #             ),
# # #         ])

# # #     # ── Internal helpers ──────────────────────────────────────────────────────

# # #     def _crop_to_tensor(self, frame, box):
# # #         """Crop one box from the frame and return a (3,224,224) float tensor."""
# # #         x1, y1, x2, y2 = map(int, box)
# # #         x1 = max(0, x1);  y1 = max(0, y1)
# # #         x2 = min(frame.shape[1], x2);  y2 = min(frame.shape[0], y2)
# # #         crop = frame[y1:y2, x1:x2]
# # #         if crop.size == 0 or crop.shape[0] < 2 or crop.shape[1] < 2:
# # #             return None
# # #         img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
# # #         return self.transform(img)   # (3, 224, 224) float32 CPU tensor

# # #     # ── Public API ────────────────────────────────────────────────────────────

# # #     def predict(self, frame, boxes):
# # #         """
# # #         Batch-infer gender for all boxes in one GPU forward pass.

# # #         Parameters
# # #         ----------
# # #         frame : np.ndarray  — full BGR frame
# # #         boxes : (N, 4)      — xyxy pixel boxes

# # #         Returns
# # #         -------
# # #         list[dict]  — [{"label": "M"|"F"|"?", "confidence": float}, ...]
# # #                        same length and order as `boxes`
# # #         """
# # #         if len(boxes) == 0:
# # #             return []

# # #         tensors = []
# # #         valid   = []   # (original_index, tensor)

# # #         for i, box in enumerate(boxes):
# # #             t = self._crop_to_tensor(frame, box)
# # #             if t is not None:
# # #                 valid.append(i)
# # #                 tensors.append(t)

# # #         # Pre-fill with fallback results
# # #         results = [{"label": "?", "confidence": 0.0}] * len(boxes)

# # #         if not tensors:
# # #             return results

# # #         # Stack → single forward pass
# # #         batch = torch.stack(tensors).to(self.device)  # (N, 3, 224, 224)
# # #         if self.use_fp16:
# # #             batch = batch.half()

# # #         with torch.no_grad():
# # #             logits = self.model(batch)                 # (N, 2)
# # #             probs  = torch.softmax(logits.float(), dim=1)
# # #             confs, preds = torch.max(probs, dim=1)

# # #         for out_idx, orig_idx in enumerate(valid):
# # #             results[orig_idx] = {
# # #                 "label":      self.CLASSES[preds[out_idx].item()],
# # #                 "confidence": float(confs[out_idx].item()),
# # #             }

# # #         return results
# # # ----------NEW3-----------------------
# # import torch
# # import torch.nn as nn
# # from torchvision import transforms, models
# # from PIL import Image
# # import cv2


# # class GenderClassifier:
# #     """
# #     MobileNetV3-Small binary classifier.
# #     Runs on a dedicated CUDA stream so it doesn't block YOLO's stream.
# #     """

# #     CLASSES = ["F", "M"]

# #     def __init__(self, weights_path, device=None):
# #         self.device   = device or torch.device(
# #             "cuda" if torch.cuda.is_available() else "cpu"
# #         )
# #         self.use_fp16 = self.device.type == "cuda"

# #         # Dedicated CUDA stream — overlaps with YOLO's default stream
# #         self.stream = (
# #             torch.cuda.Stream(device=self.device)
# #             if self.device.type == "cuda"
# #             else None
# #         )

# #         self.model = models.mobilenet_v3_small()
# #         in_features = self.model.classifier[3].in_features
# #         self.model.classifier[3] = nn.Linear(in_features, len(self.CLASSES))
# #         state_dict = torch.load(weights_path, map_location=self.device)
# #         self.model.load_state_dict(state_dict)
# #         self.model.to(self.device)
# #         if self.use_fp16:
# #             self.model.half()
# #         self.model.eval()

# #         self.transform = transforms.Compose([
# #             transforms.Resize((224, 224)),
# #             transforms.ToTensor(),
# #             transforms.Normalize(
# #                 mean=[0.485, 0.456, 0.406],
# #                 std =[0.229, 0.224, 0.225],
# #             ),
# #         ])

# #     def _crop_to_tensor(self, frame, box):
# #         x1, y1, x2, y2 = map(int, box)
# #         x1 = max(0, x1);  y1 = max(0, y1)
# #         x2 = min(frame.shape[1], x2);  y2 = min(frame.shape[0], y2)
# #         crop = frame[y1:y2, x1:x2]
# #         if crop.size == 0 or crop.shape[0] < 2 or crop.shape[1] < 2:
# #             return None
# #         return self.transform(
# #             Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
# #         )

# #     def predict(self, frame, boxes):
# #         """
# #         Single batched forward pass for all boxes.
# #         Returns list[{"label", "confidence"}] in same order as boxes.
# #         """
# #         if len(boxes) == 0:
# #             return []

# #         tensors, valid = [], []
# #         for i, box in enumerate(boxes):
# #             t = self._crop_to_tensor(frame, box)
# #             if t is not None:
# #                 valid.append(i)
# #                 tensors.append(t)

# #         results = [{"label": "?", "confidence": 0.0}] * len(boxes)
# #         if not tensors:
# #             return results

# #         ctx = (
# #             torch.cuda.stream(self.stream)
# #             if self.stream is not None
# #             else torch.no_grad()
# #         )
# #         with ctx:
# #             with torch.no_grad():
# #                 batch = torch.stack(tensors).to(self.device)
# #                 if self.use_fp16:
# #                     batch = batch.half()
# #                 logits = self.model(batch)
# #                 probs  = torch.softmax(logits.float(), dim=1)
# #                 confs, preds = torch.max(probs, dim=1)

# #         if self.stream is not None:
# #             self.stream.synchronize()

# #         for out_i, orig_i in enumerate(valid):
# #             results[orig_i] = {
# #                 "label":      self.CLASSES[preds[out_i].item()],
# #                 "confidence": float(confs[out_i].item()),
# #             }
# #         return results
# # -----------------new4------------------------------
# import torch
# import torch.nn as nn
# from torchvision import transforms, models
# from PIL import Image
# import cv2


# class GenderClassifier:
#     """
#     MobileNetV3-Small binary classifier.
#     Runs on a dedicated CUDA stream so it doesn't block YOLO's stream.
#     """

#     CLASSES = ["F", "M"]

#     def __init__(self, weights_path, device=None):
#         self.device   = device or torch.device(
#             "cuda" if torch.cuda.is_available() else "cpu"
#         )
#         self.use_fp16 = self.device.type == "cuda"

#         # Dedicated CUDA stream — overlaps with YOLO's default stream
#         self.stream = (
#             torch.cuda.Stream(device=self.device)
#             if self.device.type == "cuda"
#             else None
#         )

#         self.model = models.mobilenet_v3_small()
#         in_features = self.model.classifier[3].in_features
#         self.model.classifier[3] = nn.Linear(in_features, len(self.CLASSES))
#         state_dict = torch.load(weights_path, map_location=self.device)
#         self.model.load_state_dict(state_dict)
#         self.model.to(self.device)
#         if self.use_fp16:
#             self.model.half()
#         self.model.eval()

#         self.transform = transforms.Compose([
#             transforms.Resize((224, 224)),
#             transforms.ToTensor(),
#             transforms.Normalize(
#                 mean=[0.485, 0.456, 0.406],
#                 std =[0.229, 0.224, 0.225],
#             ),
#         ])

#     def _crop_to_tensor(self, frame, box):
#         x1, y1, x2, y2 = map(int, box)
#         x1 = max(0, x1);  y1 = max(0, y1)
#         x2 = min(frame.shape[1], x2);  y2 = min(frame.shape[0], y2)
#         crop = frame[y1:y2, x1:x2]
#         if crop.size == 0 or crop.shape[0] < 2 or crop.shape[1] < 2:
#             return None
#         return self.transform(
#             Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
#         )

#     def predict(self, frame, boxes):
#         """
#         Single batched forward pass for all boxes.
#         Returns list[{"label", "confidence"}] in same order as boxes.
#         """
#         if len(boxes) == 0:
#             return []

#         tensors, valid = [], []
#         for i, box in enumerate(boxes):
#             t = self._crop_to_tensor(frame, box)
#             if t is not None:
#                 valid.append(i)
#                 tensors.append(t)

#         results = [{"label": "?", "confidence": 0.0}] * len(boxes)
#         if not tensors:
#             return results

#         ctx = (
#             torch.cuda.stream(self.stream)
#             if self.stream is not None
#             else torch.no_grad()
#         )
#         with ctx:
#             with torch.no_grad():
#                 batch = torch.stack(tensors).to(self.device)
#                 if self.use_fp16:
#                     batch = batch.half()
#                 logits = self.model(batch)
#                 probs  = torch.softmax(logits.float(), dim=1)
#                 confs, preds = torch.max(probs, dim=1)

#         if self.stream is not None:
#             self.stream.synchronize()

#         for out_i, orig_i in enumerate(valid):
#             results[orig_i] = {
#                 "label":      self.CLASSES[preds[out_i].item()],
#                 "confidence": float(confs[out_i].item()),
#             }
#         return results
# -------------new5-------------------------------------------
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import cv2


class GenderClassifier:
    """
    MobileNetV3-Small binary classifier.
    All crops for a frame are batched into one GPU forward pass.
    Runs on a dedicated CUDA stream so it does not block YOLO's default stream.
    """

    CLASSES = ["F", "M"]

    def __init__(self, weights_path, device=None):
        self.device   = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.use_fp16 = self.device.type == "cuda"

        # Dedicated CUDA stream — GPU work here overlaps with YOLO's stream
        self.stream = (
            torch.cuda.Stream(device=self.device)
            if self.device.type == "cuda"
            else None
        )

        # Build model and load weights
        self.model = models.mobilenet_v3_small()
        in_features = self.model.classifier[3].in_features
        self.model.classifier[3] = nn.Linear(in_features, len(self.CLASSES))

        # weights_only=True: safe loading, no arbitrary code execution
        state_dict = torch.load(
            weights_path, map_location=self.device, weights_only=True
        )
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        if self.use_fp16:
            self.model.half()
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std =[0.229, 0.224, 0.225],
            ),
        ])

    def _crop_to_tensor(self, frame, box):
        """Crop one bounding box from the frame and return a float32 tensor, or None."""
        x1, y1, x2, y2 = map(int, box)
        x1 = max(0, x1);  y1 = max(0, y1)
        x2 = min(frame.shape[1], x2);  y2 = min(frame.shape[0], y2)
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0 or crop.shape[0] < 2 or crop.shape[1] < 2:
            return None
        return self.transform(
            Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        )

    def predict(self, frame, boxes):
        """
        Run a single batched forward pass for all boxes.

        Parameters
        ----------
        frame : np.ndarray  full BGR frame
        boxes : (N, 4)      xyxy pixel boxes

        Returns
        -------
        list[dict]  one {"label": str, "confidence": float} per box,
                    same order as input; invalid crops return label="?"
        """
        if len(boxes) == 0:
            return []

        # Build tensor list — track which original indices are valid
        tensors, valid = [], []
        for i, box in enumerate(boxes):
            t = self._crop_to_tensor(frame, box)
            if t is not None:
                valid.append(i)
                tensors.append(t)

        # Pre-fill with fallback for invalid crops (list comprehension = independent dicts)
        results = [{"label": "?", "confidence": 0.0} for _ in range(len(boxes))]
        if not tensors:
            return results

        # Single forward pass on dedicated CUDA stream
        ctx = (
            torch.cuda.stream(self.stream)
            if self.stream is not None
            else torch.no_grad()
        )
        with ctx:
            with torch.no_grad():
                batch = torch.stack(tensors).to(self.device)
                if self.use_fp16:
                    batch = batch.half()
                logits = self.model(batch)
                probs  = torch.softmax(logits.float(), dim=1)
                confs, preds = torch.max(probs, dim=1)

        # Synchronise before reading results back to CPU
        if self.stream is not None:
            self.stream.synchronize()

        for out_i, orig_i in enumerate(valid):
            results[orig_i] = {
                "label":      self.CLASSES[preds[out_i].item()],
                "confidence": float(confs[out_i].item()),
            }
        return results