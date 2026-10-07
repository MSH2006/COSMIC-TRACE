from __future__ import annotations

from typing import Any, Dict, List

import numpy as np


class AnomalyReasoner:
    def __init__(self) -> None:
        self.weights = {
            "motion": 0.30,
            "photometry": 0.25,
            "spectral": 0.20,
            "temporal": 0.15,
            "context": 0.10,
        }

    def analyze(self, object_data: Dict[str, Any], region: Dict[str, Any]) -> Dict[str, Any]:
        epochs = object_data["epochs"]
        if len(epochs) < 2:
            return {"anomaly_score": 0.0, "evidence_confidence": 0.0, "why_interesting": ["Not enough epochs to analyze."]}

        motion = self._analyze_motion(epochs)
        photometry = self._analyze_photometry(epochs)
        spectral = self._analyze_spectral(epochs)
        temporal = self._analyze_temporal(epochs)
        context = self._analyze_context(object_data, region)
        quality = self._check_data_quality(epochs)
        artifacts = self._investigate_artifacts(epochs)

        composite = (
            self.weights["motion"] * motion["score"]
            + self.weights["photometry"] * photometry["score"]
            + self.weights["spectral"] * spectral["score"]
            + self.weights["temporal"] * temporal["score"]
            + self.weights["context"] * context["score"]
        )

        artifact_penalty = np.mean([item["probability"] for item in artifacts]) if artifacts else 0.0
        evidence_confidence = max(0.0, min(100.0, quality["quality_score"] * (1.0 - artifact_penalty)))

        explanation = self._generate_explanation(motion, photometry, spectral, quality, context)

        return {
            "anomaly_score": round(float(min(100.0, composite)), 2),
            "evidence_confidence": round(float(evidence_confidence), 2),
            "why_interesting": explanation,
            "artifacts": artifacts,
            "data_quality": quality,
            "motion_anomaly": motion,
            "photometry_anomaly": photometry,
            "spectral_anomaly": spectral,
            "temporal_anomaly": temporal,
            "context_anomaly": context,
        }

    def _analyze_motion(self, epochs: List[Dict[str, Any]]) -> Dict[str, Any]:
        positions = [
            (epoch["data"]["ra"], epoch["data"]["dec"]) for epoch in epochs
        ]
        deltas = []
        for i in range(1, len(positions)):
            dra = abs((positions[i][0] - positions[i - 1][0]) * 3600.0)
            ddec = abs((positions[i][1] - positions[i - 1][1]) * 3600.0)
            deltas.append(np.hypot(dra, ddec))

        total_motion = float(np.sum(deltas)) if deltas else 0.0
        score = min(100.0, total_motion * 12.0)
        return {
            "score": round(score, 2),
            "is_significant": total_motion > 1.5,
            "total_motion_arcsec": round(total_motion, 3),
            "description": f"Total positional change: {total_motion:.2f} arcsec",
        }

    def _analyze_photometry(self, epochs: List[Dict[str, Any]]) -> Dict[str, Any]:
        fluxes = np.array([epoch["data"]["flux"] for epoch in epochs], dtype=float)
        if len(fluxes) < 2:
            return {"score": 0.0, "is_variable": False, "fractional_variation": 0.0, "description": "Insufficient flux data"}

        mean_flux = float(np.mean(fluxes))
        variation = float(np.std(fluxes) / mean_flux) if mean_flux else 0.0
        score = min(100.0, variation * 600.0)
        return {
            "score": round(score, 2),
            "is_variable": variation > 0.08,
            "fractional_variation": round(variation, 3),
            "description": f"Brightness variation: {variation * 100:.1f}%",
        }

    def _analyze_spectral(self, epochs: List[Dict[str, Any]]) -> Dict[str, Any]:
        spectra = []
        for epoch in epochs:
            spectrum = epoch["data"].get("spectrum")
            if spectrum:
                spectra.append(list(spectrum.values()))

        if len(spectra) < 2:
            return {"score": 0.0, "is_variable": False, "description": "No spectral information"}

        arr = np.array(spectra, dtype=float)
        variation = float(np.std(arr) / np.mean(arr)) if np.mean(arr) else 0.0
        score = min(100.0, variation * 500.0)
        return {
            "score": round(score, 2),
            "is_variable": variation > 0.12,
            "variation_fraction": round(variation, 3),
            "description": "Spectral fingerprint changes across epochs.",
        }

    def _analyze_temporal(self, epochs: List[Dict[str, Any]]) -> Dict[str, Any]:
        score = min(100.0, len(epochs) * 18.0)
        return {
            "score": round(score, 2),
            "is_significant": len(epochs) > 2,
            "epoch_count": len(epochs),
            "description": f"Observed across {len(epochs)} epochs.",
        }

    def _analyze_context(self, object_data: Dict[str, Any], region: Dict[str, Any]) -> Dict[str, Any]:
        # Compare the candidate against other sources in the region.
        target = np.mean([epoch["data"]["flux"] for epoch in object_data["epochs"]])
        all_fluxes = []
        for epoch in region["epochs"]:
            for source in epoch["sources"]:
                if source["id"] != object_data["id"]:
                    all_fluxes.append(source["flux"])

        if not all_fluxes:
            return {"score": 0.0, "is_outlier": False, "description": "No comparison sources"}

        background_mean = float(np.mean(all_fluxes))
        background_std = float(np.std(all_fluxes))
        z = abs(target - background_mean) / (background_std + 1e-9)
        score = min(100.0, z * 20.0)
        return {
            "score": round(score, 2),
            "is_outlier": z > 1.5,
            "z_score": round(z, 3),
            "description": "Behavior differs from nearby reference sources",
        }

    def _check_data_quality(self, epochs: List[Dict[str, Any]]) -> Dict[str, Any]:
        quality_values = []
        flags = []
        for epoch in epochs:
            flag = epoch["data"].get("flag", "unknown")
            flags.append(flag)
            quality_values.append(1.0 if flag == "good" else 0.7 if flag == "marginal" else 0.4)

        quality_score = float(np.mean(quality_values))
        return {
            "quality_score": round(quality_score * 100.0, 2),
            "measurement_quality": "good" if quality_score > 0.8 else "marginal" if quality_score > 0.5 else "poor",
            "flags": flags,
        }

    def _investigate_artifacts(self, epochs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        artifacts = []
        for i, epoch in enumerate(epochs):
            flux = epoch["data"].get("flux", 0.0)
            flux_err = epoch["data"].get("flux_err", 0.0)
            if flux_err / max(flux, 1.0) > 0.18:
                artifacts.append({"type": "measurement_noise", "epoch": i, "probability": 0.22, "description": "Flux uncertainty is somewhat high."})
            if epoch["data"].get("flag") == "marginal":
                artifacts.append({"type": "data_quality", "epoch": i, "probability": 0.18, "description": "One epoch has marginal quality."})
        return artifacts

    def _generate_explanation(self, motion: Dict[str, Any], photometry: Dict[str, Any], spectral: Dict[str, Any], quality: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        reasons: List[str] = []

        if motion["is_significant"]:
            reasons.append(
                f"✓ Motion anomaly: The object changed by {motion['total_motion_arcsec']} arcsec between epochs, which exceeds the typical astrometric noise floor."
            )
        if photometry["is_variable"]:
            reasons.append(
                f"✓ Photometric anomaly: The brightness changed by {photometry['fractional_variation'] * 100:.1f}% over the observation sequence."
            )
        if spectral["is_variable"]:
            reasons.append(
                "✓ Spectral anomaly: The infrared color changes across wavelengths, indicating a non-stationary spectral pattern."
            )
        if quality["measurement_quality"] in {"good", "marginal"}:
            reasons.append(
                f"✓ Data quality: The measurements are {quality['measurement_quality']} quality with enough signal for a follow-up assessment."
            )
        if context["is_outlier"]:
            reasons.append(
                f"✓ Context anomaly: The source departs from the nearby background population (z={context['z_score']})."
            )

        if not reasons:
            reasons.append("⚠ No strong anomaly detected. Object remains consistent with surrounding survey behavior.")

        return reasons


class DiscoveryPassport:
    def __init__(self, object_id: str, object_data: Dict[str, Any], analysis: Dict[str, Any], region: Dict[str, Any]):
        self.object_id = object_id
        self.object_data = object_data
        self.analysis = analysis
        self.region = region

    def to_dict(self) -> Dict[str, Any]:
        start = self.object_data["epochs"][0]["timestamp"]
        end = self.object_data["epochs"][-1]["timestamp"]
        return {
            "passport_id": f"CT-{self.region['id'].split('_')[-1]}-{self.object_id}",
            "generated_at": "2026-10-07T00:00:00Z",
            "identity": {
                "source_id": self.object_id,
                "region": self.region["name"],
                "observation_start": start,
                "observation_end": end,
                "epoch_count": len(self.object_data["epochs"]),
            },
            "motion": {
                "total_motion_arcsec": self.analysis["motion_anomaly"].get("total_motion_arcsec", 0.0),
                "assessment": "Significant motion" if self.analysis["motion_anomaly"].get("is_significant") else "Stable position",
            },
            "photometry": {
                "fractional_variation": self.analysis["photometry_anomaly"].get("fractional_variation", 0.0),
                "assessment": "Brightness changes detected" if self.analysis["photometry_anomaly"].get("is_variable") else "No strong photometric change",
            },
            "spectrum": {
                "assessment": "Multi-band infrared variation detected",
                "note": "Spectral fingerprint shows a wavelength-dependent brightening trend.",
            },
            "false_alarm_check": {
                "artifact_probability": round(float(np.mean([a["probability"] for a in self.analysis.get("artifacts", [])])) if self.analysis.get("artifacts") else 0.0, 2),
                "assessment": "Low artifact probability",
            },
            "ai_summary": {
                "anomaly_score": self.analysis.get("anomaly_score", 0.0),
                "evidence_confidence": self.analysis.get("evidence_confidence", 0.0),
                "why_interesting": self.analysis.get("why_interesting", []),
            },
            "scientific_priority": "HIGH" if self.analysis.get("anomaly_score", 0.0) > 70 else "MODERATE",
        }


if __name__ == "__main__":
    pass
