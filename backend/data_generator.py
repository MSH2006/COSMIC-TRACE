from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


def generate_demo_regions() -> Dict[str, Dict[str, Any]]:
    """Generate a synthetic multi-epoch SPHEREx-like demo region."""
    region_id = "region_001"
    base_ra = 282.74
    base_dec = -5.52

    epochs: List[Dict[str, Any]] = []
    for i, (date, wavelength, flux_delta, ra_shift, dec_shift, spectrum) in enumerate([
        (
            "2026-03-01",
            1.1,
            0.0,
            0.0,
            0.0,
            {"1.1": 50.0, "2.5": 62.0, "4.2": 74.0},
        ),
        (
            "2026-05-15",
            2.5,
            12.0,
            0.012,
            0.011,
            {"1.1": 56.0, "2.5": 71.0, "4.2": 83.0},
        ),
        (
            "2026-08-01",
            4.2,
            20.0,
            0.025,
            0.021,
            {"1.1": 62.0, "2.5": 79.0, "4.2": 96.0},
        ),
        (
            "2026-10-07",
            3.4,
            28.0,
            0.039,
            0.033,
            {"1.1": 68.0, "2.5": 88.0, "4.2": 110.0},
        ),
    ]):
        object_source = {
            "id": "RW-001",
            "ra": base_ra + ra_shift,
            "dec": base_dec + dec_shift,
            "flux": 42.0 + flux_delta,
            "flux_err": 2.1,
            "flag": "good",
            "psf_fwhm": 2.1,
            "type": "unknown",
            "spectrum": spectrum,
        }

        background_sources = [
            {"id": f"BG-{idx:03d}", "ra": base_ra + 0.03 * idx, "dec": base_dec - 0.025 * idx, "flux": 18.0 + idx * 2.5, "flux_err": 1.4, "flag": "good", "psf_fwhm": 1.8, "type": "star"}
            for idx in range(1, 6)
        ]

        epochs.append(
            {
                "timestamp": date,
                "jd": 2460000 + i * 70,
                "wavelength": wavelength,
                "sources": [object_source, *background_sources],
            }
        )

    return {
        region_id: {
            "id": region_id,
            "name": "Serpens Deep Survey",
            "ra_center": base_ra,
            "dec_center": base_dec,
            "epochs": epochs,
            "discovery_story": {
                "headline": "A candidate object changes position, brightness, and spectral signature across survey epochs.",
                "narrative": [
                    "The user opens the sky explorer and selects a region containing a candidate source.",
                    "Multiple epochs reveal a coherent change in position and brightness.",
                    "The spectral footprint becomes redder over time, indicating a potentially interesting object.",
                    "The AI explains why the signal is unusual and flags it for follow-up.",
                ],
            },
        }
    }


if __name__ == "__main__":
    regions = generate_demo_regions()
    print(list(regions.keys()))
    print(regions["region_001"]["epochs"][0]["sources"][0])
