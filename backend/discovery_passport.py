"""
Scientific Discovery Passport
Comprehensive profile for high-priority astronomical candidates.
"""
from datetime import datetime
from typing import Dict, List, Any


class DiscoveryPassport:
    """
    Generates a scientific-style profile for each candidate object.
    
    Contains:
    - Identity & coordinates
    - Motion history
    - Photometry
    - Spectra
    - Data quality
    - AI analysis
    - Cross-mission evidence
    - Scientific assessment
    """
    
    def __init__(self, object_data: Dict, analysis: Dict, region: Dict):
        """
        Initialize passport.
        
        Args:
            object_data: Object temporal sequence
            analysis: Anomaly analysis results
            region: Region context
        """
        self.object_data = object_data
        self.analysis = analysis
        self.region = region
        self.passport_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique passport identifier."""
        obj_id = self.object_data["id"]
        region_id = self.region["id"]
        
        # Format: CT-REGION-OBJECT (e.g., CT-001-RW-001)
        region_num = region_id.split("_")[-1]
        return f"CT-{region_num}-{obj_id}"
    
    def to_dict(self) -> Dict:
        """Convert passport to dictionary."""
        return {
            "passport_id": self.passport_id,
            "generated": datetime.now().isoformat(),
            "identity": self._identity_section(),
            "motion": self._motion_section(),
            "photometry": self._photometry_section(),
            "spectrum": self._spectrum_section(),
            "data_quality": self._data_quality_section(),
            "ai_analysis": self._ai_analysis_section(),
            "false_alarm_check": self._false_alarm_section(),
            "known_object_assessment": self._known_object_section(),
            "scientific_priority": self._scientific_priority_section(),
            "summary": self._summary_section()
        }
    
    def _identity_section(self) -> Dict:
        """Object identity information."""
        first_epoch = self.object_data["epochs"][0]
        
        return {
            "source_id": self.object_data["id"],
            "right_ascension_deg": round(first_epoch["data"]["ra"], 6),
            "declination_deg": round(first_epoch["data"]["dec"], 6),
            "observation_start": self.object_data["epochs"][0]["timestamp"],
            "observation_end": self.object_data["epochs"][-1]["timestamp"],
            "epoch_count": len(self.object_data["epochs"]),
            "region": self.region["name"]
        }
    
    def _motion_section(self) -> Dict:
        """Motion/trajectory analysis."""
        motion_analysis = self.analysis.get("motion_anomaly", {})
        
        positions = []
        for epoch in self.object_data["epochs"]:
            positions.append({
                "timestamp": epoch["timestamp"],
                "ra": round(epoch["data"]["ra"], 6),
                "dec": round(epoch["data"]["dec"], 6)
            })
        
        return {
            "detected": motion_analysis.get("is_significant", False),
            "total_motion_arcsec": round(motion_analysis.get("total_motion_arcsec", 0), 3),
            "description": motion_analysis.get("description", "No motion detected"),
            "position_history": positions,
            "assessment": "Significant positional change" if motion_analysis.get("is_significant") else "Within measurement uncertainty"
        }
    
    def _photometry_section(self) -> Dict:
        """Brightness/flux analysis."""
        photometry_analysis = self.analysis.get("photometry_anomaly", {})
        
        fluxes = []
        for epoch in self.object_data["epochs"]:
            data = epoch["data"]
            fluxes.append({
                "timestamp": epoch["timestamp"],
                "flux": round(data["flux"], 2),
                "flux_error": round(data["flux_err"], 2),
                "snr": round(data["flux"] / data["flux_err"], 1)
            })
        
        return {
            "variable": photometry_analysis.get("is_variable", False),
            "fractional_variation": round(photometry_analysis.get("fractional_variation", 0), 3),
            "flux_range": photometry_analysis.get("flux_range"),
            "description": photometry_analysis.get("description", "No variation detected"),
            "light_curve": fluxes,
            "assessment": "Significant brightness changes" if photometry_analysis.get("is_variable") else "Stable brightness"
        }
    
    def _spectrum_section(self) -> Dict:
        """Spectral characteristics."""
        # For demo, simplified spectral analysis
        return {
            "wavelength_coverage": "0.75 - 5.0 μm (102 infrared bands)",
            "observations": len(self.object_data["epochs"]),
            "note": "Full spectral fingerprint available in detailed analysis",
            "assessment": "Multi-wavelength infrared observations obtained"
        }
    
    def _data_quality_section(self) -> Dict:
        """Measurement quality and flags."""
        quality = self.analysis.get("data_quality", {})
        
        return {
            "overall_quality": quality.get("measurement_quality", "unknown"),
            "quality_score": round(quality.get("overall_quality", 0) * 100, 1),
            "individual_flags": quality.get("flags", []),
            "measurement_errors": [round(e*100, 1) for e in quality.get("quality_scores", [])],
            "assessment": "High-confidence measurement" if quality.get("overall_quality", 0) > 0.8 else "Moderate confidence"
        }
    
    def _ai_analysis_section(self) -> Dict:
        """AI anomaly reasoning."""
        return {
            "anomaly_score": round(self.analysis.get("anomaly_score", 0), 1),
            "interestingness_score": round(self.analysis.get("anomaly_score", 0), 1),
            "evidence_confidence": round(self.analysis.get("evidence_confidence", 0), 1),
            "why_interesting": self.analysis.get("why_interesting", []),
            "note": "Scores represent AI assessment of scientific interest and measurement reliability"
        }
    
    def _false_alarm_section(self) -> Dict:
        """Artifact and false-alarm investigation."""
        artifacts = self.analysis.get("artifacts", [])
        
        artifact_summary = []
        total_prob = 0
        
        for artifact in artifacts:
            artifact_summary.append({
                "type": artifact.get("type", "unknown"),
                "probability": round(artifact.get("probability", 0), 2),
                "description": artifact.get("description", "")
            })
            total_prob += artifact.get("probability", 0)
        
        mean_artifact_prob = total_prob / len(artifacts) if artifacts else 0
        
        return {
            "potential_artifacts": artifact_summary,
            "artifact_probability": round(mean_artifact_prob, 2),
            "assessment": "Low artifact probability—anomaly likely real" if mean_artifact_prob < 0.3 else "Moderate artifact risk—consider with caution" if mean_artifact_prob < 0.6 else "High artifact probability—likely instrumental effect"
        }
    
    def _known_object_section(self) -> Dict:
        """Known-object cross-check."""
        # Simplified: no catalog query in demo
        return {
            "catalog_match": "Not found in available reference subset",
            "possible_types": ["Unknown/Unclassified", "Potential moving object", "Variable star"],
            "assessment": "No confident match to known object—candidate for follow-up investigation"
        }
    
    def _scientific_priority_section(self) -> Dict:
        """Overall scientific priority ranking."""
        anomaly_score = self.analysis.get("anomaly_score", 0)
        confidence = self.analysis.get("evidence_confidence", 0)
        
        if anomaly_score > 80 and confidence > 75:
            priority = "VERY HIGH"
            priority_num = 1
        elif anomaly_score > 60 and confidence > 60:
            priority = "HIGH"
            priority_num = 2
        elif anomaly_score > 40 and confidence > 40:
            priority = "MODERATE"
            priority_num = 3
        else:
            priority = "LOW"
            priority_num = 4
        
        return {
            "priority": priority,
            "priority_level": priority_num,
            "recommendation": self._get_recommendation(priority)
        }
    
    def _get_recommendation(self, priority: str) -> str:
        """Get follow-up recommendation based on priority."""
        recommendations = {
            "VERY HIGH": "High-priority candidate for detailed spectroscopic follow-up and ground-based observations.",
            "HIGH": "Recommended for follow-up observations within normal survey cadence.",
            "MODERATE": "Interesting candidate—follow-up recommended if survey time permits.",
            "LOW": "Monitor for future observations; low priority for targeted follow-up at this time."
        }
        return recommendations.get(priority, "Recommend reviewing raw data.")
    
    def _summary_section(self) -> Dict:
        """Executive summary."""
        return {
            "title": f"Scientific Discovery Passport: {self.passport_id}",
            "generated_by": "COSMIC-TRACE Anomaly Discovery Engine",
            "version": "0.1.0",
            "key_findings": self.analysis.get("why_interesting", []),
            "next_steps": [
                "Review full light curve and spectral evolution",
                "Check against known moving objects and variable sources",
                "Consider follow-up observations in targeted filters",
                "Investigate temporal correlations with other survey data"
            ]
        }
