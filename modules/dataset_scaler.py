"""
Dataset Scaling Module — Synthetic data generation, augmentation, and balancing.

Features:
- Synthetic feature generation from existing samples
- Data augmentation (noise, scaling, temporal shifts)
- Mixup: blend two samples for smoother decision boundaries
- Class balancing: oversample minority classes
- Dataset expansion: scale from 45 samples to 100+ samples
"""

from __future__ import annotations

import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import shutil
from datetime import datetime


class DatasetScaler:
    """Scale and augment medical sign language datasets."""

    def __init__(self, dataset_dir: str = "dataset", seed: int = 42):
        """Initialize dataset scaler.

        Args:
            dataset_dir: Root dataset directory.
            seed: Random seed for reproducibility.
        """
        self.dataset_dir = Path(dataset_dir)
        self.seed = seed
        np.random.seed(seed)
        print(f"✓ DatasetScaler initialized with seed={seed}")

    def load_dataset(self, class_dir: str) -> Dict[str, np.ndarray]:
        """Load all feature samples from a class directory.

        Args:
            class_dir: Class subdirectory (e.g., 'dataset/demo').

        Returns:
            Dictionary mapping filename to feature array.
        """
        class_path = Path(class_dir)
        samples = {}

        if not class_path.exists():
            print(f"⚠ Class directory not found: {class_path}")
            return samples

        for npy_file in sorted(class_path.glob("*.npy")):
            try:
                data = np.load(npy_file)
                samples[npy_file.name] = data
                print(f"  Loaded: {npy_file.name} {data.shape}")
            except Exception as e:
                print(f"  ⚠ Failed to load {npy_file.name}: {e}")

        print(f"✓ Loaded {len(samples)} samples from {class_path}")
        return samples

    def augment_sample(
        self,
        sample: np.ndarray,
        augmentation_type: str = "noise",
        intensity: float = 0.1,
    ) -> np.ndarray:
        """Apply augmentation to a single feature sample.

        Args:
            sample: Feature array (60, 1280).
            augmentation_type: Type of augmentation ('noise', 'scale', 'shift', 'jitter').
            intensity: Strength of augmentation [0, 1].

        Returns:
            Augmented copy of the sample.
        """
        augmented = sample.copy()

        if augmentation_type == "noise":
            # Add Gaussian noise
            noise = np.random.normal(0, intensity * 0.1, augmented.shape)
            augmented = augmented + noise

        elif augmentation_type == "scale":
            # Scale features by random factor
            scale_factor = 1.0 + np.random.uniform(-intensity, intensity)
            augmented = augmented * scale_factor

        elif augmentation_type == "shift":
            # Temporal shift: roll frames along time axis
            shift_amount = int(intensity * 10)
            augmented = np.roll(augmented, shift_amount, axis=0)

        elif augmentation_type == "jitter":
            # Add small random perturbations to each frame
            for t in range(augmented.shape[0]):
                jitter = np.random.normal(0, intensity * 0.05, augmented[t].shape)
                augmented[t] = augmented[t] + jitter

        elif augmentation_type == "temporal_smooth":
            # Smooth temporal dimension to reduce jitter
            window = int(3 + intensity * 5)  # 3-8 frame window
            for t in range(1, augmented.shape[0] - 1):
                augmented[t] = np.mean(
                    augmented[max(0, t - window) : min(augmented.shape[0], t + window)],
                    axis=0,
                )

        # Clip to reasonable range (preserve distribution)
        augmented = np.clip(augmented, sample.min() - 1, sample.max() + 1)
        return augmented

    def mixup_samples(
        self,
        sample1: np.ndarray,
        sample2: np.ndarray,
        alpha: float = 0.5,
    ) -> np.ndarray:
        """Blend two samples using mixup technique.

        Args:
            sample1: First feature array (60, 1280).
            sample2: Second feature array (60, 1280).
            alpha: Blend factor [0, 1] (0.5 = equal blend).

        Returns:
            Blended sample.
        """
        if sample1.shape != sample2.shape:
            print(f"⚠ Shape mismatch: {sample1.shape} vs {sample2.shape}")
            return sample1.copy()

        # Mixup: weighted average
        blended = alpha * sample1 + (1 - alpha) * sample2
        return blended

    def generate_synthetic_samples(
        self,
        base_sample: np.ndarray,
        num_samples: int = 5,
        augmentation_types: List[str] = None,
    ) -> List[np.ndarray]:
        """Generate synthetic samples from a base sample using augmentation.

        Args:
            base_sample: Base feature array (60, 1280).
            num_samples: Number of synthetic samples to generate.
            augmentation_types: List of augmentation types to apply.

        Returns:
            List of generated synthetic samples.
        """
        if augmentation_types is None:
            augmentation_types = ["noise", "scale", "shift", "jitter"]

        synthetic_samples = []

        for i in range(num_samples):
            # Randomly choose augmentation type and intensity
            aug_type = np.random.choice(augmentation_types)
            intensity = np.random.uniform(0.05, 0.2)

            augmented = self.augment_sample(
                base_sample, augmentation_type=aug_type, intensity=intensity
            )
            synthetic_samples.append(augmented)

        print(f"✓ Generated {num_samples} synthetic samples using {augmentation_types}")
        return synthetic_samples

    def balance_dataset(
        self,
        source_dirs: Dict[str, str],
        target_dir: str = "dataset/scaled",
        target_samples_per_class: int = 50,
    ) -> Dict[str, int]:
        """Balance dataset by oversampling minority classes and augmenting.

        Args:
            source_dirs: Dictionary mapping class_name to source_directory.
            target_dir: Output directory for balanced dataset.
            target_samples_per_class: Target number of samples per class.

        Returns:
            Dictionary mapping class_name to generated_count.
        """
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        results = {}

        for class_name, class_dir in source_dirs.items():
            class_path = Path(class_dir)
            class_target = target_path / class_name
            class_target.mkdir(exist_ok=True)

            # Load original samples
            samples = self.load_dataset(str(class_path))

            if not samples:
                print(f"⚠ No samples found for class: {class_name}")
                results[class_name] = 0
                continue

            original_count = len(samples)
            samples_list = list(samples.values())
            generated_count = 0

            # Copy original samples
            for orig_name, sample_data in samples.items():
                target_file = class_target / orig_name
                np.save(target_file, sample_data)
                generated_count += 1

            # Generate synthetic samples if needed
            if original_count < target_samples_per_class:
                needed = target_samples_per_class - original_count
                print(
                    f"\nBalancing {class_name}: need {needed} more samples (original: {original_count})"
                )

                for i in range(needed):
                    # Select random base sample
                    base_idx = i % len(samples_list)
                    base_sample = samples_list[base_idx]

                    # Generate augmented version
                    augmented = self.augment_sample(
                        base_sample,
                        augmentation_type=np.random.choice(
                            ["noise", "scale", "shift", "jitter"]
                        ),
                        intensity=np.random.uniform(0.05, 0.2),
                    )

                    # Optional: apply mixup with another random sample
                    if np.random.rand() > 0.6 and len(samples_list) > 1:
                        other_idx = np.random.randint(0, len(samples_list))
                        if other_idx != base_idx:
                            alpha = np.random.uniform(0.3, 0.7)
                            augmented = self.mixup_samples(
                                augmented, samples_list[other_idx], alpha=alpha
                            )

                    # Save synthetic sample
                    synthetic_name = f"{class_name}_synthetic_{generated_count:03d}.npy"
                    target_file = class_target / synthetic_name
                    np.save(target_file, augmented)
                    generated_count += 1

                    if (i + 1) % 10 == 0:
                        print(f"  Generated {i + 1}/{needed} samples...")

            results[class_name] = generated_count
            print(f"✓ {class_name}: {original_count} → {generated_count} samples")

        return results

    def analyze_dataset(self, class_dir: str) -> Dict:
        """Analyze dataset statistics.

        Args:
            class_dir: Class directory to analyze.

        Returns:
            Dictionary with statistics.
        """
        samples = self.load_dataset(class_dir)

        if not samples:
            return {"error": "No samples found"}

        data_list = list(samples.values())
        data_array = np.stack(data_list)

        stats = {
            "num_samples": len(samples),
            "shape": data_list[0].shape if data_list else None,
            "mean": float(np.mean(data_array)),
            "std": float(np.std(data_array)),
            "min": float(np.min(data_array)),
            "max": float(np.max(data_array)),
            "memory_mb": data_array.nbytes / (1024 * 1024),
        }

        return stats

    def create_scaled_dataset(
        self,
        source_dirs: Dict[str, str] = None,
        target_dir: str = "dataset/scaled",
        samples_per_class: int = 50,
    ) -> Tuple[Dict[str, int], Dict[str, Dict]]:
        """Create a scaled and balanced dataset from source directories.

        Args:
            source_dirs: Dictionary mapping class_name to source_directory.
            target_dir: Output directory path.
            samples_per_class: Target samples per class.

        Returns:
            Tuple of (generation_results, stats).
        """
        if source_dirs is None:
            # Auto-discover classes
            source_dirs = {}
            for subdir in self.dataset_dir.iterdir():
                if subdir.is_dir() and (subdir / "*.npy").exists():
                    source_dirs[subdir.name] = str(subdir)

        print(f"\n{'=' * 80}")
        print("Creating Scaled Dataset")
        print(f"{'=' * 80}")
        print(f"Source classes: {list(source_dirs.keys())}")
        print(f"Target directory: {target_dir}")
        print(f"Target samples per class: {samples_per_class}\n")

        # Balance dataset
        generation_results = self.balance_dataset(
            source_dirs, target_dir, samples_per_class
        )

        # Analyze results
        target_path = Path(target_dir)
        stats = {}

        print(f"\n{'=' * 80}")
        print("Dataset Scaling Summary")
        print(f"{'=' * 80}\n")

        for class_name in generation_results.keys():
            class_path = target_path / class_name
            class_stats = self.analyze_dataset(str(class_path))
            stats[class_name] = class_stats

            print(f"Class: {class_name}")
            print(f"  Samples: {generation_results[class_name]}")
            print(f"  Shape: {class_stats.get('shape')}")
            print(f"  Mean: {class_stats.get('mean', 0):.6f}")
            print(f"  Std: {class_stats.get('std', 0):.6f}")
            print(
                f"  Range: [{class_stats.get('min', 0):.4f}, {class_stats.get('max', 0):.4f}]"
            )
            print(f"  Memory: {class_stats.get('memory_mb', 0):.2f} MB\n")

        total_samples = sum(generation_results.values())
        total_memory = sum(s.get("memory_mb", 0) for s in stats.values())

        print(f"Total samples generated: {total_samples}")
        print(f"Total memory used: {total_memory:.2f} MB")

        return generation_results, stats


def main():
    """Demo of dataset scaling."""
    print("\n" + "=" * 80)
    print("MediSign Dataset Scaling Demo")
    print("=" * 80)

    scaler = DatasetScaler(dataset_dir="dataset", seed=42)

    # Create scaled dataset
    source_dirs = {
        "demo": "dataset/demo",
        "demo2": "dataset/demo2",
    }

    generation_results, stats = scaler.create_scaled_dataset(
        source_dirs=source_dirs,
        target_dir="dataset/scaled",
        samples_per_class=50,
    )

    print(f"\n✓ Scaled dataset created at: dataset/scaled/")
    print(f"  - Total samples: {sum(generation_results.values())}")
    print(f"  - Ready for retraining: python train_full.py --dataset dataset/scaled")


if __name__ == "__main__":
    main()
