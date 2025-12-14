# AI & Machine Learning Fundamentals

## What is AI?
Artificial Intelligence - Making computers exhibit intelligent behavior.

## What is Machine Learning?
Teaching computers through examples rather than explicit rules.

### Types of ML
1. **Supervised Learning**: Learn from labeled examples
   - Classification: Spam vs Not Spam
   - Regression: Predict house prices

2. **Unsupervised Learning**: Find patterns without labels
   - Clustering: Group similar customers
   - Dimensionality Reduction: Simplify data

3. **Reinforcement Learning**: Learn through trial and reward
   - Game playing (AlphaGo)
   - Robotics

---

## Neural Networks

### What is a Neural Network?
A system inspired by the human brain - layers of connected "neurons" that process information.

### Architecture
```
Input Layer → Hidden Layers → Output Layer
```

### Key Concepts
- **Neuron**: Basic unit that receives inputs, applies weights, and produces output
- **Weights**: Learnable parameters that determine importance
- **Activation Function**: Adds non-linearity (ReLU, Sigmoid, Tanh)
- **Loss Function**: Measures how wrong predictions are
- **Backpropagation**: Algorithm to update weights based on errors

---

## Deep Learning

Neural Networks with many hidden layers.

### Popular Architectures
1. **CNN (Convolutional)**: Images, spatial data
2. **RNN (Recurrent)**: Sequences, time series
3. **Transformer**: Modern architecture for NLP and more

---

## LLMs (Large Language Models)

### What are LLMs?
AI models trained on vast text data to understand and generate language.

### Examples
- GPT (OpenAI)
- Claude (Anthropic)
- Gemini (Google)
- LLaMA (Meta)

### How They Work
1. **Training**: Learn patterns from billions of text samples
2. **Tokenization**: Break text into tokens
3. **Attention**: Focus on relevant parts of input
4. **Generation**: Predict next token, one at a time

---

## Transformers & Attention

### The Attention Mechanism
"Paying attention to what matters"

Instead of processing sequentially, look at all parts of input and determine relevance.

### Self-Attention Formula (Simplified)
```
Attention(Q, K, V) = softmax(QK^T / √d) × V

Q = Query (what am I looking for?)
K = Key (what do I contain?)
V = Value (what information do I have?)
```

### Why Transformers Changed Everything
- Parallelizable (fast training)
- Handle long-range dependencies
- Scale effectively with more data/compute

---

## Quiz Questions

1. What's the difference between supervised and unsupervised learning?
2. What is backpropagation used for?
3. Why are Transformers better than RNNs for many tasks?
4. What does the "attention" mechanism do?
5. Name 3 types of activation functions.
