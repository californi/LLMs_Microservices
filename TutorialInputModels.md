
# 🧠 LLM Microservice - Input Parameters Guide

This microservice was designed to provide a flexible and reusable interface for interacting with Large Language Models (LLMs). It simulates integration with platforms such as Hugging Face, OpenAI, and local models. Below are the **four main input parameters** used to interact with the service.

---

## 🔹 Input Parameters

### 1. `artifacts: List[str]`

A list of strings that serve as contextual information or knowledge for the LLM. These artifacts are used to guide and enrich the model's response.

#### ✅ Examples of artifacts:
- Requirement documents
- UML models or conceptual models
- Code snippets
- Error logs or debug messages
- Raw data samples

#### 📌 Example:
```json
"artifacts": [
  "Requirement: Users must register with name, email, and password. The email must be unique.",
  "Conceptual model: Entity 'User' has attributes 'id', 'name', 'email', 'password'.",
  "Code snippet: def validate_email(email): return '@' in email and '.' in email",
  "Error: Email 'test@example.com' already exists in the database."
]
```

---

### 2. `platform: str`

Defines which platform you intend to simulate or integrate with. Current options include:

- `"huggingface"`
- `"openai"`
- `"local"`
- `"ollama"`

#### 📌 Example:
```json
"platform": "huggingface"
```

---

### 3. `model: str`

Specifies the LLM model you want to use. Supported models:

- `"llama"`
- `"deepseek"`
- `"gpt"`
- `"mistral"`
- `"phi"`

#### 📌 Example:
```json
"model": "gpt"
```

---

### 4. `prompt: str`

A natural language instruction or question that defines the main task. The prompt is what the LLM will respond to, using the provided artifacts as context.

#### ✅ Examples of prompts:
- "Explain the email validation rule based on the artifacts."
- "Summarize the requirement document."
- "Generate 5 test cases for the login feature."
- "Analyze the error log and suggest causes."
- "Compare approaches A and B."

#### 📌 Example:
```json
"prompt": "Based on the provided artifacts, explain the email validation rule for user registration."
```

---

## 💡 Example JSON Request

```json
{
  "artifacts": [
    "Requirement: The user must be able to reset their password through a link sent via email.",
    "Code snippet: def send_reset_link(email): ..."
  ],
  "platform": "local",
  "model": "llama",
  "prompt": "Describe the password reset flow based on the requirement."
}
```

---

## 🚀 Future Directions

This microservice is currently offline and simulated, but it is designed to support future extensions, including:

- Real-time API integration with Hugging Face or OpenAI
- Dynamic model selection based on context
- Fine-tuned model support

---

## 📂 Repository Structure (optional suggestion)

```
llm-microservice/
├── app/
│   └── main.py
├── models/
│   └── llama.py
├── docs/
│   └── README.md
└── requirements.txt
```

---

## 🛠 How to Run (if applicable)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the microservice
python app/main.py
```

---

## 📬 Contact

For questions or contributions, please contact [your-email@example.com].
