# AI Fundamentals Handbook
### A Beginner-to-Medium Guide, Aligned with the AI Fundamentals Program with Azure

---

## Table of Contents

1. Welcome to the AI Fundamentals Program
2. Introduction to AI Fundamentals with Azure
3. AI and ML Core Concepts
4. Machine Learning
5. Computer Vision
6. Natural Language Processing
7. Conversational AI
8. Putting It All Together
9. Where to Go Next

---

## 1. Welcome to the AI Fundamentals Program

Welcome! This handbook is your companion through the AI Fundamentals Program. It's designed for beginners — no coding or data science background required to get started, though some sections (like Machine Learning) get slightly more hands-on.

**What to expect:**
- Simple explanations before technical detail
- Real-world examples for every concept
- Diagrams to visualize how each Azure AI service fits together
- A logical progression: core concepts → Machine Learning → Computer Vision → NLP → Conversational AI

**Ways to succeed:**
- Don't skip Section 3 (Core Concepts) — everything else builds on those terms.
- Try the examples described in each section, even mentally — asking "what would the input and output look like here?" cements the idea.
- Treat "Responsible AI" as a thread running through every section, not a one-time topic — it comes up again in Machine Learning, Computer Vision, and Conversational AI.

---

## 2. Introduction to AI Fundamentals with Azure

### Course overview

This program introduces the building blocks of AI and Machine Learning using **Microsoft Azure** as the platform. Azure provides pre-built AI services (so you don't need to build models from scratch) alongside tools for training your own custom models.

**Course structure at a glance:**

| Module | Focus |
|---|---|
| Core Concepts | Vocabulary and responsible AI principles |
| Machine Learning | Training and evaluating models with Azure Machine Learning |
| Computer Vision | Working with images using Azure Cognitive Services |
| Natural Language Processing | Working with text and speech |
| Conversational AI | Building bots powered by a knowledge base |

### Prerequisites

- Basic computer literacy (using a web browser, navigating a cloud portal)
- No prior programming or AI experience required
- An Azure account is helpful for hands-on practice (a free tier is available), but this handbook explains concepts even if you're reading without one

### A short history: how AI and ML developed

- **1950s** — Alan Turing proposes the idea of a machine that can "think" (the Turing Test).
- **1980s–90s** — Expert systems and early pattern-recognition approaches emerge, but are limited by hand-coded rules.
- **2000s** — Machine Learning gains traction as data and computing power grow — instead of hand-coding rules, systems learn patterns from data.
- **2010s** — Deep Learning (neural networks with many layers) drives breakthroughs in image recognition, speech, and translation.
- **Today** — Cloud platforms like Azure package these advances into ready-to-use services, so developers can add AI capabilities without building models from scratch.

**Simple example:** Predicting whether an email is spam used to require someone to write rules like "if it contains the word 'free', mark as spam." Modern ML instead *learns* what spam looks like from thousands of labeled examples.

---

## 3. AI and ML Core Concepts

### Key terms

| Term | Simple meaning | Example |
|---|---|---|
| **Artificial Intelligence (AI)** | Machines performing tasks that normally require human intelligence | A car that can recognize stop signs |
| **Machine Learning (ML)** | A way of achieving AI by learning patterns from data, rather than following hard-coded rules | A model that learns to predict house prices from past sales |
| **Deep Learning** | ML using layered neural networks, good at complex patterns like images and speech | Facial recognition in photos |
| **Model** | The trained "brain" that makes predictions | A trained spam-detection model |
| **Training data** | The examples used to teach a model | 10,000 labeled emails (spam / not spam) |
| **Features** | The input variables a model uses to make predictions | House size, location, number of bedrooms |
| **Label** | The correct answer used during training (in supervised learning) | "spam" or "not spam" |
| **Algorithm** | The method used to find patterns in data | Linear regression, decision trees, neural networks |

### How AI, ML, and Deep Learning relate

![AI, ML, and Deep Learning](ai_fundamentals_images/d1_ai_ml_dl.png)

Deep Learning is a subset of Machine Learning, and Machine Learning is a subset of AI. Not all AI uses ML (some AI is rule-based), and not all ML uses Deep Learning (many models use simpler algorithms).

### Types of Machine Learning

| Type | How it works | Example |
|---|---|---|
| **Supervised learning** | Learns from labeled examples (input + correct answer) | Predicting house prices from past sales with known prices |
| **Unsupervised learning** | Finds patterns in data without labels | Grouping customers into segments based on shopping habits |
| **Reinforcement learning** | Learns by trial and error, getting rewards/penalties | A game-playing AI that improves by playing many rounds |

### Responsible AI

Responsible AI is a set of principles to make sure AI systems are built and used ethically. Microsoft's Responsible AI principles (used throughout Azure's AI tools) include:

- **Fairness** — the model shouldn't discriminate against groups of people (e.g., a loan-approval model shouldn't be biased by race or gender).
- **Reliability & safety** — the system should perform consistently and safely, especially in critical use cases (e.g., a medical diagnosis tool).
- **Privacy & security** — personal data used to train or run models must be protected.
- **Inclusiveness** — AI systems should be usable by people of all abilities and backgrounds.
- **Transparency** — people should understand how and why an AI system made a decision.
- **Accountability** — there should be humans responsible for how an AI system behaves.

**Simple example of why this matters:** If a hiring model is trained mostly on resumes from one demographic, it may unfairly favor similar candidates in the future — this is a fairness problem that Responsible AI practices aim to catch before deployment.

---

## 4. Machine Learning

### Training and evaluating models with Azure Machine Learning

Azure Machine Learning (Azure ML) is a cloud service for building, training, and deploying ML models — either by writing code or using no-code/low-code tools.

### The basic ML workflow

![Machine Learning workflow](ai_fundamentals_images/d2_ml_workflow.png)

**Simple example — predicting house prices:**
1. **Collect data:** past home sales with size, location, number of bedrooms, and sale price.
2. **Prepare data:** remove incomplete records, split into a training set (80%) and a test set (20%).
3. **Train a model:** the algorithm learns the relationship between features (size, location) and the label (price).
4. **Evaluate:** check how close the model's predictions are to actual prices in the test set.
5. **Deploy:** publish the model as a web endpoint other applications can call.
6. **Predict:** a real-estate app sends a new house's details and receives a predicted price.

### Automated Machine Learning (AutoML)

AutoML automatically tries multiple algorithms and settings, then picks the best-performing model — without you manually testing each one.

**Example:** You upload a dataset of customer churn (whether a customer canceled their subscription). AutoML tries logistic regression, decision trees, and several other algorithms, then reports which one predicts churn most accurately — all without you writing training code.

### Azure Machine Learning Designer

The ML Designer is a drag-and-drop, visual interface for building ML pipelines — connecting boxes for data input, data cleaning, training, and evaluation, without writing code.

**Example pipeline (described in words):**
```
[Import Data] → [Clean Missing Data] → [Split Data (train/test)]
      → [Train Model] → [Score Model] → [Evaluate Model]
```
Each box is dragged onto a canvas and connected with arrows — useful for beginners who want to understand the ML process visually before writing code.

### Key evaluation metrics (simplified)

| Metric | Used for | Simple meaning |
|---|---|---|
| **Accuracy** | Classification | % of predictions that were correct |
| **Precision** | Classification | Of the times the model said "yes," how often was it right? |
| **Recall** | Classification | Of all the actual "yes" cases, how many did the model catch? |
| **Mean Absolute Error (MAE)** | Regression (predicting numbers) | On average, how far off were the predictions? |

**Example:** A model predicting house prices with an MAE of $10,000 means, on average, its predictions are off by about $10,000 — useful for judging if the model is "good enough" for real use.

---

## 5. Computer Vision

### Azure Cognitive Services for image-based workloads

Computer Vision lets applications "see" and interpret visual information — photos, video frames, or scanned documents — without you building an image-recognition model from scratch.

![Computer Vision workloads](ai_fundamentals_images/d3_computer_vision.png)

### Key workloads

**1. Image Classification**
Assigns a single label (or a few) to an entire image.
*Example:* Upload a photo → service returns `"cat"` with 96% confidence.

**2. Object Detection**
Finds multiple objects within an image and draws a bounding box around each.
*Example:* A photo of a kitchen returns boxes around `"refrigerator"`, `"table"`, and `"chair"`, each with its own confidence score.

**3. Face Detection**
Locates faces in an image and can analyze attributes like approximate age range or emotion (subject to Responsible AI limits on sensitive attribute detection).
*Example:* A photo of a group returns 4 detected faces, each with a bounding box.

**4. Text Analysis (OCR — Optical Character Recognition)**
Reads printed or handwritten text within an image.
*Example:* A photo of a street sign returns the extracted text: `"Main Street"`.

**5. Form Processing**
Extracts structured data (fields, tables, key-value pairs) from documents like invoices or receipts.
*Example:* A scanned invoice returns structured fields: `Vendor: Acme Corp`, `Total: $452.00`, `Date: 2026-03-14` — instead of just raw text.

### Simple example scenario

A retail company wants to process thousands of scanned receipts. Instead of manually typing each one into a spreadsheet:
1. Each receipt image is sent to a Form Processing model.
2. The model extracts vendor name, date, and total automatically.
3. Results are saved directly into the company's expense system.

This turns a manual task (hours of typing) into an automated one (seconds per receipt).

---

## 6. Natural Language Processing

### Working with text and speech

Natural Language Processing (NLP) allows applications to understand, analyze, and generate human language — both written text and spoken audio.

![NLP capabilities](ai_fundamentals_images/d4_nlp.png)

### Key capabilities

**1. Sentiment Analysis / Intent Recognition**
Determines whether text expresses positive, negative, or neutral sentiment — or what the user is trying to do.
*Example:* "This product broke after one day!" → sentiment: **negative**.
*Example (intent):* "Book me a flight to Paris" → intent: **BookFlight**, entity: **destination = Paris**.

**2. Key Phrase Extraction**
Pulls out the main topics or phrases from a block of text.
*Example:* "The battery life on this laptop is amazing, but the screen is too dim" → key phrases: `battery life`, `screen brightness`.

**3. Speech-to-Text and Text-to-Speech**
Converts spoken audio into written text, and vice versa.
*Example:* A voice memo saying "Remind me to call mom at 5pm" is transcribed into text a scheduling app can act on.

**4. Translation**
Translates text or speech between languages.
*Example:* "Where is the nearest train station?" → Spanish: "¿Dónde está la estación de tren más cercana?"

### Simple example scenario

A customer support team receives thousands of chat messages daily. Using NLP:
1. Each incoming message is analyzed for **sentiment** — flagging angry customers for priority handling.
2. **Key phrases** are extracted to tag common issues (e.g., "refund", "shipping delay").
3. Non-English messages are automatically **translated** so any agent can respond, regardless of language.

---

## 7. Conversational AI

### Building a knowledge base and a bot

Conversational AI lets users interact with a system through natural conversation — typically via a chatbot — instead of navigating menus or forms.

![Conversational AI flow](ai_fundamentals_images/d5_conversational_ai.png)

### Step 1: Create a knowledge base (Question & Answer pairs)

A knowledge base is a structured set of questions and their matching answers, often built from an FAQ page or support documentation.

**Example knowledge base entries:**

| Question | Answer |
|---|---|
| What are your store hours? | We're open 9am–5pm, Monday to Friday. |
| How do I reset my password? | Go to Settings > Account > Reset Password. |
| Do you offer refunds? | Yes, within 30 days of purchase with a receipt. |

The knowledge base service matches a user's question (even if worded differently) to the closest known question-answer pair.

**Example of matching flexibility:** A user asking "When are you open?" should still match the "store hours" entry, even though the wording is different — the service uses language understanding, not exact text matching.

### Step 2: Build a bot on top of the knowledge base

A bot is the conversational interface — it receives user messages, queries the knowledge base for the best-matching answer, and replies.

**Simple example conversation:**
```
User: Hey, can I get my money back for a shirt I bought last week?
Bot:  Yes, we offer refunds within 30 days of purchase with a receipt.
```

### Where bots typically live

Bots built this way can be published to multiple channels — a website chat widget, Microsoft Teams, Slack, or a mobile app — without rebuilding the underlying knowledge base for each one.

### Simple example scenario

A university wants to reduce repetitive emails to its admissions office:
1. Staff create a knowledge base from the "Frequently Asked Questions" page (application deadlines, required documents, tuition costs).
2. A bot is connected to this knowledge base and published on the university's website.
3. Prospective students get instant answers to common questions, and staff only handle unique, complex questions.

---

## 8. Putting It All Together

Here's how the modules connect in a realistic project — an AI-powered customer service platform for an online retailer:

| Need | Azure AI Area Used |
|---|---|
| Predict which customers are likely to churn | Machine Learning (Azure ML / AutoML) |
| Read and extract data from scanned return-request forms | Computer Vision (Form Processing) |
| Detect angry customers from support chat messages | Natural Language Processing (Sentiment Analysis) |
| Answer common customer questions instantly | Conversational AI (Knowledge Base + Bot) |
| Ensure the churn-prediction model isn't biased against any customer group | Responsible AI principles (Core Concepts) |

No single module solves the whole problem — real systems typically combine several Azure AI services, guided by Responsible AI principles throughout.

---

## 9. Where to Go Next

**Suggested learning path:**
1. Set up a free Azure account and explore the Azure Machine Learning Studio interface.
2. Try training a simple model using AutoML on a small sample dataset (e.g., predicting Titanic survival — a common beginner dataset).
3. Experiment with a Computer Vision demo (many Azure Cognitive Services offer a browser-based "try it out" demo without writing code).
4. Build a small knowledge base and connect it to a bot using Azure's QnA and Bot Service tools.
5. Revisit the Responsible AI principles in Section 3 and consider how they'd apply to a project you're interested in building.

**Good habits going forward:**
- Always ask "what data was this trained on?" before trusting a model's output.
- Start with pre-built Cognitive Services before building custom models — they cover a large percentage of common use cases.
- Treat evaluation metrics (accuracy, precision, recall, MAE) as a checklist, not a single number — a model can look "accurate" overall while performing poorly for a specific group or scenario.

---

*End of Handbook*
