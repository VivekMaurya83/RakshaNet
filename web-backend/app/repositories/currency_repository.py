import os
import shutil
import logging
import time
import json
from pathlib import Path
from fastapi import UploadFile

logger = logging.getLogger(__name__)

class CurrencyRepository:
    def __init__(self, upload_dir: str = "temp_uploads"):
        self.upload_dir = Path(upload_dir)
        # Ensure temporary upload directory exists in the workspace
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_temp_file(self, upload_file: UploadFile) -> Path:
        """
        Saves the UploadFile binary to the temporary uploads directory.
        """
        # Reset file pointer to beginning just in case
        upload_file.file.seek(0)
        
        # Create a unique filename if necessary, or keep original name prefix
        temp_file_path = self.upload_dir / f"temp_{upload_file.filename}"
        
        logger.info(f"Saving temporary file: {temp_file_path}")
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        return temp_file_path

    def delete_temp_file(self, file_path: Path) -> None:
        """
        Deletes a temporary file from the disk.
        """
        try:
            if file_path.exists():
                logger.info(f"Deleting temporary file: {file_path}")
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Failed to delete temporary file {file_path}: {e}")

    def save_local_report(self, scan_id: str, image_path_str: str, prediction: str, confidence: float) -> str:
        """
        Copies the temporary uploaded image to the local reported images directory
        and saves a local report JSON file in the reports/ directory.
        
        Args:
            scan_id: Unique identification code of the currency scan.
            image_path_str: Path to the temporary uploaded image.
            prediction: Model classification result.
            confidence: Inference confidence score percentage.
            
        Returns:
            The generated unique report ID.
        """
        # 1. Setup local reports directories in workspace
        reports_dir = Path("reports")
        images_dir = reports_dir / "images"
        
        reports_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Check if temp file exists
        src_path = Path(image_path_str)
        if not src_path.exists():
            # If not absolute, resolve relative to current working directory
            if not src_path.is_absolute():
                src_path = Path(os.getcwd()) / src_path
            if not src_path.exists():
                raise FileNotFoundError(f"Source temporary image file not found: {image_path_str}")
        
        # 3. Determine destination filename
        dest_filename = f"reported_{scan_id}{src_path.suffix}"
        dest_path = images_dir / dest_filename
        
        # 4. Copy image file to reported folder
        shutil.copy2(src_path, dest_path)
        logger.info(f"Copied banknote scan from {src_path} to {dest_path}")
        
        # 5. Clean up original temp upload file
        try:
            os.remove(src_path)
            logger.info(f"Deleted original temporary upload file: {src_path}")
        except Exception as e:
            logger.warning(f"Could not delete temporary scan {src_path}: {e}")
            
        # 6. Generate report JSON structure
        timestamp = int(time.time())
        report_id = f"REP-{scan_id}-{timestamp}"
        
        # Format the relative imagePath relative to workspace directory
        relative_image_path = str(dest_path.resolve().relative_to(Path.cwd().resolve())).replace("\\", "/")
        
        report_data = {
            "reportId": report_id,
            "prediction": prediction,
            "confidence": confidence,
            "imagePath": relative_image_path,
            "reportedAt": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "status": "Pending",
            "recommendation": "Submit to authorities for manual verification."
        }
        
        # Write JSON to reports/report_<timestamp>.json
        report_json_path = reports_dir / f"report_{timestamp}.json"
        with open(report_json_path, "w") as f:
            json.dump(report_data, f, indent=4)
            
        logger.info(f"Written local report JSON metadata to: {report_json_path}")
        return report_id
