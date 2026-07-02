import os
import shutil
import glob
import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/v1/currency"

def run_tests():
    print("====================================================")
    print("🧪 Starting RakshaNet Currency Analyzer API Test")
    print("====================================================\n")

    # 1. Resolve paths to specific test images
    base_dir = Path(__file__).resolve().parent.parent
    real_img_path = base_dir / "datasets" / "raw" / "currency500_real_fake" / "real" / "REAL 500" / "IMG-20250717-WA0005.jpg"
    fake_img_path = base_dir / "datasets" / "raw" / "currency500_real_fake" / "real" / "REAL 500" / "IMG-20250717-WA0006.jpg"
    
    if not real_img_path.exists() or not fake_img_path.exists():
        print("❌ Error: Could not locate test images in dataset splits.")
        return
        
    print(f"✓ Target Genuine test image: {real_img_path.name}")
    print(f"✓ Target Counterfeit test image: {fake_img_path.name}\n")

    # Step 2: Test invalid file format validation
    print("📡 Step 2: Testing invalid file format validation...")
    bad_files = {"image": ("test_note.txt", b"random text file content", "text/plain")}
    response = requests.post(f"{BASE_URL}/analyze", files=bad_files)
    if response.status_code == 400:
        print("✓ Successfully rejected invalid txt format (HTTP 400 Bad Request)")
        print(f"✓ Response message: {response.json().get('detail')}\n")
    else:
        print(f"❌ Failed format validation test: status code {response.status_code}\n")

    # Step 3: Test maximum upload size validation (over 5MB)
    print("📡 Step 3: Testing file size limit validation (over 5MB)...")
    huge_bytes = b"0" * (5 * 1024 * 1024 + 100)  # > 5MB
    large_files = {"image": ("huge_note.png", huge_bytes, "image/png")}
    response = requests.post(f"{BASE_URL}/analyze", files=large_files)
    if response.status_code == 413:
        print("✓ Successfully rejected oversized upload (HTTP 413 Payload Too Large)")
        print(f"✓ Response message: {response.json().get('detail')}\n")
    else:
        print(f"❌ Failed size validation test: status code {response.status_code}\n")

    # Step 4: Test successful /analyze endpoint for Genuine Note
    print("📡 Step 4: Testing '/analyze' on Genuine banknote...")
    with open(real_img_path, "rb") as f:
        real_img_bytes = f.read()
        
    files = {"image": (real_img_path.name, real_img_bytes, "image/jpeg")}
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", files=files)
        if response.status_code == 200:
            result = response.json()
            print("✓ HTTP 200 OK")
            print("✓ Prediction: ", result.get("prediction"))
            print("✓ Confidence: ", result.get("confidence"), "%")
            print("✓ Explanation: ", result.get("explanation"))
            print("✓ Detected Features: ", result.get("detectedFeatures"))
            print("✓ Can Report: ", result.get("canReport"))
            print("✓ Scan ID: ", result.get("scanId"))
            print("✓ Saved Path: ", result.get("imagePath"), "\n")
            
            # Assertions
            assert result.get("prediction") == "Genuine"
            assert result.get("canReport") is False
            print("✓ Genuine classification assertions passed.\n")
        else:
            print("❌ Analyze Genuine endpoint failed with status code: ", response.status_code)
            print("Error details: ", response.text)
            return
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Ensure uvicorn is running on http://localhost:8000")
        return

    # Step 5: Test successful /analyze endpoint for Counterfeit Note
    print("📡 Step 5: Testing '/analyze' on Counterfeit banknote...")
    with open(fake_img_path, "rb") as f:
        fake_img_bytes = f.read()
        
    files = {"image": (fake_img_path.name, fake_img_bytes, "image/jpeg")}
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", files=files)
        if response.status_code == 200:
            result = response.json()
            print("✓ HTTP 200 OK")
            print("✓ Prediction: ", result.get("prediction"))
            print("✓ Confidence: ", result.get("confidence"), "%")
            print("✓ Explanation: ", result.get("explanation"))
            print("✓ Detected Features: ", result.get("detectedFeatures"))
            print("✓ Can Report: ", result.get("canReport"))
            print("✓ Scan ID: ", result.get("scanId"))
            print("✓ Saved Path: ", result.get("imagePath"), "\n")
            
            # Assertions
            assert result.get("prediction") == "Counterfeit"
            assert result.get("canReport") is True
            print("✓ Counterfeit classification assertions passed.\n")
            
            # Store values for the report test
            scan_id = result.get("scanId")
            temp_image_path = result.get("imagePath")
            prediction = result.get("prediction")
            confidence = result.get("confidence")
        else:
            print("❌ Analyze Counterfeit endpoint failed with status code: ", response.status_code)
            print("Error details: ", response.text)
            return
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Ensure uvicorn is running on http://localhost:8000")
        return

    # Step 6: Test /report endpoint for Counterfeit Note
    print("📡 Step 6: Testing '/report' local save submission...")
    report_payload = {
        "scanId": scan_id,
        "imagePath": temp_image_path,
        "prediction": prediction,
        "confidence": confidence
    }
    
    response = requests.post(f"{BASE_URL}/report", json=report_payload)
    if response.status_code == 200:
        result = response.json()
        print("✓ HTTP 200 OK")
        print("✓ Status: ", result.get("status"))
        print("✓ Report ID: ", result.get("reportId"))
        print("✓ Saved Locally: ", result.get("savedLocally"), "\n")
        
        report_id = result.get("reportId")
        
        assert result.get("status") == "success"
        assert result.get("savedLocally") is True
        print("✓ Report API response assertions passed.\n")
    else:
        print("❌ Report endpoint failed with status code: ", response.status_code)
        print("Error details: ", response.text)
        return

    # Step 7: Verify local filesystem storage outputs
    print("📁 Step 7: Verifying local file storage outputs...")
    
    # Check reported image exists
    images_dir = Path("reports") / "images"
    expected_image = images_dir / f"reported_{scan_id}{Path(temp_image_path).suffix}"
    
    if not expected_image.exists():
        # Try checking in web-backend subpath (where Uvicorn runs)
        expected_image = Path("web-backend") / "reports" / "images" / f"reported_{scan_id}{Path(temp_image_path).suffix}"
        
    if expected_image.exists():
        print(f"✓ Verified: Reported banknote image successfully saved to {expected_image}")
    else:
        print(f"❌ Error: Expected image copy not found at {expected_image}")
        return
        
    # Check report JSON exists
    reports = glob.glob("reports/report_*.json") + glob.glob("web-backend/reports/report_*.json")
    if len(reports) > 0:
        print(f"✓ Verified: Local JSON reports found in reports/ directory (Count: {len(reports)})")
    else:
        print("❌ Error: No report JSON files found in reports/ directory.")
        return
        
    print("\n🎉 All integration tests completed successfully!")

if __name__ == "__main__":
    run_tests()
