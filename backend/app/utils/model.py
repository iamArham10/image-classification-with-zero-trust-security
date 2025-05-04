import torch
import torchvision.transforms as transforms
from PIL import Image
import io

def load_model():
    model = torch.hub.load('chenyaofo/pytorch-cifar-models', 'cifar10_resnet20', pretrained=True)
    model.eval()
    return model

def preprocess_image(image_bytes):
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
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        top_prob, top_class = torch.topk(probabilities, k=5)
    return top_prob, top_class

def get_class_names():
    return ['airplane', 'automobile', 'bird', 'cat', 'deer',
            'dog', 'frog', 'horse', 'ship', 'truck']

def classify_image(image_bytes):
    
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