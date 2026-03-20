"""
Retraining pipeline for scaled dataset.

This script retrains the model using the scaled and augmented dataset created in Stage 12.
"""

import argparse
from pathlib import Path
import sys

# Add workspace to path
workspace_dir = Path(__file__).parent
sys.path.insert(0, str(workspace_dir))


def retrain_with_scaled_data(
    dataset_dir: str = "dataset/scaled",
    output_dir: str = "models",
    epochs: int = 20,
    batch_size: int = 8,
):
    """Retrain model with scaled dataset.

    Args:
        dataset_dir: Path to scaled dataset directory.
        output_dir: Output directory for trained model.
        epochs: Number of training epochs.
        batch_size: Batch size for training.
    """
    print("\n" + "=" * 80)
    print("Retraining with Scaled Dataset")
    print("=" * 80)

    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        print(f"❌ Dataset not found: {dataset_dir}")
        return False

    print(f"\n✓ Dataset directory: {dataset_path.absolute()}")

    # Count samples
    sample_count = len(list(dataset_path.rglob("*.npy")))
    print(f"✓ Total samples: {sample_count}")

    # List classes
    classes = sorted([d.name for d in dataset_path.iterdir() if d.is_dir()])
    print(f"✓ Classes: {classes}")

    for cls in classes:
        cls_count = len(list((dataset_path / cls).glob("*.npy")))
        print(f"  - {cls}: {cls_count} samples")

    print(f"\n{'=' * 80}")
    print("Training Configuration")
    print(f"{'=' * 80}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    print(f"Dataset: {dataset_dir}")
    print(f"Output: {output_dir}")

    print(f"\n{'=' * 80}")
    print("Training Steps")
    print(f"{'=' * 80}")

    # Import training module
    try:
        from train_full import main as train_main

        print(f"\n✓ Training module imported")
        print(f"\nTo train the model, run:")
        print(f"  python train_full.py --dataset {dataset_dir} --epochs {epochs}")

    except ImportError as e:
        print(f"⚠ Could not import training module: {e}")
        print(f"Try running: python train_full.py --dataset {dataset_dir}")

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Retrain MediSign model with scaled dataset"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="dataset/scaled",
        help="Path to scaled dataset",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models",
        help="Output directory for trained model",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=20,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for training",
    )
    args = parser.parse_args()

    retrain_with_scaled_data(
        dataset_dir=args.dataset,
        output_dir=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
