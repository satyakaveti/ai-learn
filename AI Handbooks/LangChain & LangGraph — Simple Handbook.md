# LangChain & LangGraph — Simple Handbook


# LangChain vs LangGraph — Detailed Explanation

To understand the difference, think of building an AI application that can answer questions, call APIs, retrieve information from databases, make decisions, and execute multi-step tasks.

LangChain helps you build the components that interact with an LLM. LangGraph helps you control how those components execute as a workflow or AI agent. They complement each other rather than compete.

## 1. What is LangChain?

LangChain is an open-source framework for building applications powered by Large Language Models (LLMs), such as Llama, GPT, and models accessed through Groq Cloud.

Without a framework, you would need to write code to call model APIs, construct prompts, parse responses, integrate tools, retrieve documents, and manage conversation history. LangChain provides reusable abstractions for these tasks.

### Core components of LangChain
 <img width="624" height="574" alt="image" src="https://github.com/user-attachments/assets/85d543b8-0b82-4fda-8dec-24df10c180e5" />


### Important LangChain concepts

| Component        | Purpose                                   | Example                              |
| ---------------- | ----------------------------------------- | ------------------------------------ |
| Chat models      | Connect to an LLM                         | `ChatGroq`                           |
| Prompt templates | Construct reusable prompts                | `ChatPromptTemplate`                 |
| Output parsing   | Validate or transform output              | Pydantic, structured output          |
| Chains / LCEL    | Connect processing steps                  | <code>prompt \\\| model</code>       |
| Tools            | Expose Python functions or APIs to models | `@tool`, `bind_tools()`              |
| RAG              | Ground responses in external documents    | Retriever + model                    |
| Message history  | Retain conversational context             | Previous user and assistant messages |

 LangChain provides components for document loading, splitting, embedding integration, retrieval, and model interaction. You still need to choose and configure the actual embedding model and vector store.

## 2. What is LangGraph?

LangGraph is a framework for building stateful, multi-step workflows and AI agents. It represents the application as a graph of nodes and edges.

* Nodes perform work: call an LLM, execute a tool, validate data, or run business logic.

* Edges determine which node runs next.

* State holds the information shared across the workflow.

* Conditional edges select the next step based on a decision.

* Checkpoints save workflow state so execution can resume later.

Unlike a simple sequence of operations, a LangGraph workflow can branch, loop, pause, and resume.

### Core architecture of LangGraph
 <img width="624" height="469" alt="image" src="https://github.com/user-attachments/assets/f631bdc0-37ee-4bbb-a623-985720d0ad76" />


### The five essential concepts

| Concept      | Meaning                                                  |
| ------------ | -------------------------------------------------------- |
| `StateGraph` | Defines the workflow graph                               |
| State        | Holds inputs, messages, results, and other workflow data |
| Nodes        | Execute individual steps                                 |
| Edges        | Connect nodes and control transitions                    |
| Checkpointer | Saves graph state at execution checkpoints               |

LangGraph also supports streaming, human-in-the-loop interruptions, and subgraphs. These capabilities are particularly valuable for long-running or sensitive workflows.

 

## 3. LangChain vs LangGraph — Detailed comparison

| Area                | LangChain                                            | LangGraph                                                                   |
| ------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------- |
| Primary role        | LLM application building blocks                      | Workflow and agent orchestration                                            |
| Main abstraction    | Models, prompts, tools, retrievers, runnables        | Graphs, nodes, edges, state                                                 |
| Execution           | Often a sequence of components or an agent loop      | Explicit workflow with branching and looping                                |
| Tool execution      | Tool integration and agent abstractions              | Can route to tool nodes and manage repeated execution                       |
| State               | Conversation history and application state utilities | Shared graph state updated throughout execution                             |
| Persistence         | Depends on the component and storage approach        | Checkpoint-based persistence integrated into graph execution                |
| Human approval      | Can be implemented by application code               | Supports interrupt-and-resume workflows                                     |
| Workflow complexity | Ideal for direct LLM tasks and reusable components   | Ideal for complex, stateful, branching workflows                            |
| Can it work alone?  | Yes                                                  | Yes, with a compatible model integration; LangChain components are optional |

One important distinction: LangChain is not limited to simple chains. It also offers agent-building abstractions. LangGraph provides more explicit control when you need to define and manage a workflow's execution in detail.

## 5. When should you use each one?

Use LangChain

* Simple question-answering chatbot

* Summarizing text or documents

* Extracting structured JSON from text

* RAG over PDFs or internal documents

* Integrating an LLM with APIs or databases

Use LangGraph

* Agents that repeatedly call tools until a task is complete

* Workflows with branching decisions

* Multi-step business processes

* Human approval before executing sensitive operations

* Long-running workflows that need persistence and resumption

* Multi-agent systems with specialized agents



**Step 1 — Create a project folder and virtual environment** (Python 3.10 or above):

```bash
mkdir langchain-handbook && cd langchain-handbook
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate
```

**Step 2 — Install the packages** (one time only):

```bash
pip install -U langchain langchain-core langchain-groq langgraph \
  langchain-community langchain-text-splitters langchain-huggingface \
  langchain-chroma sentence-transformers pypdf python-dotenv \
  langgraph-checkpoint-sqlite streamlit
```

**Step 3 — Get a free Groq API key** from console.groq.com → API Keys → Create. Copy it immediately; it is shown only once.

**Step 4 — Keep the key in a `.env` file**, never hard-code it in source, and add `.env` to `.gitignore`:

```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
# optional, for tracing (topic 9 and LangGraph topic 10)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_xxxxxxxx
LANGSMITH_PROJECT=langchain-handbook
```

**Step 5 — Smoke test.** Save as `hello.py` and run `python hello.py`. If you get a reply, your setup is ready, no tension.

```python
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()  # reads GROQ_API_KEY from .env
llm = ChatGroq(model="llama-3.3-70b-versatile")
print(llm.invoke("Say namaste in one line").content)
```

Note: Groq model names change from time to time. If a model is decommissioned, simply check the Models page on console.groq.com and replace the name. All code in this book uses the same `llm` object, so you change it in one place only.

### Connecting to Groq models (used everywhere in this book)

Every chat model in this handbook runs on Groq through the `langchain-groq` package. Groq hosts open models (Llama, GPT-OSS, Qwen and others) on its fast LPU hardware, and LangChain talks to it through the `ChatGroq` class.

**Step A — Create one shared helper `groq_llm.py`** and import it in every topic and project, so the model name and settings live in one place only:

```python
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY missing. Add it to your .env file.")

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "llama-3.1-8b-instant")

def get_llm(model: str = DEFAULT_MODEL, temperature: float = 0, **kwargs) -> ChatGroq:
    """Return a configured Groq chat model."""
    return ChatGroq(
        model=model,
        temperature=temperature,
        max_tokens=kwargs.pop("max_tokens", 1024),
        timeout=kwargs.pop("timeout", 30),
        max_retries=kwargs.pop("max_retries", 2),
        **kwargs,
    )

llm = get_llm()              # big, smart model for answers and agents
fast_llm = get_llm(FAST_MODEL)  # small, cheap model for routing and classification
```

After this, wherever the book shows `llm = ChatGroq(...)`, you can simply write `from groq_llm import llm` (or `get_llm(temperature=0.7)` for creative work).

**Step B — Choose the right Groq model:**

| Model id | Size / speed | Use it for |
| --- | --- | --- |
| `llama-3.3-70b-versatile` | Large, good quality | Default for chat, RAG answers, tool-calling agents |
| `llama-3.1-8b-instant` | Small, very fast, cheapest | Routers, classifiers, fallback model, simple summaries |
| `openai/gpt-oss-120b` | Large reasoning model | Harder multi-step reasoning and planning |

Groq adds and retires models regularly, so confirm the ids on console.groq.com → Models before you start. Change only `GROQ_MODEL` in `.env`; no code change needed.

**Step C — List the models your key can use** (quick check that the connection works):

```python
import os, requests
from dotenv import load_dotenv

load_dotenv()
resp = requests.get("https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
                    timeout=10)
for m in resp.json()["data"]:
    print(m["id"])
```

**Step D — Know the Groq-specific points:**

- **Tool calling and structured output:** use a model that supports tool use (the Llama 3.3 70B and GPT-OSS models do). `bind_tools()` and `with_structured_output()` then work exactly as shown in the topics.
- **Rate limits:** the free tier limits requests and tokens per minute. If you see HTTP 429, keep `max_retries`, slow down `batch()` with `config={"max_concurrency": 2}`, or fall back to `fast_llm`.
- **Embeddings:** Groq does not offer embedding models. So in RAG (topic 8 and Project 2) Groq generates the answers, while a free local HuggingFace model creates the embeddings. This is the normal, recommended combination.
- **Provider-independent style:** `init_chat_model("groq:llama-3.3-70b-versatile")` also connects to Groq, if you prefer a config string.

# Part 1 — LangChain

## 1. LLM fundamentals

An LLM is a very big next-word predictor: you give text, it predicts the most likely next token, again and again, until the answer is complete. Everything else in LangChain is built on top of this one simple idea.

| Term | Simple meaning | Why you should care |
| --- | --- | --- |
| Token | A piece of a word; roughly 1 token ≈ 4 English characters or ¾ of a word | Billing, speed and limits are all counted in tokens, not words |
| Context window | Maximum tokens the model can see at one time (prompt + history + answer) | Long chat history or big PDFs will overflow it; that is why we need RAG and trimming |
| Temperature | Randomness knob, usually 0 to 1 | 0 = same answer every time (good for JSON, extraction); 0.7+ = creative (stories, ideas) |
| max\_tokens | Upper limit on answer length | Prevents very long, costly replies |
| Inference | One call to the model to generate output | Every `invoke()` is one inference; it costs money and time |
| API key | Secret password for the provider | Keep in `.env`, never commit to Git |

**Key points to remember:**

- LLMs are stateless. The model does not remember your previous message; you must send the history every time (topic 6).
- LLMs do not know your private data or today's news. You give that data inside the prompt (topic 8, RAG).
- LLMs cannot run code or call APIs themselves. They only *ask* for a tool call; your code runs it (topic 7).
- Output is text. If you want structured data, you must ask for it and parse it (topic 4).

**Practice:** Run the `hello.py` from setup three times with `temperature=0` and three times with `temperature=1`. You will see the difference with your own eyes.

## 2. Chat Models

A chat model takes a list of messages and returns one `AIMessage`. In LangChain every provider (Groq, OpenAI, Anthropic, Ollama) has the same interface, so you can swap providers by changing just one line.

**Configure the model:**

```python
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,      # deterministic
    max_tokens=512,     # answer length limit
    timeout=30,         # seconds
    max_retries=2,      # auto retry on network errors
)
```

**The three ways to call any model (remember this, it is the same for chains and graphs also):**

```python
# 1. invoke() — one input, one output
resp = llm.invoke("What is RAG in one line?")
print(resp.content)          # the text
print(resp.usage_metadata)   # {'input_tokens': .., 'output_tokens': .., 'total_tokens': ..}

# 2. batch() — many inputs in parallel, output list in same order
answers = llm.batch(["Capital of India?", "Capital of Japan?"])
for a in answers:
    print(a.content)

# 3. stream() — tokens come one by one, like ChatGPT typing effect
for chunk in llm.stream("Write 3 lines on Hyderabad biryani"):
    print(chunk.content, end="", flush=True)
```

Async versions are also there: `ainvoke()`, `abatch()`, `astream()` — use them inside FastAPI or any async web app.

**Provider-independent way** (useful when you want config-driven model choice, like Spring profiles):

```python
from langchain.chat_models import init_chat_model
llm = init_chat_model("groq:llama-3.3-70b-versatile", temperature=0)
```

**Practice:** Ask the same question with `invoke()` and `stream()`, and print `usage_metadata` for both.

## 3. Prompt Templates

A prompt template is a reusable prompt with `{placeholders}`, exactly like a `String.format()` or a Thymeleaf template. You write it once and fill different values every time.

**Message types** — every chat is a list of these:

| Message | Who says it | Use |
| --- | --- | --- |
| `SystemMessage` | You (the developer) | Sets role and rules: "You are a strict code reviewer" |
| `HumanMessage` | The user | The actual question |
| `AIMessage` | The model | The model's previous replies |
| `ToolMessage` | Your code | Result of a tool call (topic 7) |

**Direct messages (no template):**

```python
from langchain_core.messages import SystemMessage, HumanMessage

msgs = [
    SystemMessage(content="You are a helpful Java mentor. Answer in 3 lines."),
    HumanMessage(content="What is dependency injection?"),
]
print(llm.invoke(msgs).content)
```

**PromptTemplate** — for plain single-string prompts:

```python
from langchain_core.prompts import PromptTemplate

pt = PromptTemplate.from_template("Explain {topic} to a {level} developer in 2 lines.")
print(pt.invoke({"topic": "Kafka", "level": "fresher"}).to_string())
```

**ChatPromptTemplate** — the one you will use 90% of the time:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Reply in {language}."),
    MessagesPlaceholder("history", optional=True),  # slot for old messages (topic 6)
    ("human", "{question}"),
])

filled = prompt.invoke({
    "role": "travel guide",
    "language": "simple English",
    "question": "Best time to visit Kerala?",
})
print(llm.invoke(filled).content)
```

**Good prompt habits:** give a clear role, give the output format, give one example if format is tricky, and tell what NOT to do ("If you don't know, say I don't know").

**Practice:** Build a template that takes `{code}` and `{language}` and returns a code review with exactly 3 bullet points.

## 4. Output Parsers & Structured Output

For real applications you need data, not paragraphs. The best way today is `with_structured_output()` with a Pydantic class — it is like mapping JSON to a Java POJO with Jackson, but the LLM fills the fields.

**Way 1 — StrOutputParser** (just get clean text instead of an AIMessage object):

```python
from langchain_core.output_parsers import StrOutputParser
text = (llm | StrOutputParser()).invoke("Say hi")   # plain str
```

**Way 2 — JsonOutputParser** (when you only need a dict):

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

parser = JsonOutputParser()
prompt = ChatPromptTemplate.from_template(
    "Give name and capital of {country}.\n{format_instructions}"
).partial(format_instructions=parser.get_format_instructions())

print((prompt | llm | parser).invoke({"country": "India"}))
# {'name': 'India', 'capital': 'New Delhi'}
```

**Way 3 — with\_structured\_output() + Pydantic (recommended):**

```python
from pydantic import BaseModel, Field
from typing import Literal

class BugReport(BaseModel):
    """Structured details extracted from a bug description."""
    title: str = Field(description="Short title, max 8 words")
    severity: Literal["low", "medium", "high", "critical"]
    component: str = Field(description="Affected module name")
    steps: list[str] = Field(description="Steps to reproduce")

extractor = llm.with_structured_output(BugReport)
bug = extractor.invoke(
    "Login page crashes with NullPointerException when password is empty. "
    "Happens in auth-service on every attempt, users are fully blocked."
)
print(bug.severity)       # 'critical'
print(bug.model_dump())   # normal dict, ready to save in DB
```

**Tips:**

- Field `description` text goes to the model, so write it clearly — it works like an instruction.
- Use `temperature=0` for extraction work.
- Use `Literal[...]` or `Enum` to restrict values; the model cannot invent new ones easily.
- Wrap in try/except — if the model returns bad data, Pydantic raises `ValidationError` (see topic 9).

**Practice:** Extract `name`, `email`, `skills: list[str]` and `years_of_experience: int` from a pasted resume paragraph.

## 5. Chains & LCEL

LCEL (LangChain Expression Language) means joining components with the `|` pipe, so the output of the left side becomes the input of the right side. Every piece is a **Runnable**, and every Runnable has `invoke`, `batch` and `stream` — so a full chain also streams and batches for free.

**Basic chain = prompt | model | parser:**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Write a tweet about {topic}")
chain = prompt | llm | StrOutputParser()   # this is a RunnableSequence

print(chain.invoke({"topic": "monsoon in Mumbai"}))
```

The `|` above is just a short form of `RunnableSequence(prompt, llm, StrOutputParser())`.

**Important Runnables you must know:**

| Runnable | What it does | Typical use |
| --- | --- | --- |
| `RunnablePassthrough()` | Passes input as-is | Carry the user question forward in RAG |
| `RunnablePassthrough.assign(x=...)` | Adds a new key, keeps old keys | Enrich the input dict step by step |
| `RunnableParallel({...})` or a plain dict | Runs branches in parallel, returns dict | Fetch context and question together |
| `RunnableLambda(func)` | Wraps any Python function | Custom cleaning, formatting, logging |

**Composition example — two chains joined together:**

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Chain A: make a short outline
outline = (ChatPromptTemplate.from_template("Give a 3-point outline on {topic}")
           | llm | StrOutputParser())

# Chain B: write the blog using that outline
blog = (ChatPromptTemplate.from_template("Write a 120-word blog on {topic} using:\n{outline}")
        | llm | StrOutputParser())

full = (
    RunnablePassthrough.assign(outline=outline)   # adds 'outline' key, keeps 'topic'
    | blog
    | RunnableLambda(lambda s: s.strip().upper()[:50] + "...")  # any custom function
)
print(full.invoke({"topic": "UPI payments"}))
```

**Parallel example:**

```python
from langchain_core.runnables import RunnableParallel

both = RunnableParallel(
    pros=ChatPromptTemplate.from_template("2 pros of {x}") | llm | StrOutputParser(),
    cons=ChatPromptTemplate.from_template("2 cons of {x}") | llm | StrOutputParser(),
)
print(both.invoke({"x": "remote work"}))   # {'pros': '...', 'cons': '...'}
```

**Practice:** Make a chain that translates English to Telugu, then a second step that counts the words using `RunnableLambda`.

## 6. Conversation Memory

Since the LLM is stateless, "memory" simply means: store old messages and send them again with every new question. You keep one history per user/session, like an `HttpSession` in Spring.

**Level 1 — manual list (understand the idea):**

```python
from langchain_core.messages import HumanMessage, AIMessage

history = []
for q in ["My name is Maneesha", "What is my name?"]:
    history.append(HumanMessage(q))
    ans = llm.invoke(history)
    history.append(ans)
    print(ans.content)
```

**Level 2 — RunnableWithMessageHistory (automatic, per session):**

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant."),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])
chain = prompt | llm

store = {}   # session_id -> history object
def get_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chat = RunnableWithMessageHistory(
    chain, get_history,
    input_messages_key="input",
    history_messages_key="history",
)

cfg = {"configurable": {"session_id": "user-101"}}
chat.invoke({"input": "I live in Hyderabad"}, config=cfg)
print(chat.invoke({"input": "Where do I live?"}, config=cfg).content)
```

**Level 3 — persistent history (survives restart):** just change the history class. Example with SQLite:

```python
from langchain_community.chat_message_histories import SQLChatMessageHistory

def get_history(session_id: str):
    return SQLChatMessageHistory(session_id=session_id,
                                 connection="sqlite:///chat_history.db")
```

Redis, Postgres and MongoDB versions are also available in `langchain_community`.

**Keep the history small** — otherwise you cross the context window and pay more. Use `trim_messages` to keep only recent tokens:

```python
from langchain_core.messages import trim_messages
trimmer = trim_messages(max_tokens=1000, strategy="last",
                        token_counter=llm, include_system=True)
```

Note: for new agent-style apps, LangGraph checkpointers (LangGraph topic 6) are the modern way to store memory. Learn this topic for understanding and for simple chains.

**Practice:** Run two different `session_id`s and confirm one user cannot see the other's history.

## 7. Tools & Function Calling

A tool is a normal Python function that the LLM is allowed to request. The model never runs it — it only returns "please call `get_weather` with city=Hyderabad"; your code runs the function and sends the result back as a `ToolMessage`.

**Step 1 — Define tools with `@tool`.** The docstring and type hints become the tool schema, so write them properly:

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"It is 31°C and sunny in {city}."   # dummy; call a real API later

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

print(multiply.name, multiply.args)   # see the schema LangChain created
```

**Step 2 — Bind tools to the model:**

```python
llm_with_tools = llm.bind_tools([get_weather, multiply])
ai_msg = llm_with_tools.invoke("What is 12.5 times 8, and weather in Chennai?")
print(ai_msg.tool_calls)
# [{'name': 'multiply', 'args': {'a': 12.5, 'b': 8}, 'id': 'call_1'},
#  {'name': 'get_weather', 'args': {'city': 'Chennai'}, 'id': 'call_2'}]
```

**Step 3 — Run the tools and send results back:**

```python
from langchain_core.messages import HumanMessage

tools_by_name = {"get_weather": get_weather, "multiply": multiply}
messages = [HumanMessage("What is 12.5 times 8, and weather in Chennai?"), ai_msg]

for call in ai_msg.tool_calls:
    tool_msg = tools_by_name[call["name"]].invoke(call)   # returns a ToolMessage
    messages.append(tool_msg)

final = llm_with_tools.invoke(messages)
print(final.content)   # natural answer using both tool results
```

**Tool schema with Pydantic** (when you need validations or descriptions per argument):

```python
from pydantic import BaseModel, Field

class OrderLookup(BaseModel):
    order_id: str = Field(description="Order ID like ORD-1234")

@tool(args_schema=OrderLookup)
def get_order_status(order_id: str) -> str:
    """Look up the delivery status of an order."""
    return "Shipped, arriving tomorrow"
```

**Things to remember:** one clear job per tool; good names and docstrings (the LLM chooses by reading them); return short strings or JSON; never give a tool more power than needed (no DELETE queries for a read-only assistant). Doing this loop by hand is boring — LangGraph's `ToolNode` automates it (LangGraph topic 5).

**Practice:** Create a `convert_currency(amount, from_cur, to_cur)` tool with fixed rates and ask "How much is 100 USD in INR?"

## 8. Retrieval & RAG

RAG (Retrieval-Augmented Generation) = first search your own documents for the relevant pieces, then give only those pieces to the LLM along with the question. This way the model answers from your data, with less hallucination, and you don't cross the context window.

RAG has two phases:

1. **Indexing (one time):** Load documents → split into chunks → convert chunks to embeddings → store in a vector database.
2. **Querying (every question):** Convert question to embedding → find the most similar chunks → put them in the prompt → LLM answers.

| Building block | Simple meaning | Example class |
| --- | --- | --- |
| Document loader | Reads files into `Document(page_content, metadata)` objects | `PyPDFLoader`, `TextLoader`, `WebBaseLoader`, `CSVLoader` |
| Text splitter | Cuts long text into overlapping chunks | `RecursiveCharacterTextSplitter` |
| Embeddings | Converts text into a list of numbers (vector); similar meaning = nearby vectors. Groq has no embedding models, so we use a free local one; Groq still answers | `HuggingFaceEmbeddings` (free, local) |
| Vector database | Stores vectors and does similarity search | `Chroma`, `FAISS`, `PGVector`, Pinecone |
| Retriever | Simple interface: question in, top-k documents out | `vectorstore.as_retriever()` |

**Full mini RAG (works with any text file):**

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- Indexing ---
docs = TextLoader("company_policy.txt", encoding="utf-8").load()
chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(docs)
emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vs = Chroma.from_documents(chunks, emb, persist_directory="./chroma_db")
retriever = vs.as_retriever(search_kwargs={"k": 4})

# --- Querying ---
prompt = ChatPromptTemplate.from_template(
    "Answer ONLY from the context. If not found, say 'Not in the document'.\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)
def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)
print(rag_chain.invoke("How many leaves per year?"))
```

**Tuning tips:**

- `chunk_size` 500–1000 characters with 10–20% overlap is a good starting point.
- `k` = 3 to 5 chunks normally; too many chunks confuse the model.
- Use `search_type="mmr"` in `as_retriever()` to avoid near-duplicate chunks.
- Keep `metadata` (file name, page number) so you can show sources to the user.
- Next time, load the saved DB instead of re-embedding: `Chroma(persist_directory="./chroma_db", embedding_function=emb)`.

**Practice:** Index two text files and print `metadata["source"]` of the retrieved chunks for each question.

## 9. Error Handling & Callbacks

LLM calls fail more often than normal REST calls — rate limits, timeouts, bad JSON. Production code must expect this, the same way you handle a flaky downstream service with Resilience4j.

**Timeouts and built-in retries** (at model level):

```python
llm = ChatGroq(model="llama-3.3-70b-versatile", timeout=30, max_retries=3)
```

**Retry any Runnable or chain** with backoff:

```python
safe_chain = chain.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
    retry_if_exception_type=(TimeoutError, ConnectionError),
)
```

**Fallback to another model** if the first one keeps failing:

```python
backup = ChatGroq(model="llama-3.1-8b-instant")
robust_llm = llm.with_fallbacks([backup])
```

**Catch parsing errors** from structured output:

```python
from pydantic import ValidationError
try:
    bug = extractor.invoke(text)
except ValidationError as e:
    print("Model returned bad data:", e)
    bug = None   # or retry with a stricter prompt
```

**Callbacks — logging and token usage.** A callback handler gets events like start, end and error for every LLM call:

```python
import logging
from langchain_core.callbacks import BaseCallbackHandler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("llm")

class LogHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        log.info("LLM call started")
    def on_llm_end(self, response, **kwargs):
        msg = response.generations[0][0].message
        log.info("Tokens used: %s", msg.usage_metadata)
    def on_llm_error(self, error, **kwargs):
        log.error("LLM failed: %s", error)

chain.invoke({"topic": "AI"}, config={"callbacks": [LogHandler()]})
```

**Total token usage across many calls:**

```python
from langchain_core.callbacks import UsageMetadataCallbackHandler
cb = UsageMetadataCallbackHandler()
chain.invoke({"topic": "AI"}, config={"callbacks": [cb]})
print(cb.usage_metadata)   # tokens per model name
```

**Tracing with LangSmith (strongly recommended):** just set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` in `.env` (see setup). Every chain, prompt, tool call, latency and token count then appears in the LangSmith web UI — no code change needed. This is the fastest way to debug "why did the model say this?"

**Practice:** Set `timeout=0.01` deliberately, add `with_fallbacks`, and confirm the backup model answers.

# Part 2 — LangGraph

## 1. LangGraph fundamentals

LangGraph builds your app as a graph: **nodes** are Python functions that do work, **edges** decide which node runs next, and a shared **state** object flows through all of them. LCEL chains go only in a straight line; a graph can branch, loop and pause — that is why agents are built with LangGraph.

| Concept | Meaning | Java/Spring analogy |
| --- | --- | --- |
| `StateGraph` | The graph builder | A workflow / state-machine config |
| State | Shared dict passed to every node | A DTO passed along a pipeline |
| Node | Function `state -> partial update` | A service method |
| Edge | Fixed "after A go to B" | Next step in the pipeline |
| `START` / `END` | Special entry and exit points | Controller entry / return |
| `compile()` | Validates and builds a runnable app | Application context startup |

**First graph — two nodes in sequence:**

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    topic: str
    joke: str
    rating: str

def write_joke(state: State):
    joke = llm.invoke(f"Tell a clean one-line joke about {state['topic']}").content
    return {"joke": joke}                 # return ONLY the keys you change

def rate_joke(state: State):
    r = llm.invoke(f"Rate this joke 1-10, only number: {state['joke']}").content
    return {"rating": r}

builder = StateGraph(State)
builder.add_node("write_joke", write_joke)
builder.add_node("rate_joke", rate_joke)
builder.add_edge(START, "write_joke")
builder.add_edge("write_joke", "rate_joke")
builder.add_edge("rate_joke", END)

graph = builder.compile()
print(graph.invoke({"topic": "software engineers"}))
```

A compiled graph is also a Runnable, so `invoke`, `batch` and `stream` all work like in LangChain.

**See your graph:** `print(graph.get_graph().draw_mermaid())` gives Mermaid text; paste it into mermaid.live to see the picture.

**Practice:** Add a third node `improve_joke` between the two and check the final state.

## 2. State Management

The state schema decides what data the graph carries, and a **reducer** decides how a node's update is merged into the old value. Without a reducer the new value simply overwrites; with a reducer like `operator.add` it appends.

**State schema with reducers:**

```python
import operator
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    question: str                                          # overwrite (default)
    steps: Annotated[list[str], operator.add]              # append lists
    messages: Annotated[list[AnyMessage], add_messages]    # smart message merge
    attempts: int
```

**How updates work — remember these 3 rules:**

1. A node returns a **partial** dict; keys not returned stay unchanged.
2. For a key with no reducer, the returned value replaces the old one.
3. For a key with a reducer, LangGraph calls `reducer(old, new)`.

```python
def step_a(state: State):
    return {"steps": ["A done"], "attempts": state.get("attempts", 0) + 1}

def step_b(state: State):
    return {"steps": ["B done"]}   # steps becomes ['A done', 'B done']
```

**Why `add_messages` is special:** it appends new messages, but if a message with the same `id` comes again, it replaces it instead of duplicating. It also accepts plain tuples like `("user", "hi")`.

**Shortcut — MessagesState:** for chat-style graphs you don't need to write the schema yourself:

```python
from langgraph.graph import MessagesState

class AgentState(MessagesState):   # already has messages + add_messages
    user_name: str                  # add your own extra fields
```

**Custom reducer** — any function `(old, new) -> merged`:

```python
def keep_max(old: int, new: int) -> int:
    return max(old or 0, new)

class Score(TypedDict):
    best: Annotated[int, keep_max]
```

**Tips:** keep the state small and typed; store IDs or summaries, not full PDFs. Pydantic `BaseModel` can also be used as state if you want runtime validation.

**Practice:** Make a graph where three nodes each append to `steps`, and print the final list.

## 3. Conditional Routing

`add_conditional_edges()` lets a function look at the state and decide the next node at runtime — like a `switch` statement for your workflow. This is how you build classifiers, retries and agent loops.

**Example — support ticket router:**

```python
from typing import Literal, TypedDict
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    query: str
    category: str
    answer: str

class Category(BaseModel):
    category: Literal["billing", "technical", "general"]

classifier = llm.with_structured_output(Category)

def classify(state: State):
    return {"category": classifier.invoke(state["query"]).category}

def billing(state: State):   return {"answer": "Routing to billing team..."}
def technical(state: State): return {"answer": llm.invoke("Fix this: " + state["query"]).content}
def general(state: State):   return {"answer": llm.invoke(state["query"]).content}

# the router: reads state, returns the NAME of the next node
def route(state: State) -> Literal["billing", "technical", "general"]:
    return state["category"]

b = StateGraph(State)
b.add_node("classify", classify)
b.add_node("billing", billing)
b.add_node("technical", technical)
b.add_node("general", general)
b.add_edge(START, "classify")
b.add_conditional_edges("classify", route)     # dynamic path
for n in ["billing", "technical", "general"]:
    b.add_edge(n, END)

app = b.compile()
print(app.invoke({"query": "I was charged twice for my plan"})["answer"])
```

**Path map** — when the router returns labels instead of node names:

```python
b.add_conditional_edges("check", lambda s: "ok" if s["score"] > 7 else "retry",
                        {"ok": END, "retry": "write"})
```

**Loop with a safety limit** (very important — otherwise infinite loop and big bill):

```python
def should_retry(state):
    if state["score"] >= 7 or state["attempts"] >= 3:
        return END
    return "write"
```

LangGraph also has a global `recursion_limit` (default 25 steps): `app.invoke(inp, config={"recursion_limit": 10})`.

**Alternative — `Command`:** a node can update state and choose the next node in one return: `return Command(update={"x": 1}, goto="next_node")` (import from `langgraph.types`). Useful in multi-agent handoffs.

**Practice:** Build a "write → review" loop that rewrites a paragraph until the review score is 8 or above, max 3 attempts.

## 4. Agent Loops

An agent is simply a loop: the LLM thinks, asks for a tool, sees the tool result (observation), and thinks again — until it has enough information to give the final answer. This pattern is called **ReAct** (Reason + Act).

The cycle, step by step:

1. **LLM node** gets all messages and replies — either with `tool_calls` or with a final text answer.
2. **Router** checks the last message: tool calls present → go to tools; no tool calls → END.
3. **Tool node** runs each requested tool and adds `ToolMessage`s to the state.
4. Edge goes **back to the LLM node**, which now sees the observations. Repeat.

**Agent loop written by hand** (so you understand what happens inside):

```python
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END

@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@tool
def square(x: int) -> int:
    """Square an integer."""
    return x * x

tools = [add, square]
tools_by_name = {t.name: t for t in tools}
llm_tools = llm.bind_tools(tools)

def call_llm(state: MessagesState):
    return {"messages": [llm_tools.invoke(state["messages"])]}

def run_tools(state: MessagesState):
    results = []
    for call in state["messages"][-1].tool_calls:
        output = tools_by_name[call["name"]].invoke(call["args"])
        results.append(ToolMessage(content=str(output), tool_call_id=call["id"]))
    return {"messages": results}

def should_continue(state: MessagesState):
    return "tools" if state["messages"][-1].tool_calls else END

b = StateGraph(MessagesState)
b.add_node("llm", call_llm)
b.add_node("tools", run_tools)
b.add_edge(START, "llm")
b.add_conditional_edges("llm", should_continue, ["tools", END])
b.add_edge("tools", "llm")          # <-- this back-edge makes it a loop
agent = b.compile()

out = agent.invoke({"messages": [("user", "Add 3 and 4, then square the result")]})
for m in out["messages"]:
    m.pretty_print()
```

You will see: LLM asks `add(3,4)` → tool returns 7 → LLM asks `square(7)` → tool returns 49 → LLM answers "49". Two loops, decided by the model itself.

**Ready-made agent (one line):** once you understand the loop, you can use the prebuilt version, which builds exactly this graph:

```python
from langchain.agents import create_agent
agent = create_agent(llm, tools=tools, system_prompt="You are a math helper.")
```

(In older code you will see `langgraph.prebuilt.create_react_agent` — same idea.)

**Practice:** Add a `divide` tool and ask a question that needs three tool calls in order.

## 5. ToolNode & tools\_condition

`ToolNode` and `tools_condition` are prebuilt replacements for the `run_tools` and `should_continue` functions we wrote by hand in topic 4. Same loop, less code, plus parallel tool execution and error handling built in.

| Prebuilt | Replaces | What it does |
| --- | --- | --- |
| `ToolNode(tools)` | `run_tools` | Reads `tool_calls` of the last AIMessage, runs them (in parallel), returns `ToolMessage`s |
| `tools_condition` | `should_continue` | Returns `"tools"` if the last message has tool calls, else `END` |

**Same agent, short version:**

```python
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

def call_llm(state: MessagesState):
    return {"messages": [llm_tools.invoke(state["messages"])]}

b = StateGraph(MessagesState)
b.add_node("llm", call_llm)
b.add_node("tools", ToolNode(tools))       # node name MUST be "tools" for tools_condition
b.add_edge(START, "llm")
b.add_conditional_edges("llm", tools_condition)
b.add_edge("tools", "llm")
agent = b.compile()
```

**Tool errors:** by default `ToolNode` catches exceptions inside a tool and sends the error text back to the LLM as a `ToolMessage`, so the model can correct its arguments and try again instead of crashing your app. You can customise this:

```python
ToolNode(tools, handle_tool_errors="Tool failed. Check the arguments and try again.")
```

**System prompt for the agent** — add it inside the LLM node, not in the state, so it is not stored again and again:

```python
from langchain_core.messages import SystemMessage
SYS = SystemMessage("You are a helpful assistant. Use tools when needed. Be brief.")

def call_llm(state: MessagesState):
    return {"messages": [llm_tools.invoke([SYS] + state["messages"])]}
```

**Practice:** Make one tool deliberately raise `ValueError` for negative numbers and watch the LLM recover by itself.

## 6. Persistence & Checkpointing

A **checkpointer** saves the full state after every step, keyed by a `thread_id`. Same `thread_id` next time = the graph continues from where it stopped. This one feature gives you chat memory, crash recovery, human-in-the-loop and time-travel debugging.

**In-memory (for learning and tests):**

```python
from langgraph.checkpoint.memory import InMemorySaver   # older name: MemorySaver

memory = InMemorySaver()
app = b.compile(checkpointer=memory)

cfg = {"configurable": {"thread_id": "maneesha-1"}}
app.invoke({"messages": [("user", "Hi, I work on Spring Boot")]}, cfg)
out = app.invoke({"messages": [("user", "What framework do I use?")]}, cfg)
print(out["messages"][-1].content)   # remembers Spring Boot

# a new thread_id = fresh conversation
app.invoke({"messages": [("user", "What framework do I use?")]},
           {"configurable": {"thread_id": "other-user"}})
```

Notice: you only send the **new** message each time; the checkpointer loads the old ones automatically. Compare this with the manual work in LangChain topic 6.

**Database-backed (survives restarts):**

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
app = b.compile(checkpointer=SqliteSaver(conn))
```

For production use Postgres: `pip install langgraph-checkpoint-postgres` and `PostgresSaver.from_conn_string(DB_URI)` (call `.setup()` once to create tables).

**Inspect and time-travel:**

```python
snap = app.get_state(cfg)                 # latest state of this thread
print(snap.values["messages"][-1].content)
print(snap.next)                          # which node runs next (empty = finished)

for s in app.get_state_history(cfg):      # every saved checkpoint, newest first
    print(s.config["configurable"]["checkpoint_id"], len(s.values["messages"]))

app.update_state(cfg, {"messages": [("user", "note: be brief")]})   # edit state manually
```

**Checkpointer vs Store:** a checkpointer is memory for one thread (one conversation). For facts shared across all threads of a user (like "prefers Telugu"), LangGraph has a separate `Store` (`InMemoryStore`, Postgres store) — learn it after this.

**Practice:** Use `SqliteSaver`, chat a little, stop the script, start again with the same `thread_id`, and confirm it remembers.

## 7. Human-in-the-Loop

`interrupt()` pauses the graph in the middle of a node, saves the state through the checkpointer, and waits for a human. You resume later with `Command(resume=...)`, and that value becomes the return value of `interrupt()`. Use it before risky actions — sending emails, payments, DB writes, deployments.

**Rule:** interrupts need a checkpointer and a `thread_id`; without them there is nowhere to save the paused state.

**Example — approve an email before sending:**

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    request: str
    draft: str
    status: str

def write_draft(state: State):
    return {"draft": llm.invoke(f"Write a 3-line email: {state['request']}").content}

def human_review(state: State):
    decision = interrupt({"draft": state["draft"],
                          "question": "Approve, reject, or give edited text?"})
    if decision["action"] == "approve":
        return {"status": "approved"}
    if decision["action"] == "edit":
        return {"draft": decision["text"], "status": "approved"}
    return {"status": "rejected"}

def send_email(state: State):
    if state["status"] == "approved":
        print("SENDING:\n", state["draft"])   # call your mail API here
    return {}

b = StateGraph(State)
b.add_node("write_draft", write_draft)
b.add_node("human_review", human_review)
b.add_node("send_email", send_email)
b.add_edge(START, "write_draft")
b.add_edge("write_draft", "human_review")
b.add_edge("human_review", "send_email")
b.add_edge("send_email", END)
app = b.compile(checkpointer=InMemorySaver())

cfg = {"configurable": {"thread_id": "mail-1"}}
result = app.invoke({"request": "Ask manager for leave on Friday"}, cfg)
print(result["__interrupt__"][0].value)    # the draft shown to human

# ... later, maybe from a UI button click ...
app.invoke(Command(resume={"action": "approve"}), cfg)
```

**Important behaviour:** on resume, the interrupted node runs again **from its beginning**, and `interrupt()` now returns the resume value instead of pausing. So keep side effects (API calls, DB writes) *after* the `interrupt()` call or in the next node, never before it.

**Common patterns:** approve/reject a tool call, edit the state, give extra input when the agent is stuck, review output before final answer.

**Practice:** Put an approval `interrupt()` in front of a `delete_record` tool so nothing is deleted without a "yes".

## 8. Streaming

Agents take time, so users should see progress instead of a blank screen. LangGraph's `stream()` gives you different kinds of live output depending on `stream_mode`.

| stream\_mode | What you get | Use for |
| --- | --- | --- |
| `"values"` | Full state after every step | Debugging, showing the whole conversation |
| `"updates"` | Only what each node changed, with node name | Progress like "Searching...", "Calling tool..." |
| `"messages"` | LLM tokens one by one + metadata | ChatGPT-style typing effect |
| `"custom"` | Anything you emit from inside a node | Your own progress messages |
| `"debug"` | Very detailed internal events | Deep debugging only |

**Node-by-node updates:**

```python
inputs = {"messages": [("user", "Add 3 and 4, then square it")]}
for chunk in agent.stream(inputs, stream_mode="updates"):
    for node, update in chunk.items():
        print(f"--- {node} ---")
        update["messages"][-1].pretty_print()
```

**Token streaming (typing effect):**

```python
for msg_chunk, meta in agent.stream(inputs, stream_mode="messages"):
    if meta["langgraph_node"] == "llm" and msg_chunk.content:
        print(msg_chunk.content, end="", flush=True)
```

**Custom progress from inside a node:**

```python
from langgraph.config import get_stream_writer

def slow_node(state):
    writer = get_stream_writer()
    writer({"progress": "Reading 50 pages..."})
    return {}
```

**Multiple modes together:** `stream_mode=["updates", "messages"]` — then each chunk comes as a `(mode, data)` tuple.

Async apps (FastAPI + Server-Sent Events) use `async for chunk in agent.astream(...)`. For the most fine-grained events (every chain and tool start/end) there is also `astream_events(..., version="v2")`.

**Practice:** Stream your agent with `["updates", "messages"]` and print `[TOOL]` lines for tool nodes and live tokens for the LLM.

## 9. Subgraphs & Multi-Agent Systems

A compiled graph can be used as a node inside another graph — that is a **subgraph**. It lets you build reusable workflows (like a "research" module) and combine many specialist agents, each with its own prompt and tools, under one parent.

**Subgraph as a node** (works directly when parent and child share the same state keys, e.g. `messages`):

```python
# child graph built and compiled separately
research_graph = research_builder.compile()

parent = StateGraph(MessagesState)
parent.add_node("research", research_graph)   # compiled graph used as a node
parent.add_node("writer", writer_node)
parent.add_edge(START, "research")
parent.add_edge("research", "writer")
parent.add_edge("writer", END)
```

If the states are different, wrap the subgraph in a normal function that converts parent state → child input and child output → parent update.

**Common multi-agent patterns:**

| Pattern | How it works | Good for |
| --- | --- | --- |
| Supervisor | One manager LLM decides which worker agent runs next, then gets control back | Clear task delegation, easy to debug |
| Network / handoff | Agents pass control directly to each other using `Command(goto=...)` | Conversational flows (sales → support) |
| Hierarchical | Supervisors managing other supervisors (subgraphs) | Large systems with teams of agents |
| Agents as tools | A main agent calls other agents wrapped as `@tool` | Simplest way to start |

**Supervisor pattern (built from basics):**

```python
from typing import Literal
from pydantic import BaseModel
from langchain.agents import create_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command

math_agent = create_agent(llm, tools=[add, square], system_prompt="You do math only.")
writer_agent = create_agent(llm, tools=[], system_prompt="You write short friendly text.")

class Route(BaseModel):
    next: Literal["math", "writer", "FINISH"]

router = llm.with_structured_output(Route)

def supervisor(state: MessagesState) -> Command[Literal["math", "writer", "__end__"]]:
    decision = router.invoke(
        [("system", "Pick the next worker: math, writer, or FINISH if the user's request is fully answered.")]
        + state["messages"]
    )
    return Command(goto=END if decision.next == "FINISH" else decision.next)

def make_worker(agent, name):
    def node(state: MessagesState) -> Command[Literal["supervisor"]]:
        result = agent.invoke(state)
        last = result["messages"][-1]
        return Command(update={"messages": [("ai", f"[{name}] {last.content}")]},
                       goto="supervisor")
    return node

b = StateGraph(MessagesState)
b.add_node("supervisor", supervisor)
b.add_node("math", make_worker(math_agent, "math"))
b.add_node("writer", make_worker(writer_agent, "writer"))
b.add_edge(START, "supervisor")
team = b.compile()

team.invoke({"messages": [("user", "Square 12, then write a cheerful one-line message with the answer")]},
            {"recursion_limit": 15})
```

**Tips:** start with one agent and add more only when one prompt becomes too confused; give each agent a narrow job and few tools; always keep a `recursion_limit`. Ready-made helper libraries also exist (`langgraph-supervisor`, `langgraph-swarm`) once you understand the basics.

**Practice:** Add a third worker "researcher" with a dummy `search` tool and see the supervisor route to it.

## 10. Production & Evaluation

A demo agent and a production agent are very different. In production you need retries, limits, tests, tracing and a proper deployment — the same discipline you already follow for Spring Boot services with CI/CD.

**Retries and timeouts per node:**

```python
from langgraph.types import RetryPolicy

b.add_node("call_api", call_api,
           retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0,
                                    backoff_factor=2.0))
```

Also keep: `timeout`/`max_retries` on the model (LangChain topic 9), `recursion_limit` on every invoke, and `max_tokens` on answers.

**Testing — three levels:**

1. **Unit test nodes** as normal functions — nodes are just Python, so pytest them with a fake state.
2. **Test the graph with a fake LLM** so tests are fast, free and repeatable:

```python
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

def test_simple_reply():
    fake = GenericFakeChatModel(messages=iter([AIMessage("Hello!")]))
    graph = build_graph(llm=fake)          # make your builder accept the llm
    out = graph.invoke({"messages": [("user", "hi")]})
    assert out["messages"][-1].content == "Hello!"
```

3. **Evaluate quality with a dataset** — real questions + expected answers, scored automatically.

**LangSmith tracing and evaluation:** with `LANGSMITH_TRACING=true`, every graph run shows each node, tool call, token count and latency. Then create a dataset and run evaluations:

```python
from langsmith import Client
client = Client()
ds = client.create_dataset("faq-eval")
client.create_examples(dataset_id=ds.id,
    inputs=[{"question": "How many leaves per year?"}],
    outputs=[{"answer": "24"}])

def target(inputs):
    return {"answer": rag_chain.invoke(inputs["question"])}

def contains_answer(outputs, reference_outputs):
    return reference_outputs["answer"] in outputs["answer"]

client.evaluate(target, data="faq-eval", evaluators=[contains_answer])
```

For open-ended answers, use an "LLM-as-judge" evaluator that scores correctness or groundedness.

**Deployment options:**

| Option | When to choose |
| --- | --- |
| FastAPI + Docker (your own server) | Full control; fits existing Azure / Kubernetes setup and Azure DevOps pipelines |
| LangGraph Platform / LangSmith Deployment | Managed hosting with built-in persistence, streaming APIs and Studio UI |
| `langgraph dev` (local Studio) | Visual debugging on your laptop during development |

**Production checklist:**

- [ ] API keys from a secret store (Azure Key Vault, env vars), never in code
- [ ] Postgres checkpointer instead of InMemorySaver
- [ ] Model timeouts, retries, fallbacks, and recursion\_limit set
- [ ] Input validation and prompt-injection guard for tool-using agents
- [ ] Human approval for any write/delete/payment tool
- [ ] Tracing on; token usage and cost dashboards
- [ ] Eval dataset run in CI before every prompt or model change
- [ ] Dependencies scanned (Veracode SCA / pip-audit), versions pinned in `requirements.txt`

# Part 3 — Practical Projects

## Project 1 — Basic AI Chatbot

You will build a chatbot with a custom personality that remembers the conversation per user, streams its answers, and has a simple web UI. Topics used: Chat Models, Prompt Templates, LCEL, Conversation Memory, Streaming.

**Final folder structure:**

```text
project1-chatbot/
├── .env               # GROQ_API_KEY
├── config.py          # model setup
├── bot.py             # chain + memory
├── cli.py             # terminal chat
└── app.py             # Streamlit web UI
```

**Step 1 — Setup.** Create the folder, activate the venv from the setup section, and put your key in `.env`.

**Step 2 — Model config (`config.py`).** Keep model creation in one place:

```python
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(temperature: float = 0.6):
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=temperature,
                    max_tokens=800, timeout=30, max_retries=2)
```

**Step 3 — Prompt + chain + memory (`bot.py`).** System prompt gives the personality, `MessagesPlaceholder` holds the history, and SQLite keeps it after restart:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from config import get_llm

SYSTEM = ("You are 'Dost', a friendly tech mentor for Indian software engineers. "
          "Explain simply, use small examples, and keep answers under 150 words. "
          "If you don't know something, say so honestly.")

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

chain = prompt | get_llm() | StrOutputParser()

def get_history(session_id: str):
    return SQLChatMessageHistory(session_id=session_id,
                                 connection="sqlite:///chat.db")

chatbot = RunnableWithMessageHistory(
    chain, get_history,
    input_messages_key="input",
    history_messages_key="history",
)

def ask(session_id: str, text: str):
    """Yields the answer token by token."""
    cfg = {"configurable": {"session_id": session_id}}
    yield from chatbot.stream({"input": text}, config=cfg)
```

**Step 4 — Terminal version (`cli.py`).** Test the logic before building any UI:

```python
from bot import ask

session = input("Enter your user id: ").strip() or "guest"
print("Type 'exit' to quit.\n")
while True:
    q = input("You: ").strip()
    if q.lower() in {"exit", "quit"}:
        break
    print("Dost: ", end="")
    for token in ask(session, q):
        print(token, end="", flush=True)
    print("\n")
```

Run `python cli.py`. Tell it your name, ask something, then ask "what is my name?". Stop and run again with the same user id — it should still remember.

**Step 5 — Web UI (`app.py`).** Streamlit gives a chat screen in a few lines:

```python
import uuid
import streamlit as st
from bot import ask, get_history

st.title("Dost — your AI tech mentor")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# show previous messages from the DB
for m in get_history(st.session_state.session_id).messages:
    with st.chat_message("user" if m.type == "human" else "assistant"):
        st.markdown(m.content)

if q := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        st.write_stream(ask(st.session_state.session_id, q))
```

Run `streamlit run app.py` and open the browser link it prints.

**Step 6 — Test it properly:**

- [ ] Answers stream word by word
- [ ] Bot remembers facts within the session
- [ ] Two browser tabs (two sessions) do not mix memory
- [ ] Bot stays in its "Dost" personality and word limit

**Step 7 — Improve it (stretch goals):** add a sidebar to pick temperature, add a "Clear chat" button that calls `get_history(id).clear()`, trim long history with `trim_messages`, and rebuild the same bot with a LangGraph `MessagesState` + `InMemorySaver` to compare both styles.

## Project 2 — PDF Question-Answering Agent

You will build an agent that reads your PDFs, stores them in a vector database, and answers questions with page-number citations — searching the PDF only when the question needs it. Topics used: RAG, embeddings, vector DB, retrievers, tools, LangGraph agent loop, checkpointing.

**Final folder structure:**

```text
project2-pdf-qa/
├── .env
├── docs/              # put your PDFs here
├── chroma_db/         # created automatically
├── ingest.py          # PDF -> chunks -> embeddings -> Chroma
├── agent.py           # retriever tool + LangGraph agent
├── cli.py             # terminal Q&A
└── app.py             # Streamlit UI with upload
```

**Step 1 — Setup.** Same venv as before. Copy one or two PDFs (an employee handbook, a research paper, a Spring Boot guide) into `docs/`. The first run downloads the free embedding model (\~90 MB), so be patient.

**Step 2 — Ingestion (`ingest.py`).** Run this once, and again whenever PDFs change:

```python
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DB_DIR = "chroma_db"
emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def ingest(folder: str = "docs"):
    pages = []
    for pdf in Path(folder).glob("*.pdf"):
        pages += PyPDFLoader(str(pdf)).load()          # one Document per page
    print(f"Loaded {len(pages)} pages")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(pages)           # metadata (source, page) is kept
    print(f"Created {len(chunks)} chunks")

    Chroma.from_documents(chunks, emb, persist_directory=DB_DIR,
                          collection_name="pdfs")
    print("Saved to vector DB")

if __name__ == "__main__":
    ingest()
```

Run `python ingest.py`. You should see page and chunk counts.

**Step 3 — Retriever as a tool (`agent.py`, part 1).** Making retrieval a tool lets the agent decide when to search, search again with better words, or skip searching for small talk:

```python
from langchain_core.tools import tool
from langchain_chroma import Chroma
from ingest import emb, DB_DIR

vs = Chroma(persist_directory=DB_DIR, embedding_function=emb, collection_name="pdfs")
retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": 4})

@tool
def search_pdfs(query: str) -> str:
    """Search the uploaded PDF documents. Use this for any question about their content."""
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant content found."
    return "\n\n".join(
        f"[{Path(d.metadata['source']).name}, page {d.metadata.get('page', 0) + 1}]\n{d.page_content}"
        for d in docs
    )
```

(Add `from pathlib import Path` at the top.)

**Step 4 — The agent graph (`agent.py`, part 2):**

```python
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
tools = [search_pdfs]
llm_tools = llm.bind_tools(tools)

SYS = SystemMessage(
    "You answer questions about the user's PDF documents. "
    "Always call search_pdfs before answering a document question. "
    "Answer ONLY from the search results and cite like (file.pdf, page 3). "
    "If the answer is not in the results, say 'I could not find this in the documents.'"
)

def assistant(state: MessagesState):
    return {"messages": [llm_tools.invoke([SYS] + state["messages"])]}

b = StateGraph(MessagesState)
b.add_node("assistant", assistant)
b.add_node("tools", ToolNode(tools))
b.add_edge(START, "assistant")
b.add_conditional_edges("assistant", tools_condition)
b.add_edge("tools", "assistant")
pdf_agent = b.compile(checkpointer=InMemorySaver())

def ask(question: str, thread_id: str = "default") -> str:
    cfg = {"configurable": {"thread_id": thread_id}, "recursion_limit": 10}
    out = pdf_agent.invoke({"messages": [("user", question)]}, cfg)
    return out["messages"][-1].content
```

**Step 5 — Terminal test (`cli.py`):**

```python
from agent import ask
while (q := input("\nQuestion: ").strip()) not in {"", "exit"}:
    print("Answer:", ask(q, thread_id="cli"))
```

Try: a direct fact question, a follow-up like "explain that more simply" (memory), and a question not in the PDF (should say not found).

**Step 6 — Streamlit UI with upload (`app.py`):**

```python
import uuid, shutil
from pathlib import Path
import streamlit as st

st.title("Chat with your PDFs")
up = st.sidebar.file_uploader("Upload PDF", type="pdf", accept_multiple_files=True)
if up and st.sidebar.button("Index PDFs"):
    Path("docs").mkdir(exist_ok=True)
    for f in up:
        Path("docs", f.name).write_bytes(f.getvalue())
    shutil.rmtree("chroma_db", ignore_errors=True)   # rebuild cleanly
    from ingest import ingest
    ingest()
    st.sidebar.success("Indexed! Restart the app once to load the new index.")

from agent import ask
st.session_state.setdefault("tid", str(uuid.uuid4()))
st.session_state.setdefault("chat", [])
for role, text in st.session_state.chat:
    st.chat_message(role).markdown(text)
if q := st.chat_input("Ask about your PDFs"):
    st.chat_message("user").markdown(q)
    with st.spinner("Searching documents..."):
        a = ask(q, st.session_state.tid)
    st.chat_message("assistant").markdown(a)
    st.session_state.chat += [("user", q), ("assistant", a)]
```

**Step 7 — Test checklist:**

- [ ] Answers include file name and page number
- [ ] Out-of-document questions get "could not find", not a made-up answer
- [ ] Follow-up questions work (checkpointer memory)
- [ ] In `stream_mode="updates"` you can see the agent calling `search_pdfs`

**Step 8 — Improve it (stretch goals):** tune `chunk_size` and `k` and compare answers; add a grader node that checks if retrieved chunks are relevant and rewrites the query if not ("corrective RAG"); switch Chroma to PGVector; build a 10-question eval dataset in LangSmith and measure accuracy.

## Project 3 — Tool-Calling AI Agent

You will build an "Office Assistant" agent that calls a real weather API, answers questions by querying a SQLite company database, does calculations, and asks for human approval before writing anything to the database. Topics used: tools, bind\_tools, agent loop, ToolNode, checkpointing, human-in-the-loop, streaming, error handling.

**Final folder structure:**

```text
project3-tool-agent/
├── .env
├── seed_db.py         # creates company.db with sample data
├── tools.py           # weather, SQL, calculator, leave-request tools
├── agent.py           # LangGraph agent
└── cli.py             # streaming chat with approval prompts
```

**Step 1 — Setup.** Same venv, plus `pip install requests`. The weather API used here (Open-Meteo) is free and needs no key.

**Step 2 — Create the database (`seed_db.py`).** Run once with `python seed_db.py`:

```python
import sqlite3

con = sqlite3.connect("company.db")
con.executescript("""
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS leave_requests;
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT,
                        city TEXT, salary INTEGER, leaves_left INTEGER);
CREATE TABLE leave_requests (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        emp_id INTEGER, days INTEGER, reason TEXT);
INSERT INTO employees VALUES
 (1,'Ravi Kumar','Engineering','Hyderabad',1800000,12),
 (2,'Priya Sharma','Engineering','Bengaluru',2100000,8),
 (3,'Arjun Reddy','Sales','Chennai',1200000,15),
 (4,'Sneha Iyer','HR','Pune',1100000,10);
""")
con.commit(); con.close()
print("company.db ready")
```

**Step 3 — Write the tools (`tools.py`).** Each tool does one job, has a clear docstring, and is safe:

```python
import sqlite3, requests
from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def get_weather(city: str) -> str:
    """Get the current temperature and wind speed for a city."""
    geo = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                       params={"name": city, "count": 1}, timeout=10).json()
    if not geo.get("results"):
        return f"City '{city}' not found."
    loc = geo["results"][0]
    cur = requests.get("https://api.open-meteo.com/v1/forecast",
                       params={"latitude": loc["latitude"], "longitude": loc["longitude"],
                               "current": "temperature_2m,wind_speed_10m"},
                       timeout=10).json()["current"]
    return f"{loc['name']}: {cur['temperature_2m']}°C, wind {cur['wind_speed_10m']} km/h"

@tool
def get_db_schema() -> str:
    """Return table names and columns of the company database. Call this before writing SQL."""
    con = sqlite3.connect("company.db")
    rows = con.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
    con.close()
    return "\n".join(r[0] for r in rows)

@tool
def run_sql_query(query: str) -> str:
    """Run a READ-ONLY SQL SELECT query on the company database and return rows."""
    if not query.strip().lower().startswith("select"):
        return "Error: only SELECT queries are allowed."
    con = sqlite3.connect("file:company.db?mode=ro", uri=True)   # read-only connection
    try:
        cur = con.execute(query)
        cols = [c[0] for c in cur.description]
        rows = cur.fetchmany(50)
        return str([dict(zip(cols, r)) for r in rows]) or "No rows."
    finally:
        con.close()

@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression like '1800000 * 0.1 + 5000'."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Error: only numbers and + - * / ( ) are allowed."
    return str(eval(expression))   # safe because characters are restricted

@tool
def create_leave_request(emp_id: int, days: int, reason: str) -> str:
    """Create a leave request for an employee. Needs human approval."""
    answer = interrupt(f"Approve leave: employee {emp_id}, {days} days, reason '{reason}'? (yes/no)")
    if str(answer).lower() != "yes":
        return "Leave request was REJECTED by the human reviewer."
    con = sqlite3.connect("company.db")
    con.execute("INSERT INTO leave_requests(emp_id, days, reason) VALUES (?,?,?)",
                (emp_id, days, reason))
    con.execute("UPDATE employees SET leaves_left = leaves_left - ? WHERE id = ?", (days, emp_id))
    con.commit(); con.close()
    return f"Leave request created for employee {emp_id}."

ALL_TOOLS = [get_weather, get_db_schema, run_sql_query, calculator, create_leave_request]
```

Note the safety design: SQL tool is read-only at connection level, calculator restricts characters, and the only write tool is behind `interrupt()` — and the DB write happens *after* the interrupt, as LangGraph topic 7 taught.

**Step 4 — Build the agent (`agent.py`):**

```python
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from tools import ALL_TOOLS

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0,
               timeout=30, max_retries=2).bind_tools(ALL_TOOLS)

SYS = SystemMessage(
    "You are an Office Assistant. Use tools for facts; never guess numbers. "
    "For database questions, first call get_db_schema, then run_sql_query. "
    "Use calculator for any maths. Keep answers short and clear."
)

def assistant(state: MessagesState):
    return {"messages": [llm.invoke([SYS] + state["messages"])]}

b = StateGraph(MessagesState)
b.add_node("assistant", assistant)
b.add_node("tools", ToolNode(ALL_TOOLS))
b.add_edge(START, "assistant")
b.add_conditional_edges("assistant", tools_condition)
b.add_edge("tools", "assistant")
agent = b.compile(checkpointer=InMemorySaver())   # needed for interrupt()
```

**Step 5 — Streaming CLI with approval (`cli.py`):**

```python
from langgraph.types import Command
from agent import agent

cfg = {"configurable": {"thread_id": "office-1"}, "recursion_limit": 15}

def run(inp):
    for chunk in agent.stream(inp, cfg, stream_mode="updates"):
        for node, update in chunk.items():
            if node == "__interrupt__":
                continue
            last = update["messages"][-1]
            if node == "assistant" and last.tool_calls:
                for c in last.tool_calls:
                    print(f"  [calling {c['name']} {c['args']}]")
            elif node == "tools":
                print(f"  [result: {str(last.content)[:120]}]")
            else:
                print("Assistant:", last.content)

while (q := input("\nYou: ").strip()) not in {"", "exit"}:
    run({"messages": [("user", q)]})
    state = agent.get_state(cfg)
    while state.interrupts:                       # paused for approval
        ans = input(f"\n>>> {state.interrupts[0].value} ")
        run(Command(resume=ans))
        state = agent.get_state(cfg)
```

**Step 6 — Try these questions** and watch the tool calls print:

| Question | Tools you should see |
| --- | --- |
| What is the weather in Hyderabad right now? | `get_weather` |
| Who earns the highest salary in Engineering? | `get_db_schema` → `run_sql_query` |
| What is the average salary of Engineering, plus 10% hike? | `run_sql_query` → `calculator` |
| Weather in the city where Priya works? | `run_sql_query` → `get_weather` |
| Create 2 days leave for Ravi for a family function | `run_sql_query` → `create_leave_request` (asks you yes/no) |
| Delete all employees | No tool can do it; agent should refuse |

**Step 7 — Test checklist:**

- [ ] Multi-step questions chain tools correctly
- [ ] Saying "no" to approval leaves the DB unchanged
- [ ] A wrong SQL column causes an error message, and the agent retries with the schema
- [ ] Turning off the internet gives a polite weather error, not a crash

**Step 8 — Improve it (stretch goals):** wrap the agent in a FastAPI endpoint with SSE streaming; swap SQLite for your company's Postgres with a read-only DB user; switch `InMemorySaver` to `SqliteSaver`; add LangSmith tracing and an eval dataset of 15 questions; split into a supervisor with "HR agent" and "Weather agent" (LangGraph topic 9).

# Quick Revision Cheat Sheet

Keep this page open while coding — most day-to-day work needs only these imports.

| Need | Import / call |
| --- | --- |
| Groq model | `from langchain_groq import ChatGroq` |
| Messages | `from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage` |
| Prompts | `from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder` |
| Text output | `from langchain_core.output_parsers import StrOutputParser` |
| Structured output | `llm.with_structured_output(MyPydanticModel)` |
| LCEL helpers | `from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda` |
| Chat history | `from langchain_core.runnables.history import RunnableWithMessageHistory` |
| Tools | `from langchain_core.tools import tool` → `llm.bind_tools([...])` |
| PDF loader | `from langchain_community.document_loaders import PyPDFLoader` |
| Splitter | `from langchain_text_splitters import RecursiveCharacterTextSplitter` |
| Embeddings | `from langchain_huggingface import HuggingFaceEmbeddings` |
| Vector DB | `from langchain_chroma import Chroma` |
| Graph basics | `from langgraph.graph import StateGraph, MessagesState, START, END` |
| Message reducer | `from langgraph.graph.message import add_messages` |
| Prebuilt tools | `from langgraph.prebuilt import ToolNode, tools_condition` |
| Checkpointer | `from langgraph.checkpoint.memory import InMemorySaver` |
| HITL & routing | `from langgraph.types import interrupt, Command, RetryPolicy` |
| Ready agent | `from langchain.agents import create_agent` |

**Five golden rules:**

1. The LLM is stateless — memory is always something you send back to it.
2. The LLM never runs tools — your code (or `ToolNode`) does.
3. Nodes return only the keys they change; reducers decide how they merge.
4. Every loop needs an exit: a condition plus `recursion_limit`.
5. Anything that writes, deletes or pays goes behind `interrupt()`.

**Suggested study plan** (about 1–1.5 hours a day):

| Week | Learn | Build |
| --- | --- | --- |
| 1 | LangChain topics 1–6 | Project 1 (CLI, then Streamlit) |
| 2 | LangChain topics 7–9 | Project 2 with a simple RAG chain |
| 3 | LangGraph topics 1–6 | Convert Project 2 into the agent version |
| 4 | LangGraph topics 7–10 | Project 3, then add LangSmith evals |

**Progress tracker:**

- [ ] LangChain 1–3: fundamentals, chat models, prompts
- [ ] LangChain 4–6: structured output, LCEL, memory
- [ ] LangChain 7–9: tools, RAG, error handling
- [ ] LangGraph 1–3: graph basics, state, routing
- [ ] LangGraph 4–6: agent loops, ToolNode, checkpointing
- [ ] LangGraph 7–10: HITL, streaming, multi-agent, production
- [ ] Project 1 — Basic AI chatbot
- [ ] Project 2 — PDF question-answering agent
- [ ] Project 3 — Tool-calling AI agent

Once all three projects are on GitHub with a clear README, a short demo GIF and a LangSmith eval screenshot, you have a solid AI-engineering portfolio — and your Java + CI/CD + security background makes it stand out further. All the best!
