import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import io
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from tqdm import tqdm
import os

class RobustResNet20(nn.Module):
    def __init__(self, num_classes=10):
        super(RobustResNet20, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(16)
        
        # First block
        self.layer1 = self._make_layer(16, 16, 3)
        self.layer2 = self._make_layer(16, 32, 3, stride=2)
        self.layer3 = self._make_layer(32, 64, 3, stride=2)
        
        self.linear = nn.Linear(64, num_classes)
        
    def _make_layer(self, in_channels, out_channels, num_blocks, stride=1):
        layers = []
        layers.append(ResBlock(in_channels, out_channels, stride))
        for _ in range(1, num_blocks):
            layers.append(ResBlock(out_channels, out_channels))
        return nn.Sequential(*layers)
    
    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = F.avg_pool2d(out, 8)
        out = out.view(out.size(0), -1)
        out = self.linear(out)
        return out

class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out

def pgd_attack(model, images, labels, eps=8/255, alpha=2/255, iters=10):
    images = images.clone().detach().requires_grad_(True)
    
    for _ in range(iters):
        outputs = model(images)
        loss = F.cross_entropy(outputs, labels)
        loss.backward()
        
        # Create adversarial perturbation
        adv_images = images + alpha * images.grad.sign()
        eta = torch.clamp(adv_images - images, min=-eps, max=eps)
        images = torch.clamp(images + eta, min=0, max=1).detach().requires_grad_(True)
    
    return images

def train_robust_model(epochs=100, batch_size=128, lr=0.1):
    # Load CIFAR-10 dataset
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
    ])
    
    trainset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform_train)
    trainloader = DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=2)
    
    # Initialize model
    model = RobustResNet20()
    model = model.cuda()
    
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)
    scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[50, 75], gamma=0.1)
    
    # Training loop
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (inputs, targets) in enumerate(tqdm(trainloader)):
            inputs, targets = inputs.cuda(), targets.cuda()
            
            # Generate adversarial examples
            adv_inputs = pgd_attack(model, inputs, targets)
            
            # Forward pass on both clean and adversarial examples
            outputs_clean = model(inputs)
            outputs_adv = model(adv_inputs)
            
            # Calculate losses
            loss_clean = criterion(outputs_clean, targets)
            loss_adv = criterion(outputs_adv, targets)
            loss = 0.5 * (loss_clean + loss_adv)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Calculate accuracy
            _, predicted = outputs_clean.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            total_loss += loss.item()
        
        # Print statistics
        print(f'Epoch: {epoch+1}, Loss: {total_loss/len(trainloader):.3f}, '
              f'Accuracy: {100.*correct/total:.2f}%')
        
        scheduler.step()
    
    return model

def load_model():
    """Load the pre-trained robust CIFAR-10 model"""
    # Initialize model
    model = RobustResNet20()
    
    # Get the absolute path to the model file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, '..', '..', 'models', 'robust_cifar10_model.pth')
    
    # Check if model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            "Please ensure the model file is in the correct location."
        )
    
    try:
        # Set device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Loading model on device: {device}")
        
        # Load the model state dict
        state_dict = torch.load(model_path, map_location=device)
        model.load_state_dict(state_dict)
        model = model.to(device)
        
        print("Successfully loaded pre-trained robust model")
        return model
    except Exception as e:
        raise RuntimeError(f"Error loading model: {str(e)}")

def preprocess_image(image_bytes):
    """Preprocess the image for model input"""
    # Convert bytes to PIL Image and ensure RGB
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # Define transformations
    transform = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
    
    # Apply transformations
    image_tensor = transform(image).unsqueeze(0)
    return image_tensor

def get_predictions(model, image_tensor):
    """Get predictions from the model"""
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        top_prob, top_class = torch.topk(probabilities, k=5)
    return top_prob, top_class

def get_class_names():
    """Get CIFAR-10 class names"""
    return ['airplane', 'automobile', 'bird', 'cat', 'deer',
            'dog', 'frog', 'horse', 'ship', 'truck']

def classify_image(image_bytes):
    """
    Main function to classify an image
    
    Args:
        image_bytes: Image in bytes format
    
    Returns:
        list: List of dictionaries containing class names and probabilities
    """
    # Load model
    model = load_model()
    
    # Preprocess image
    image_tensor = preprocess_image(image_bytes)
    
    # Get predictions
    top_prob, top_class = get_predictions(model, image_tensor)
    
    # Get class names
    class_names = get_class_names()
    
    # Format predictions
    predictions = []
    for i in range(len(top_prob[0])):
        predictions.append({
            "class": class_names[top_class[0][i].item()],
            "probability": float(top_prob[0][i].item())
        })
    
    return predictions 