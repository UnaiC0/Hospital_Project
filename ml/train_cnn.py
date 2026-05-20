import json
import os
from collections import Counter
from pathlib import Path
from time import perf_counter

import torch
from sklearn.metrics import classification_report, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms


FOLDER_TO_LABEL = {
    "COVID19": "COVID-19",
    "NORMAL": "Sana",
    "PNEUMONIA": "Neumonia",
}
DATASET_DIR = Path(os.getenv("DATASET_DIR", "/data/radiology_dataset"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", "/models"))
EPOCHS = int(os.getenv("EPOCHS", "5"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "16"))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.0005"))
PRETRAINED = os.getenv("PRETRAINED", "false").lower() == "true"
VAL_SPLIT = float(os.getenv("VAL_SPLIT", "0.2"))
SEED = int(os.getenv("SEED", "42"))
NUM_WORKERS = int(os.getenv("NUM_WORKERS", "2"))


def build_transforms():
    train_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=8),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )
    eval_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )
    return train_transform, eval_transform


def require_dataset() -> None:
    expected = [DATASET_DIR / split for split in ("train", "test")]
    missing = [str(path) for path in expected if not path.exists()]
    if missing:
        message = {
            "error": "Dataset incompleto",
            "expected_structure": {
                "train": [f"train/{folder}/imagenes" for folder in FOLDER_TO_LABEL],
                "test": [f"test/{folder}/imagenes" for folder in FOLDER_TO_LABEL],
            },
            "missing_paths": missing,
        }
        print(json.dumps(message, indent=2))
        raise SystemExit(2)


def stratified_split(targets: list[int], val_ratio: float, seed: int) -> tuple[list[int], list[int]]:
    generator = torch.Generator().manual_seed(seed)
    by_class: dict[int, list[int]] = {}
    for index, label in enumerate(targets):
        by_class.setdefault(label, []).append(index)
    train_idx: list[int] = []
    val_idx: list[int] = []
    for label, indices in by_class.items():
        permuted = [indices[i] for i in torch.randperm(len(indices), generator=generator).tolist()]
        cut = int(round(len(permuted) * val_ratio))
        val_idx.extend(permuted[:cut])
        train_idx.extend(permuted[cut:])
    return train_idx, val_idx


def map_classes(folder_classes: list[str]) -> list[str]:
    unknown = [c for c in folder_classes if c not in FOLDER_TO_LABEL]
    if unknown:
        raise ValueError(
            f"Carpetas no reconocidas en train/: {unknown}. "
            f"Esperadas: {sorted(FOLDER_TO_LABEL.keys())}"
        )
    return [FOLDER_TO_LABEL[c] for c in folder_classes]


def build_dataloaders():
    train_transform, eval_transform = build_transforms()

    full_train = datasets.ImageFolder(DATASET_DIR / "train", transform=train_transform)
    full_train_eval = datasets.ImageFolder(DATASET_DIR / "train", transform=eval_transform)
    test_dataset = datasets.ImageFolder(DATASET_DIR / "test", transform=eval_transform)

    if full_train.classes != test_dataset.classes:
        raise ValueError(
            f"train/ y test/ tienen clases distintas: {full_train.classes} vs {test_dataset.classes}"
        )

    class_names = map_classes(full_train.classes)
    targets = [label for _, label in full_train.samples]
    train_idx, val_idx = stratified_split(targets, VAL_SPLIT, SEED)

    train_subset = Subset(full_train, train_idx)
    val_subset = Subset(full_train_eval, val_idx)

    train_class_counts = Counter(targets[i] for i in train_idx)
    val_class_counts = Counter(targets[i] for i in val_idx)
    test_class_counts = Counter(label for _, label in test_dataset.samples)

    loaders = {
        "train": DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS),
        "val": DataLoader(val_subset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS),
        "test": DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS),
    }
    counts = {
        "train": {class_names[k]: v for k, v in train_class_counts.items()},
        "val": {class_names[k]: v for k, v in val_class_counts.items()},
        "test": {class_names[k]: v for k, v in test_class_counts.items()},
    }
    return loaders, class_names, train_class_counts, counts


def compute_class_weights(train_counts: Counter, num_classes: int, device: torch.device) -> torch.Tensor:
    total = sum(train_counts.values())
    weights = [total / (num_classes * max(train_counts.get(i, 1), 1)) for i in range(num_classes)]
    return torch.tensor(weights, dtype=torch.float32, device=device)


def build_model(num_classes: int) -> nn.Module:
    weights = models.ResNet18_Weights.DEFAULT if PRETRAINED else None
    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    running_correct = 0
    total = 0
    for images, labels in dataloader:
        images = images.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        running_correct += (outputs.argmax(dim=1) == labels).sum().item()
        total += images.size(0)

    return {
        "loss": running_loss / max(total, 1),
        "accuracy": running_correct / max(total, 1),
    }


@torch.no_grad()
def evaluate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    running_correct = 0
    total = 0
    y_true: list[int] = []
    y_pred: list[int] = []
    for images, labels in dataloader:
        images = images.to(device)
        labels = labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)
        predictions = outputs.argmax(dim=1)

        running_loss += loss.item() * images.size(0)
        running_correct += (predictions == labels).sum().item()
        total += images.size(0)
        y_true.extend(labels.cpu().tolist())
        y_pred.extend(predictions.cpu().tolist())

    return {
        "loss": running_loss / max(total, 1),
        "accuracy": running_correct / max(total, 1),
        "y_true": y_true,
        "y_pred": y_pred,
    }


def build_report(eval_output: dict, class_names: list[str]) -> dict:
    report = classification_report(
        eval_output["y_true"],
        eval_output["y_pred"],
        labels=list(range(len(class_names))),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(
        eval_output["y_true"],
        eval_output["y_pred"],
        labels=list(range(len(class_names))),
    ).tolist()
    return {"classification_report": report, "confusion_matrix": matrix}


def main() -> None:
    require_dataset()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    dataloaders, class_names, train_counts, split_counts = build_dataloaders()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(num_classes=len(class_names)).to(device)
    class_weights = compute_class_weights(train_counts, len(class_names), device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    started = perf_counter()
    history = []
    best_accuracy = -1.0
    best_path = MODEL_DIR / "radiology_cnn_resnet18.pt"
    contract = json.loads((Path(__file__).parent / "model_contract.json").read_text())

    for epoch in range(1, EPOCHS + 1):
        train_metrics = train_one_epoch(
            model, dataloaders["train"], criterion, optimizer, device,
        )
        val_metrics = evaluate(model, dataloaders["val"], criterion, device)
        row = {
            "epoch": epoch,
            "train": train_metrics,
            "val": {"loss": val_metrics["loss"], "accuracy": val_metrics["accuracy"]},
        }
        history.append(row)
        print(json.dumps(row))

        if val_metrics["accuracy"] > best_accuracy:
            best_accuracy = val_metrics["accuracy"]
            torch.save(
                {
                    "model_name": "radiology-cnn-resnet18",
                    "model_version": "0.2.0",
                    "class_names": class_names,
                    "state_dict": model.state_dict(),
                    "preprocessing": contract,
                },
                best_path,
            )

    val_final = evaluate(model, dataloaders["val"], criterion, device)
    test_final = evaluate(model, dataloaders["test"], criterion, device)

    metrics = {
        "model": "radiology-cnn-resnet18",
        "version": "0.2.0",
        "classes": class_names,
        "folder_mapping": FOLDER_TO_LABEL,
        "device": str(device),
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "pretrained": PRETRAINED,
        "val_split": VAL_SPLIT,
        "seed": SEED,
        "class_weights": class_weights.cpu().tolist(),
        "split_counts": split_counts,
        "duration_seconds": round(perf_counter() - started, 2),
        "best_validation_accuracy": best_accuracy,
        "history": history,
        "validation_final": {
            "loss": val_final["loss"],
            "accuracy": val_final["accuracy"],
            **build_report(val_final, class_names),
        },
        "test_final": {
            "loss": test_final["loss"],
            "accuracy": test_final["accuracy"],
            **build_report(test_final, class_names),
        },
        "clinical_reading_hint": (
            "Revisar especialmente falsos negativos de COVID-19 y confusiones COVID-19/Neumonia."
        ),
    }
    (MODEL_DIR / "radiology_cnn_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
