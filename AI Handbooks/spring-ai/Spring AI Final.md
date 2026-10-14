
<img width="1400" height="846" alt="untitled (5)" src="https://github.com/user-attachments/assets/3caabdda-5a01-4c44-bb2a-a75be7a68013" />




# Part 1: Spring AI Foundations & Core Components

## What is Spring AI

Spring AI is an application framework that simplifies the integration of AI capabilities into Java applications. Its core goal is to "streamline AI feature development without introducing unnecessary complexity."

The fundamental problem Spring AI solves is: **connecting enterprise data and APIs with AI models**. For teams that already run Spring Boot business systems, Spring AI offers a natural path to add AI capabilities into existing architecture—rather than forcing developers to learn an entirely new Python toolchain.

In terms of positioning, Spring AI is not a "black-box agent framework" that hides all the details. It organizes model calls, Tool Calling, RAG, Structured Output, and Vector Stores in a **Spring-native way**—through Starters, auto-configuration, Properties, and a Fluent API, letting Java developers build AI applications using patterns they already know.

Spring AI has reached its official release, supports Java 21 and virtual threads, and offers GraalVM native image support with significantly faster startup than traditional JVM mode.


## Architecture & High-Level Overview of Components

Spring AI's architecture can be understood as **layered abstractions**: replaceable model interfaces at the bottom, high-level APIs for Spring applications at the top.

### Core Layers

**Model Abstraction Layer**: Defines interfaces like `ChatModel`, `EmbeddingModel`, and `ImageModel`. Each AI provider (OpenAI, Anthropic, Ollama, etc.) supplies its own implementation, so switching models only requires changing dependencies and configuration—not code.

**Client Layer**: `ChatClient` is the API developers interact with most. It offers a Fluent-style call, similar to `WebClient` and `RestClient`, with support for synchronous and streaming responses.

**Advisor Layer**: Encapsulates reusable generative AI patterns. The RAG Advisor automatically injects retrieved context into the prompt, and the Chat Memory Advisor manages conversation history. This layer is Spring AI's primary mechanism for handling "cross-cutting concerns."

**Vector Store Layer**: A unified `VectorStore` interface supporting PostgreSQL/PGVector, Chroma, Pinecone, Milvus, Neo4j, Redis, and other mainstream vector databases.

### Key Module Structure (as of April 2025)

Spring AI has split its core into finer-grained domain modules:

- `spring-ai-commons`: Base domain models (Document, TextSplitter)
- `spring-ai-model`: AI capability abstractions (ChatModel, EmbeddingModel, Tool Calling)
- `spring-ai-vector-store`: Unified vector database abstraction
- `spring-ai-client-chat`: ChatClient, ChatMemory, OutputConverter
- `spring-ai-rag`: Complete RAG framework, including `RetrievalAugmentationAdvisor`

This modular design lets applications pull in only what they need, reducing unnecessary dependencies.


## Comparison with LangChain

This is a common point of confusion. The two frameworks **overlap in problem domain, but differ in design philosophy and ideal use case**.

### Core Positioning Differences

**Spring AI** positions itself as "**AI infrastructure inside Spring applications**." Its strength is not the most complex agent orchestration, but letting AI capabilities **enter existing Spring Boot applications naturally**.

**LangChain (Python)** positions itself as "**the de facto toolkit for AI development**." It has the largest ecosystem—100+ LLM integrations, 50+ vector stores, 100+ tools—and the biggest community.

### Key Differences

| Dimension | Spring AI | LangChain (Python) |
|---|---|---|
| **Language & Ecosystem** | Deeply tied to Java / Spring Boot | Python / TypeScript |
| **Integration Style** | Auto-config, Starters, Properties | Explicit Chain/Agent assembly |
| **Enterprise Features** | Native support for security, monitoring, health checks | Requires additional integration |
| **Ecosystem Breadth** | Leaner, focused on mainstream providers | Extremely broad, covers almost everything |
| **Learning Curve** | Nearly zero for Spring developers | Fast for Python devs, but many concepts |

### One-Line Recommendation

If you're already building enterprise apps with **Spring Boot** and want to add AI with minimal architectural change, Spring AI is the natural choice. If you need **fast prototyping, a huge set of non-mainstream integrations, or your team is Python-first**, LangChain's ecosystem advantage is more obvious.

It's worth noting that Spring AI and LangChain are **not mutually exclusive**. A common hybrid architecture: the Java layer uses Spring AI for business integration and API exposure, while the Python layer uses LangChain for complex AI orchestration, communicating via REST or gRPC.


## Model Providers

One of Spring AI's core design goals is **portability**: call different model providers through the same API. This is achieved through multiple implementations of `ChatModel`, `EmbeddingModel`, and similar interfaces.

### Supported Providers (Partial)

According to the official `AiProvider` enum and documentation, supported providers include:

- **Anthropic** (Claude series)
- **OpenAI** (GPT series)
- **Microsoft / Azure OpenAI**
- **Amazon Bedrock**
- **Google Vertex AI / Google GenAI** (Gemini series)
- **Ollama** (local model runtime)
- **Mistral AI**
- **DeepSeek**
- **ONNX**

Additionally, Spring AI supports OpenAI-compatible APIs, allowing integration with providers like Groq, Perplexity, and NVIDIA.

### Multimodal & Feature Comparison (Partial)

Providers differ in capabilities. Here's a key comparison:

| Provider | Multimodal Support | Tool Calling | Streaming | Built-in JSON Mode |
|---|---|---|---|---|
| OpenAI | text, image, audio | ✓ | ✓ | ✓ |
| Anthropic Claude | text, pdf, image | ✓ | ✓ | ✗ |
| Azure OpenAI | text, image | ✓ | ✓ | ✓ |
| Google GenAI | text, pdf, image, audio, video | ✓ | ✓ | ✓ |
| Ollama | text, image | ✓ | ✓ | ✓ |
| DeepSeek | text | ✓ | ✓ | ✓ |

This table helps you pick the right provider for your project. For example, if you need video understanding, Google GenAI and Vertex AI Gemini currently offer the most complete support; if you need local execution with privacy in mind, Ollama is the top choice.


## Key Abstractions

Spring AI provides a set of core interfaces and classes that let Java developers interact with AI models in a consistent way. Below are the abstractions developers encounter most.

### ChatClient

`ChatClient` is the **entry-point API** for interacting with chat models. It offers Fluent-style calls:

```java
String response = chatClient.prompt()
    .user("Explain Spring AI in one sentence")
    .call()
    .content();
```

`ChatClient` supports `.system()` for system prompts, `.user()` for user messages, `.call()` for synchronous calls, and `.stream()` for streaming. Its design goal is to make AI calls feel like ordinary Spring service calls.

### ChatModel

`ChatModel` is the lower-level interface, offering finer control. Use it when you need to work directly with `Prompt` and `ChatResponse` objects, or when you need access to provider-specific features.

The relationship is similar to `RestClient` versus `RestTemplate`: `ChatClient` is the high-level wrapper, `ChatModel` is the underlying capability.

### EmbeddingModel

`EmbeddingModel` converts text into vector embeddings. This is the foundation of semantic search and RAG. Each provider has its own implementation, so switching is just a dependency change.

### VectorStore

`VectorStore` is the unified abstraction for vector databases. Core methods include:

- `add(List<Document>)`: add documents and their embeddings
- `similaritySearch(SearchRequest)`: similarity search
- `delete(...)`: delete documents

When adding documents, `VectorStore` typically uses the configured `EmbeddingModel` to generate vectors automatically, then stores them in the underlying database.

### PromptTemplate

`PromptTemplate` builds reusable prompt templates with placeholder substitution. This is Prompt Engineering made engineer-friendly in Spring AI.

### Document and the ETL Framework

The `Document` class represents a unit of data in the ETL (Extract-Transform-Load) pipeline, containing content, metadata, and embeddings. Spring AI provides a complete ETL toolkit:

- **DocumentReader**: reads documents from JSON, text, PDF, and other sources
- **DocumentTransformer**: e.g., `TokenTextSplitter` for chunking, `KeywordMetadataEnricher` for keyword extraction
- **DocumentWriter**: writes to `VectorStore` or files

### Tool Calling / Function Calling

Tool Calling lets the LLM proactively request execution of Java methods. Developers just add the `@Tool` annotation:

```java
@Tool
public Weather getWeather(String city) {
    return weatherService.query(city);
}
```

Spring AI automatically generates the Tool Schema, matches the model's Tool Call request, executes the method, and feeds the result back to the model. The full agent loop (call model → detect Tool Call → execute Tool → return result → call model again) is managed by the framework.

### Advisors API

Advisors are Spring AI's **interceptor mechanism** for cross-cutting concerns. For example:

- **QuestionAnswerAdvisor**: automatically performs RAG retrieval and injects context into the prompt
- **VectorStoreChatMemoryAdvisor**: automatically manages conversation history

### Structured Output

`OutputConverter` maps the LLM's text response into a Java POJO automatically. Spring AI supports JSON Schema-driven structured output, provided the model supports JSON mode.


That's an overview of Spring AI foundations and core components. Once you understand these abstractions and how they relate, you have the knowledge base to systematically integrate AI into Spring Boot applications. Later chapters dive deeper into RAG, AI application patterns, and production deployment.
