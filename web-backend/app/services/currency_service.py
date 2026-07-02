import os
import uuid
import logging
import cv2
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.repositories.currency_repository import CurrencyRepository
from app.ai.preprocess import preprocess_image
from app.ai.inference import CurrencyInference
from app.ai.explain import generate_explanation

logger = logging.getLogger(__name__)

class CurrencyService:
    def __init__(self, repository: CurrencyRepository = None):
        self.repository = repository or CurrencyRepository()
        self.inference = CurrencyInference()
        
        # 1. Initialize local ORB detector and matcher
        self.orb = cv2.ORB_create(nfeatures=1000)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # 2. Find and load reference template banknote descriptor
        self.template_path = self._find_template_image()
        self.des_temp = None
        
        if self.template_path and self.template_path.exists():
            try:
                img_template = cv2.imread(str(self.template_path), cv2.IMREAD_GRAYSCALE)
                if img_template is not None:
                    _, self.des_temp = self.orb.detectAndCompute(img_template, None)
                    logger.info(f"Initialized local ORB validation template: {self.template_path.name}")
            except Exception as e:
                logger.error(f"Failed to extract descriptors for banknote template: {e}")
        else:
            logger.warning("Genuine reference banknote template could not be located in datasets.")

    def _find_template_image(self) -> Path:
        """Helper to find any genuine banknote image inside the project datasets to act as reference template."""
        # 1. Get base path relative to this file
        try:
            file_base = Path(__file__).resolve().parent.parent.parent.parent
        except Exception:
            file_base = Path.cwd()
            
        # 2. Get base path relative to current working directory
        cwd_base = Path.cwd()
        
        # Search targets
        search_bases = [file_base, cwd_base]
        valid_exts = {".jpg", ".jpeg", ".png"}
        
        for base in search_bases:
            search_dirs = [
                base / "datasets" / "raw" / "currency500_real_fake" / "real",
                base / "datasets" / "processed" / "train" / "real",
                base / "datasets" / "processed" / "validate" / "real",
                base / "datasets" / "processed" / "test" / "real"
            ]
            for directory in search_dirs:
                if directory.exists():
                    for p in directory.rglob("*"):
                        if p.is_file() and p.suffix.lower() in valid_exts:
                            return p
        return None

    def _is_banknote(self, file_path: Path) -> bool:
        """
        Runs local ORB keypoint matching to verify if the image contains a currency note.
        Does not require external APIs or internet connection.
        """
        if self.des_temp is None:
            logger.warning("Banknote reference descriptors are empty. Bypassing domain check.")
            return True

        try:
            # 1. Read input image in grayscale
            img = cv2.imread(str(file_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                return False

            # 2. Extract ORB descriptors
            _, des_img = self.orb.detectAndCompute(img, None)
            if des_img is None:
                return False

            # 3. Match against reference template descriptors
            matches = self.bf.match(self.des_temp, des_img)
            
            # 4. Filter high-quality matches
            good_matches = [m for m in matches if m.distance < 45]
            match_count = len(good_matches)
            
            logger.info(f"Local domain check matching keypoints: {match_count} found.")
            return match_count >= 12
        except Exception as e:
            logger.warning(f"Local domain validation check failed: {e}. Defaulting to True.")
            return True

    def analyze_banknote(self, upload_file: UploadFile) -> dict:
        """
        Orchestrates the banknote analysis pipeline:
        1. Saves the upload file temporarily.
        2. Performs local OpenCV domain validation check (is it a banknote?).
        3. Preprocesses the image (read, validate, resize, normalize).
        4. Invokes inference to get prediction status.
        5. Invokes explain module to obtain features and recommendations.
        6. Deletes the temporary file from disk ONLY IF genuine.
        """
        temp_path = None
        keep_temp = False
        try:
            # 1. Save uploaded file to temp directory
            temp_path = self.repository.save_temp_file(upload_file)
            
            # 2. Perform domain validation
            if not self._is_banknote(temp_path):
                raise ValueError("The uploaded image does not appear to contain a valid banknote. Please capture or upload a clear photo of a ₹500 currency note.")

            # 3. Run image preprocessing
            normalized_img = preprocess_image(temp_path)
            
            # 4. Model classification and confidence evaluation
            prediction_res = self.inference.predict(normalized_img)
            prediction = prediction_res["prediction"]
            confidence = prediction_res["confidence"]
            
            # 5. Generate static features list and RBI explanations
            explanation_res = generate_explanation(prediction)
            
            # 6. Determine canReport (only Counterfeit notes can be reported)
            can_report = bool(prediction == "Counterfeit")
            
            # If counterfeit, we keep the temp file so the user can submit a report.
            # If genuine, we mark it to be deleted in the finally block.
            keep_temp = can_report

            scan_id = f"SCN-{uuid.uuid4().hex[:8].upper()}"
            
            # Format the image path relative to the workspace root
            relative_image_path = str(temp_path.resolve().relative_to(Path.cwd().resolve())).replace("\\", "/")

            result = {
                "prediction": prediction,
                "confidence": confidence,
                "explanation": explanation_res["explanation"],
                "detectedFeatures": explanation_res["detectedFeatures"],
                "canReport": can_report,
                "scanId": scan_id,
                "imagePath": relative_image_path
            }
            return result
        except ValueError as val_err:
            logger.error(f"Validation error processing note image: {val_err}")
            raise HTTPException(status_code=400, detail=str(val_err))
        except Exception as e:
            logger.error(f"Internal error processing note image: {e}")
            raise HTTPException(status_code=500, detail=f"Inference processing failed: {str(e)}")
        finally:
            # Delete temporary file immediately IF the image is genuine (not kept)
            if temp_path and not keep_temp:
                self.repository.delete_temp_file(temp_path)

    def create_local_report(self, scan_id: str, image_path_str: str, prediction: str, confidence: float) -> dict:
        """
        Submits a local report based on a counterfeit banknote audit.
        """
        try:
            report_id = self.repository.save_local_report(scan_id, image_path_str, prediction, confidence)
            return {
                "status": "success",
                "reportId": report_id,
                "savedLocally": True
            }
        except FileNotFoundError as fnf:
            logger.error(f"Failed to find reported image: {fnf}")
            raise HTTPException(status_code=400, detail=str(fnf))
        except Exception as e:
            logger.error(f"Failed to write local report file: {e}")
            raise HTTPException(status_code=500, detail=f"Could not save local report: {str(e)}")
