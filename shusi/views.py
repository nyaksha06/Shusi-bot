from django.shortcuts import render
from django.http import JsonResponse
import torch
import torch.nn as nn
import numpy as np
import nltk
import json
import random
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()

with open('model/intents.json', 'r') as f:
    intents = json.load(f)

def tokenize(sentence):
    return nltk.word_tokenize(sentence, language="english")

def stem(word):
    return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, all_words):
    sentence_words = [stem(word) for word in tokenized_sentence]
    bag = np.zeros(len(all_words), dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in sentence_words:
            bag[idx] = 1
    return bag

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out

FILE = "model/data.pth"  # Ensure this path is correct
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size)
model.load_state_dict(model_state)
model.eval()

def home(request):
    return render(request, 'home.html')

def bot(request):
    return render(request, 'chat.html')

def generate_response(user_message):
    input_tensor = preprocess(user_message)
    output = model(input_tensor)
    response = postprocess(output)
    return response

def send_message(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        response = generate_response(user_message)
        return JsonResponse({'response': response})
    return JsonResponse({'response': 'Invalid request method'})

def preprocess(user_message):
    sentence = tokenize(user_message)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X)
    return X

def postprocess(output):
    bot_name = "Sushi bot"
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return f"{bot_name}: {random.choice(intent['responses'])}"
    else:
        return f"{bot_name}: I do not understand..."
