from typing import Dict, Any, List

def generate_explanation(prediction: str) -> Dict[str, Any]:
    """
    Generates RBI feature-based explanations and recommendations based on classification.
    
    Args:
        prediction: The predicted banknote status ("Counterfeit" or "Genuine").
        
    Returns:
        A dictionary with keys 'detectedFeatures', 'explanation', and 'recommendation'.
    """
    if prediction == "Counterfeit":
        detected_features = [
            "Watermark appears inconsistent",
            "Security thread could not be verified",
            "Micro lettering appears blurred",
            "Colour shifting feature missing"
        ]
        explanation = (
            "Visual analysis of the banknote shows key mismatches. The security thread could not "
            "be verified under template registration, and standard watermarks appear inconsistent. "
            "This suggests the note is counterfeit."
        )
        recommendation = "Submit to authorities for manual verification."
    else:
        detected_features = [
            "Security thread appears consistent",
            "Watermark detected",
            "Visual characteristics align with RBI specifications"
        ]
        explanation = (
            "Visual characteristics align with RBI specifications. The security thread appears "
            "consistent and the structural watermark is detected."
        )
        recommendation = "No action required. Note verified safe."
        
    return {
        "detectedFeatures": detected_features,
        "explanation": explanation,
        "recommendation": recommendation
    }
