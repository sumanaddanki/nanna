# Mathematical Foundations

## Linear Algebra

### Vectors
A list of numbers representing magnitude and direction.

```
v = [3, 4]  → 2D vector
v = [1, 2, 3]  → 3D vector
```

**Real-world examples:**
- Location: [x, y] coordinates
- RGB color: [255, 0, 0] = red
- Features: [height, weight, age]

### Vector Operations
```
Addition: [1,2] + [3,4] = [4,6]
Scalar multiply: 2 × [1,2] = [2,4]
Dot product: [1,2] · [3,4] = 1×3 + 2×4 = 11
```

### Matrices
A 2D array of numbers.

```
A = | 1  2 |
    | 3  4 |
```

**Why matrices matter:**
- Represent transformations
- Store data tables
- Neural network weights

### Matrix Multiplication
```
(m × n) × (n × p) = (m × p)

Dimensions must align!
```

---

## Calculus

### Derivatives
Rate of change - "how fast is something changing?"

```
f(x) = x²
f'(x) = 2x  (derivative)
```

**Intuition:** Slope of the curve at any point.

**In ML:** Gradient descent uses derivatives to minimize loss.

### Partial Derivatives
Derivative with respect to one variable, holding others constant.

```
f(x,y) = x² + xy
∂f/∂x = 2x + y
∂f/∂y = x
```

### Integrals
"Area under the curve" - accumulation.

```
∫x² dx = x³/3 + C
```

**In ML:** Probability distributions, cumulative functions.

---

## Probability

### Basic Rules

**Sample Space (S):** All possible outcomes
**Event (E):** Subset of outcomes

```
P(E) = Number of favorable outcomes / Total outcomes
```

### Key Formulas

**Addition Rule:**
```
P(A or B) = P(A) + P(B) - P(A and B)
```

**Multiplication Rule (Independent):**
```
P(A and B) = P(A) × P(B)
```

**Conditional Probability:**
```
P(A|B) = P(A and B) / P(B)
```

**Bayes' Theorem:**
```
P(A|B) = P(B|A) × P(A) / P(B)
```

---

## Statistics

### Measures of Central Tendency

**Mean (Average):**
```
μ = Σx / n
```

**Median:** Middle value when sorted

**Mode:** Most frequent value

### Measures of Spread

**Variance:**
```
σ² = Σ(x - μ)² / n
```

**Standard Deviation:**
```
σ = √variance
```

### Distributions

**Normal Distribution (Bell Curve):**
- Symmetric around mean
- 68% within 1σ, 95% within 2σ, 99.7% within 3σ

**Uniform:** Equal probability for all outcomes

**Bernoulli:** Binary outcome (success/failure)

**Binomial:** Multiple Bernoulli trials

---

## Math for AI/ML

### Gradient Descent
Find minimum of loss function by following negative gradient.

```
θ_new = θ_old - α × ∇L(θ)

α = learning rate
∇L = gradient of loss
```

### Softmax Function
Convert logits to probabilities.

```
softmax(x_i) = e^(x_i) / Σe^(x_j)
```

### Cross-Entropy Loss
Measure prediction vs actual distribution.

```
L = -Σ y_true × log(y_pred)
```

---

## Quiz Questions

1. What is the dot product of [1,2,3] and [4,5,6]?
2. What does a derivative measure intuitively?
3. State Bayes' Theorem.
4. What is the standard deviation of [2, 4, 4, 4, 5, 5, 7, 9]?
5. In gradient descent, what does the learning rate control?
