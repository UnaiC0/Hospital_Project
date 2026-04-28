import json
import os
from pathlib import Path
from time import perf_counter

import torch
from sklearn.metrics import classification_report, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


LABELS = ["Sana", "Neumonia", "COVID-19"]
DATASET_DIR = Path(os.getenv("DATASET_DIR", "/data/radiology_dataset"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", "/models"))
EPOCHS = int(os.getenv("EPOCHS", "5"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "16"))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.0005"))
PRETRAINED = os.getenv("PRETRAINED", "false").lower() == "true"


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
    expected = [DATASET_DIR / split for split in ("train", "val")]
    missing = [str(path) for path in expected if not path.exists()]
    if missing:
        message = {
            "error": "Dataset incompleto",
            "expected_structure": {
                "train": [f"train/{label}/imagenes" for label in LABELS],
                "val": [f"val/{label}/imagenes" for label in LABELS],
                "test_optional": [f"test/{label}/imagenes" for label in LABELS],
            },
            "missing_paths": missing,
        }
        print(json.dumps(message, indent=2))
        raise SystemExit(2)


def build_dataloaders():
    train_transform, eval_transform = build_transforms()
    train_dataset = datasets.ImageFolder(DATASET_DIR / "train", transform=train_transform)
    val_dataset = datasets.ImageFolder(DATASET_DIR / "val", transform=eval_transform)

    if set(train_dataset.classes) != set(LABELS):
        raise ValueError(f"Clases esperadas: {LABELS}. Clases encontradas: {train_dataset.classes}")

    return {
        "train": DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2),
        "val": DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2),
    }, train_dataset.classes


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
    y_true = []
    y_pred = []
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


def main() -> None:
    require_dataset()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    dataloaders, classes = build_dataloaders()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(num_classes=len(classes)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    started = perf_counter()
    history = []
    best_accuracy = -1.0
    best_path = MODEL_DIR / "radiology_cnn_resnet18.pt"

    for epoch in range(1, EPOCHS + 1):
        train_metrics = train_one_epoch(
            model,
            dataloaders["train"],
            criterion,
            optimizer,
            device,
        )
        val_metrics = evaluate(model, dataloaders["val"], criterion, device)
        row = {
            "epoch": epoch,
            "train": train_metrics,
            "val": {
                "loss": val_metrics["loss"],
                "accuracy": val_metrics["accuracy"],
            },
        }
        history.append(row)
        print(json.dumps(row))

        if val_metrics["accuracy"] > best_accuracy:
            best_accuracy = val_metrics["accuracy"]
            torch.save(
                {
                    "model_name": "radiology-cnn-resnet18",
                    "model_version": "0.1.0",
                    "class_names": classes,
                    "state_dict": model.state_dict(),
                    "preprocessing": json.loads((Path(__file__).parent / "model_contract.json").read_text()),
                },
                best_path,
            )

    final_metrics = evaluate(model, dataloaders["val"], criterion, device)
    report = classification_report(
        final_metrics["y_true"],
        final_metrics["y_pred"],
        labels=list(range(len(classes))),
        target_names=classes,
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(
        final_metrics["y_true"],
        final_metrics["y_pred"],
        labels=list(range(len(classes))),
    ).tolist()

    metrics = {
        "model": "radiology-cnn-resnet18",
        "version": "0.1.0",
        "classes": classes,
        "device": str(device),
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "pretrained": PRETRAINED,
        "duration_seconds": round(perf_counter() - started, 2),
        "best_validation_accuracy": best_accuracy,
        "history": history,
        "classification_report": report,
        "confusion_matrix": matrix,
        "clinical_reading_hint": (
            "Revisar especialmente falsos negativos de COVID-19 y confusiones COVID-19/Neumonia."
        ),
    }
    (MODEL_DIR / "radiology_cnn_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
