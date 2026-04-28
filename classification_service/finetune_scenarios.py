import torch
import torch.nn as nn
import numpy as np
from pathlib import Path

# Import model architecture
from main import EMGCNN, N_CLASSES, _normalize_signal_shape

scenarios = {
    1: [9, 18, 13, 14, 0],
    2: [10, 26, 15, 16, 0],
    3: [34, 10, 9, 0],
    5: [10, 20, 0, 14, 0]
}

def train():
    data_dir = Path(r"d:\Eng\SBE\4th\rehab\project\Rehab_Project\integration_service\data")
    model_path = Path(__file__).parent / "emg_model_epoch_40.pt"
    out_model_path = Path(__file__).parent / "emg_model_finetuned.pt"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = EMGCNN(num_classes=N_CLASSES).to(device)

    print(f"Loading checkpoint {model_path}...")
    # Load state dict
    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
    except Exception as e:
        print(f"Could not load state dict directly: {e}")
        print("Attempting to load as full model object...")
        loaded = torch.load(model_path, map_location=device)
        if isinstance(loaded, nn.Module):
            model = loaded.to(device)
        else:
            model.load_state_dict(loaded)

    X_list = []
    Y_list = []

    print("\nLoading scenarios...")
    for s_id, sequence in scenarios.items():
        npy_path = data_dir / f"scenario_{s_id}.npy"
        if not npy_path.exists():
            print(f"Warning: {npy_path} not found.")
            continue
        
        data = np.load(npy_path) # expected (12, 400 * len)
        expected_len = 400 * len(sequence)
        
        # Slicing into 400 timestep chunks
        for i, label in enumerate(sequence):
            chunk = data[:, i*400 : (i+1)*400]
            if chunk.shape[1] == 400:
                normalized_chunk = _normalize_signal_shape(chunk.tolist())
                X_list.append(normalized_chunk.numpy())
                Y_list.append(label)
            else:
                print(f"Warning: Scenario {s_id} chunk {i} has invalid shape {chunk.shape}")

    if not X_list:
        print("No data loaded. Exiting.")
        return

    X = torch.tensor(np.array(X_list), dtype=torch.float32).to(device)
    Y = torch.tensor(np.array(Y_list), dtype=torch.long).to(device)

    print(f"\nDataset shape: X={X.shape}, Y={Y.shape}")
    print(f"Unique classes in this fine-tuning set: {torch.unique(Y).tolist()}")

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    print("\nStarting training...")
    model.train()
    for m in model.modules():
        if isinstance(m, (nn.Dropout, nn.BatchNorm1d)):
            m.eval()
            
    epochs = 600
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, Y)
        loss.backward()
        optimizer.step()
        
        preds = torch.argmax(outputs, dim=1)
        acc = (preds == Y).float().mean().item()
        
        if (epoch + 1) % 50 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:3d}/{epochs} | Loss: {loss.item():.4f} | Accuracy: {acc*100:.2f}%")

    model.eval()
    with torch.no_grad():
        eval_out = model(X)
        eval_preds = torch.argmax(eval_out, dim=1)
        eval_acc = (eval_preds == Y).float().mean().item()
    print(f"\nFinal Eval Accuracy on training set: {eval_acc*100:.2f}%")

    print(f"\nSaving fine-tuned model state dict to {out_model_path}...")
    torch.save(model.state_dict(), out_model_path)
    print("Done! 🎉")

if __name__ == "__main__":
    train()
