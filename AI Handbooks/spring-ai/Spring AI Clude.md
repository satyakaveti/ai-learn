# Spring AI Handbook V2

### AI for Backend Developers, Part 7: building AI applications in Java with Spring AI

You already know what LLMs, prompts, RAG, agents and MCP are. This handbook shows how to **build** each of them in a Spring Boot application, using Spring AI.

**Builds on the earlier parts of the series**

| Series part | Concept | Where it is implemented here |
| --- | --- | --- |
| [Part 1: AI Fundamentals](https://medium.com/@satyacodes/ai-for-backend-developers-part-2-ai-fundamentals-910e8cd2e3d2) | AI, ML, DL, LLMs | Chapters 1 to 3 |
| [Part 2: Generative AI](https://medium.com/@satyacodes/ai-for-backend-developers-part-3-generative-ai-fundamentals-c4b896127d1c) | Tokens, temperature, generation | Chapters 3, 5, 12 |
| [Part 3: Prompt Engineering](https://medium.com/@satyacodes/ai-for-backend-developers-part-4-prompt-engineering-8e0687959a8e) | Prompts as clear tickets | Chapters 4, 5 |
| [Part 4: RAG + Vector Databases](https://medium.com/@satyacodes/ai-for-backend-developers-part-5-rag-vector-databases-1203c6f7a22e) | Chat with your documents | Chapters 8, 9 |
| [Part 5: Agentic AI](https://medium.com/@satyacodes/ai-for-backend-developers-part-6-agentic-ai-cca78c569dc7) | Agents vs chatbots | Chapters 7, 10 |
| [Part 6: MCP](https://satyacodes.medium.com/ai-for-backend-developers-part-7-mcp-model-context-protocol-b452c6a3a4ee?sharedUserId=satyacodes) | Connecting models to tools | Chapter 11 |

**Version baseline used in this handbook:** Spring AI **2.0.x** (2.0.1 is the latest stable at the time of writing), Spring Boot **4.x**, Java **17 or newer** (examples use Java 21). If you are on Spring Boot 3.5, use Spring AI **1.1.x**; the differences are called out in the **Version note** boxes.

**Two running examples** carry through the chapters:

- **Refund Policy assistant:** a RAG app over the Amazon refund policy PDF (chapters 8 and 9, Project 2).
- **Goa trip agent:** an agent that plans a trip within a budget using flight and hotel tools (chapters 7 and 10, Project 3).

---

## Table of Contents

**Part 1: Spring AI Fundamentals**
1. Introduction to Spring AI
2. Spring AI Setup
3. Spring AI Core Components

**Part 2: Building AI Applications**
4. ChatClient and Prompt Engineering
5. Structured Output and Streaming
6. Chat Memory
7. Tool Calling

**Part 3: RAG and Vector Databases**
8. Embeddings and Vector Stores
9. Document Ingestion and RAG

**Part 4: Agents and MCP**
10. Building AI Agents
11. Spring AI and MCP

**Part 5: Production-Ready Spring AI**
12. Advisors and Advanced Capabilities
13. Testing, Observability and Security
14. Deployment and Best Practices

**Hands-On Projects**
- Project 1: AI Chat REST API
- Project 2: Chat with PDF Documents (Spring AI and PGvector)
- Project 3: AI Agent with Java Tools and MCP

**Appendix:** Cheat sheet

---

# Part 1: Spring AI Fundamentals

## 1. Introduction to Spring AI

### 1.1 What it is

Spring AI is a Spring project that gives Java developers a **portable, Spring-style API** for talking to AI models and for building the pieces around them: prompts, memory, tools, RAG and MCP. Its goal is to connect your enterprise data and APIs with AI models.

### 1.2 Why it is needed

Without a framework you write the same plumbing for every model: an HTTP client, request and response JSON, retries, streaming, and tool-call loops. That is exactly what the Python scripts in the earlier labs did by hand (`requests.post(...)`, a regex `parse()`, a `while` loop). Spring AI replaces that plumbing with familiar Spring building blocks.

| Plumbing you would write yourself | What Spring AI gives you |
| --- | --- |
| HTTP client per provider | One `ChatModel` API; swap OpenAI for Ollama by changing a dependency and a property |
| JSON parsing of replies | `.entity(MyRecord.class)` maps the reply to a Java type |
| Conversation history list | `ChatMemory` and a memory advisor |
| Tool-call loop | `@Tool` methods and a built-in tool-calling loop |
| Embedding, similarity search | `EmbeddingModel` and `VectorStore` over many databases |
| Custom logging and tracing | Micrometer observability built in |
| Wiring and config | Spring Boot auto-configuration and starters |

### 1.3 Architecture

```
Your Spring Boot application
 |
 |-- ChatClient  (fluent API: prompt, call, stream, entity)
 |      |-- Advisors  (memory, RAG, tool calling, logging, your own)
 |      |-- Tools     (@Tool methods, MCP tools)
 |
 |-- Model API  (ChatModel, EmbeddingModel, image, audio)  --->  OpenAI, Ollama, Anthropic, Google, Bedrock, ...
 |
 |-- VectorStore (PGvector, Chroma, Redis, ...)  <---  ETL: DocumentReader -> TextSplitter -> embed -> store
 |
 |-- Observability (Micrometer metrics and traces)
```

### 1.4 Spring AI vs LangChain

| | Spring AI (Java) | LangChain and LangGraph (Python) |
| --- | --- | --- |
| Language and fit | Java and Spring Boot teams; fits existing services | Python teams and notebooks |
| Wiring | Auto-configuration, dependency injection, `application.yml` | Explicit Python objects |
| Building blocks | `ChatClient`, advisors, `VectorStore`, `@Tool` | Chat models, prompts, LCEL chains, retrievers, `@tool` |
| Cross-cutting behaviour | Advisors chain (like servlet filters) | Callbacks and runnables |
| Agents | Tool-calling loop in the advisor chain; you write the control flow in Java | LangGraph: explicit stateful graph with checkpoints and human-in-the-loop |
| Observability | Micrometer, Spring Boot Actuator | LangSmith |
| Enterprise features | Security, data access, transactions, Actuator come from the Spring ecosystem | You assemble them yourself |
| Ecosystem pace | Smaller, steadier | Larger, moves very fast |

Pick Spring AI when the AI feature lives inside a Java service you already run. Pick LangChain and LangGraph when you need their larger ecosystem or complex checkpointed graphs. Many teams do both: Java services with Spring AI, and Python for experiments.

### 1.5 Versions at a glance

| Spring AI | Spring Boot | Notes |
| --- | --- | --- |
| 2.0.x (stable) | 4.x | Tool calling rebuilt around `ToolCallingAdvisor`; Java 17 minimum |
| 1.1.x | 3.5.x | Older line; tool loop lived inside each chat model |
| 2.1 (in development) | 4.x | Some property names are being flattened; check release notes |

> **Version note:** this handbook targets 2.0.x. Starter artifact names follow the pattern `spring-ai-starter-model-<provider>`. Old names such as `spring-ai-openai-spring-boot-starter` stopped at 1.0.0-M6, so tutorials using them are out of date.

---

## 2. Spring AI Setup

### 2.1 Create the project

Generate a project at [start.spring.io](https://start.spring.io) with **Spring Web**, plus **Ollama** (local and free) or **OpenAI**. Generating it there guarantees the starter names match your Boot version.

`pom.xml` essentials:

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.0.2</version> <!-- any current 4.x -->
</parent>

<properties>
    <java.version>21</java.version>
    <spring-ai.version>2.0.1</spring-ai.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>${spring-ai.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-webmvc</artifactId> <!-- spring-boot-starter-web on Boot 3.x -->
    </dependency>
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-starter-model-ollama</artifactId>
    </dependency>
    <!-- or: spring-ai-starter-model-openai -->
</dependencies>
```

Gradle equivalent: `implementation platform("org.springframework.ai:spring-ai-bom:2.0.1")` plus `implementation "org.springframework.ai:spring-ai-starter-model-ollama"`.

The BOM manages every Spring AI version, so individual starters carry no version number.

### 2.2 Configuration

`src/main/resources/application.yml` for local Ollama:

```yaml
spring:
  ai:
    ollama:
      base-url: http://localhost:11434
      chat:
        options:
          model: llama3.1
          temperature: 0.2
```

For OpenAI instead:

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: <a current model name from your OpenAI account>
          temperature: 0.2
```

If **both** starters are on the classpath, choose one explicitly: `spring.ai.model.chat=ollama` (or `openai`). A common setup is Ollama for development and OpenAI in production, switched by Spring profile.

### 2.3 API keys

- Keep keys in **environment variables** (`OPENAI_API_KEY`) and reference them as `${OPENAI_API_KEY}`. Never commit a key.
- In IntelliJ or PyCharm, set them in the run configuration. In Kubernetes, use a Secret (chapter 14).
- If a key is ever pasted into a chat, a ticket or a repo, rotate it.

### 2.4 Hello world

```java
@RestController
class HelloController {

    private final ChatClient chatClient;

    HelloController(ChatClient.Builder builder) {   // auto-configured by the starter
        this.chatClient = builder.build();
    }

    @GetMapping("/hello")
    String hello(@RequestParam(defaultValue = "Say hello to a Java developer in one line.") String q) {
        return chatClient.prompt().user(q).call().content();
    }
}
```

```bash
ollama pull llama3.1
./mvnw spring-boot:run
curl "http://localhost:8080/hello?q=What%20is%20Spring%20AI%3F"
```

### 2.5 Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Connection refused` on port 11434 | Ollama server is not running | Start the Ollama app or run `ollama serve` |
| `404` or "model not found" | Model never pulled | `ollama pull <model>`; confirm with `ollama list` |
| `401 Unauthorized` | Missing or wrong API key | Check the environment variable is visible to the app |
| No bean of type `ChatClient.Builder` | No model starter on the classpath | Add a `spring-ai-starter-model-*` dependency |
| Two `ChatModel` beans, startup error | Both starters present | Set `spring.ai.model.chat=ollama` or `openai` |

---

## 3. Spring AI Core Components

### 3.1 The pieces

| Component | What it is | Analogy |
| --- | --- | --- |
| `ChatModel` | Low-level interface: takes a `Prompt`, returns a `ChatResponse` | JDBC `Connection` |
| `ChatClient` | Fluent high-level API built on a `ChatModel` | `RestClient` or `JdbcClient` |
| `Prompt` | The full request: a list of messages plus options | Request object |
| `Message` | One turn with a role: `SystemMessage`, `UserMessage`, `AssistantMessage`, `ToolResponseMessage` | A chat bubble |
| `ChatOptions` | Model, temperature, max tokens, per call or default | Request parameters |
| `ChatResponse` | The result: one or more generations plus metadata (token usage, finish reason) | Response object |
| Model provider | The service behind `ChatModel`: OpenAI, Ollama, Anthropic, Google, Azure OpenAI, Bedrock, and more | Database driver |

### 3.2 Using `ChatModel` and `Prompt` directly

```java
@Service
class CoreDemo {

    private final ChatModel chatModel;

    CoreDemo(ChatModel chatModel) { this.chatModel = chatModel; }

    String plan() {
        Prompt prompt = new Prompt(List.of(
                new SystemMessage("You are a travel planner. Be concise."),
                new UserMessage("Plan 3 nights in Goa.")));

        ChatResponse response = chatModel.call(prompt);

        String text = response.getResult().getOutput().getText();
        Integer tokens = response.getMetadata().getUsage().getTotalTokens();
        return text + " (" + tokens + " tokens)";
    }
}
```

Reading the response: `getResult()` is the first `Generation`; `getOutput()` is its `AssistantMessage`; `getText()` is the reply text. `getMetadata().getUsage()` carries token counts, which you will use for cost tracking (chapter 13).

### 3.3 The same call with `ChatClient`

```java
String text = chatClient.prompt()
        .system("You are a travel planner. Be concise.")
        .user("Plan 3 nights in Goa.")
        .call()
        .content();                      // just the text

ChatResponse full = chatClient.prompt()
        .user("Plan 3 nights in Goa.")
        .call()
        .chatResponse();                 // text plus metadata
```

### 3.4 Which one to use

| Use | When |
| --- | --- |
| `ChatClient` | Almost always. It adds templates, advisors (memory, RAG), tools and structured output |
| `ChatModel` | You need exact control of the `Prompt` or are writing framework-level code |

### 3.5 Model providers

All providers follow the same pattern: add `spring-ai-starter-model-<provider>`, set `spring.ai.<provider>.*` properties, and your `ChatClient` code does not change.

| Provider | Starter suffix | Typical use |
| --- | --- | --- |
| Ollama | `ollama` | Local development, offline, free |
| OpenAI | `openai` | Hosted, strong general models |
| Anthropic | `anthropic` | Hosted Claude models |
| Google, Azure OpenAI, Amazon Bedrock, Mistral, and others | see the reference docs | Cloud and enterprise setups |

> **Tool calling needs a capable model.** Small local models may not support tools. With Ollama use a tool-capable model such as `llama3.1`; `gemma2:2b` does not support tool calling in Ollama.


---

# Part 2: Building AI Applications

## 4. ChatClient and Prompt Engineering

Part 3 of the series framed a prompt as "a clear Jira ticket for an AI". In Spring AI that ticket has parts: a **system prompt** (role and rules), **user messages** (the task), and **parameters** (the dynamic data).

### 4.1 System prompts and user messages

```java
String answer = chatClient.prompt()
        .system("You are a travel planner. Answer in at most three sentences.")
        .user("Is November a good month to visit Goa?")
        .call()
        .content();
```

Set a default system prompt once when you build the client, so every call inherits it:

```java
@Configuration
class AiConfig {

    @Bean
    ChatClient chatClient(ChatClient.Builder builder) {
        return builder
                .defaultSystem("You are a travel planner for Indian cities. Amounts are in rupees.")
                .build();
    }
}
```

A per-call `.system(...)` overrides the default for that call.

### 4.2 Prompt templates

Placeholders use `{name}` and are filled with `.param(...)`:

```java
String plan = chatClient.prompt()
        .user(u -> u.text("Plan {nights} nights in {city} within Rs {budget}.")
                .param("nights", 3)
                .param("city", "Goa")
                .param("budget", 13000))
        .call()
        .content();
```

The same works for the system prompt: `.system(s -> s.text("...{persona}...").param("persona", "budget traveller"))`.

### 4.3 Templates in files

Long prompts belong in `src/main/resources/prompts/`, not in Java strings.

`prompts/trip-planner.st`:

```
Plan {nights} nights in {city} within Rs {budget}.
List the flight, the hotel and the total cost.
```

```java
@Value("classpath:/prompts/trip-planner.st")
private Resource tripPrompt;

String plan = chatClient.prompt()
        .user(u -> u.text(tripPrompt)
                .param("nights", 3).param("city", "Goa").param("budget", 13000))
        .call()
        .content();
```

`PromptTemplate` is the standalone version when you need to build a `Prompt` yourself:

```java
Prompt prompt = new PromptTemplate("Tell me about {topic}").create(Map.of("topic", "Goa"));
```

> **Curly braces:** `{` and `}` mark placeholders. If your prompt needs literal JSON, pass it in as a parameter (`{example}`) instead of typing braces in the template.

### 4.4 Dynamic prompts

A prompt is just data, so build it from runtime state:

```java
String persona = user.isPremium() ? "a luxury travel concierge" : "a budget travel guide";

String reply = chatClient.prompt()
        .system(s -> s.text("You are {persona}. Respond in {language}.")
                .param("persona", persona)
                .param("language", user.language()))
        .user(question)
        .call()
        .content();
```

### 4.5 Prompt engineering checklist for Java code

| Technique (from Part 3) | In Spring AI |
| --- | --- |
| Give a role | `.system(...)` or `defaultSystem(...)` |
| Be specific about format | State the format in the prompt, or use `.entity(...)` (chapter 5) |
| Provide examples (few-shot) | Put examples in the system prompt as a parameter, or send them as earlier user and assistant messages |
| Constrain the answer | "Answer only from the context. If unknown, say you do not know." (used in RAG) |
| Lower randomness for factual tasks | `temperature` in `application.yml` or per call (chapter 12) |
| Keep prompts versioned | Prompt files in `resources/prompts/`, reviewed like code |

---

## 5. Structured Output and Streaming

### 5.1 Mapping responses to Java types

Ask for a Java type and Spring AI adds format instructions to the prompt and converts the reply:

```java
record TripPlan(String flight, String hotel, int totalRs, boolean withinBudget) {}

TripPlan plan = chatClient.prompt()
        .user("Flight Rs 8633, hotel Rs 2100, budget Rs 13000. Summarise as a trip plan.")
        .call()
        .entity(TripPlan.class);

System.out.println(plan.totalRs() + " " + plan.withinBudget());   // a real int and boolean
```

Lists and generics use `ParameterizedTypeReference`:

```java
List<String> cities = chatClient.prompt()
        .user("List three beach cities in India.")
        .call()
        .entity(new ParameterizedTypeReference<List<String>>() {});
```

Under the hood, `.entity(...)` derives a JSON schema from your type, adds it to the prompt, and parses the reply with a `BeanOutputConverter`. This replaces the regex `parse()` from the Python lab.

### 5.2 When the model returns bad JSON

The default `.entity(...)` call asks for matching JSON but cannot force it. Spring AI 2.x adds a self-correcting retry:

```java
TripPlan plan = chatClient.prompt()
        .user("...")
        .call()
        .entity(TripPlan.class, spec -> spec.validateSchema());   // method name per the current 2.x docs
```

It validates the reply against the schema and retries (3 attempts by default), sending the validation error back to the model. Small local models benefit most. Some providers also offer **native structured output**, which Spring AI can use when the model supports it; see the structured output reference.

| Option | Use when |
| --- | --- |
| `.entity(Type.class)` | Capable models, simple types |
| `.entity(Type.class, spec -> spec.validateSchema())` | Small models or strict downstream code |
| Native structured output | Provider supports it and you need guarantees |

### 5.3 Streaming

For chat UIs, stream tokens as they arrive instead of waiting for the full reply:

```java
@GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
Flux<String> stream(@RequestParam String q) {
    return chatClient.prompt().user(q).stream().content();
}
```

`.stream().content()` returns a reactor `Flux<String>`; each element is a chunk of text. Spring MVC can return a `Flux` as server-sent events. For the full response object use `.stream().chatResponse()`.

Notes:

- `.entity(...)` works with `.call()`, not with `.stream()`. To get a typed object, collect the stream first and convert, or use `.call()`.
- Streaming reduces **perceived** latency; it does not reduce token cost.
- Clients must handle `text/event-stream`. In a browser use `EventSource` or `fetch` with a stream reader.

---

## 6. Chat Memory

### 6.1 The problem

An LLM is stateless. "Make it 4 nights" only works if you resend the earlier turns. Spring AI's `ChatMemory` stores those turns per conversation and a memory advisor adds them to each request automatically.

### 6.2 The pieces

| Piece | Role |
| --- | --- |
| `ChatMemory` | Decides which past messages are sent to the model |
| `MessageWindowChatMemory` | The default: keeps the last N messages |
| `ChatMemoryRepository` | Where messages are stored (in memory, JDBC, Redis, Neo4j, and others) |
| `MessageChatMemoryAdvisor` | The advisor that loads and saves messages around each call |
| `ChatMemory.CONVERSATION_ID` | The key that separates one conversation from another |

Spring AI auto-configures a `ChatMemory` bean, backed by an in-memory repository unless you add another.

### 6.3 Multi-turn conversations

```java
@Configuration
class AiConfig {

    @Bean
    ChatClient chatClient(ChatClient.Builder builder, ChatMemory chatMemory) {
        return builder
                .defaultSystem("You are a travel planner.")
                .defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
                .build();
    }
}
```

```java
String reply(String conversationId, String message) {
    return chatClient.prompt()
            .user(message)
            .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, conversationId))
            .call()
            .content();
}
```

```
reply("trip-1", "Plan Goa within Rs 13000")   -> a plan
reply("trip-1", "Make it 4 nights")           -> the model remembers Goa and the budget
reply("trip-2", "What was my budget?")        -> it does not know: a different conversation
```

Set the window size with your own bean:

```java
@Bean
ChatMemory chatMemory() {
    return MessageWindowChatMemory.builder().maxMessages(20).build();
}
```

### 6.4 Persisting memory in a database

In-memory history disappears on restart. Add the JDBC repository:

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-chat-memory-repository-jdbc</artifactId>
</dependency>
```

```yaml
spring:
  ai:
    chat:
      memory:
        repository:
          jdbc:
            initialize-schema: always   # or embedded / never; create the table yourself in production
```

The default `ChatMemory` bean then uses your database. Check the chat memory reference for the exact starter name and schema options in your version.

### 6.5 Things to get right

- **Memory is not history.** Memory is what you send to the model (bounded by a window). History is the complete audit log. If you need both, store history separately.
- **Tie the conversation id to the user.** Never take it blindly from the request. If user A can guess user B's id, A can read B's chat. Derive it from the authenticated principal, for example `userId + ":" + threadId`.
- **Watch the token cost.** Every remembered message is resent on every call. A window of 20 messages costs more than a window of 6.
- **Tool messages:** in 2.x the memory advisor sits outside the tool loop by default, so only the final user and assistant messages are stored. That is safe for every repository. Storing the full tool transcript needs a repository that supports tool messages (in-memory, Redis and Neo4j do; the JDBC repository does not store them as of 2.0).

---

## 7. Tool Calling

### 7.1 What it is

Tool calling lets the model **ask your application to run a function** and use the result. The model never executes anything; Spring AI runs your Java method and sends the result back. This is the mechanism behind agents (Part 5 of the series).

### 7.2 `@Tool` on Java methods

```java
@Component
class TravelTools {

    @Tool(description = "Add the flight price and hotel total and say whether it fits the budget")
    String checkBudget(
            @ToolParam(description = "Round-trip flight price in rupees") int flightPrice,
            @ToolParam(description = "Total hotel price in rupees") int hotelTotal,
            @ToolParam(description = "Budget in rupees") int budget) {

        int total = flightPrice + hotelTotal;
        return total <= budget
                ? "Total Rs %d is within budget (Rs %d left)".formatted(total, budget - total)
                : "Total Rs %d is over budget by Rs %d".formatted(total, total - budget);
    }
}
```

Spring AI generates the JSON schema from the method signature. The **description is what the model reads** to decide when to call the tool, so write it like documentation for a colleague.

Pass tools to a call explicitly:

```java
String answer = chatClient.prompt()
        .user("Flight is Rs 8633 and the hotel is Rs 5014. Is that within Rs 13000?")
        .tools(travelTools)
        .call()
        .content();
```

Or register them for every call: `builder.defaultTools(travelTools)`.

### 7.3 Calling Spring services

A tool is a normal bean method, so it can use anything you inject: services, repositories, security context.

```java
@Component
class OrderTools {

    private final OrderService orders;

    OrderTools(OrderService orders) { this.orders = orders; }

    @Tool(description = "Look up the status of an order by its id")
    String orderStatus(@ToolParam(description = "Order id, for example 123-4567") String orderId) {
        return orders.findStatus(orderId);
    }
}
```

### 7.4 Calling external APIs

```java
@Component
class SerpApiClient {

    private final RestClient rest = RestClient.create("https://serpapi.com");
    private final String apiKey;

    SerpApiClient(@Value("${serpapi.key}") String apiKey) { this.apiKey = apiKey; }

    JsonNode flights(String from, String to, String out, String back) {
        return rest.get()
                .uri(u -> u.path("/search.json")
                        .queryParam("engine", "google_flights")
                        .queryParam("departure_id", from)
                        .queryParam("arrival_id", to)
                        .queryParam("outbound_date", out)
                        .queryParam("return_date", back)
                        .queryParam("currency", "INR")
                        .queryParam("api_key", apiKey)
                        .build())
                .retrieve()
                .body(JsonNode.class);   // Jackson 3 on Boot 4: tools.jackson.databind.JsonNode
    }
}

@Component
class FlightTools {

    private final SerpApiClient serp;

    FlightTools(SerpApiClient serp) { this.serp = serp; }

    @Tool(description = "Find the best round-trip flight price in rupees for the given airports and dates")
    String searchFlights(String origin, String destination,
                         @ToolParam(description = "yyyy-MM-dd") String outboundDate,
                         @ToolParam(description = "yyyy-MM-dd") String returnDate) {
        JsonNode result = serp.flights(origin, destination, outboundDate, returnDate);
        int price = result.path("best_flights").path(0).path("price").asInt(-1);
        return price < 0 ? "No flights found" : "Best round-trip flight: Rs " + price;
    }
}
```

Return a **short string or a small record**, not the whole API payload. The result goes back into the model's context, and a huge response wastes tokens and confuses small models. The SerpApi field names are the same ones used in the Python lab; confirm them against a live response.

### 7.5 Passing context the model should not see

```java
@Tool(description = "List the current user's saved trips")
List<String> savedTrips(ToolContext context) {
    String userId = (String) context.getContext().get("userId");
    return trips.findByUser(userId);
}

chatClient.prompt()
        .user("What trips have I saved?")
        .tools(tripTools)
        .toolContext(Map.of("userId", currentUser.id()))
        .call().content();
```

The user id travels in `ToolContext`, never in the prompt, so the model cannot change it.

### 7.6 Errors

If a tool throws, Spring AI by default sends the error text back to the model so it can recover or explain. Set `spring.ai.tools.throw-exception-on-error=true` to throw instead. Either way, validate arguments yourself: the model can pass wrong values.

### 7.7 Upgrading tool code from 1.x to 2.0

| 1.x | 2.0 |
| --- | --- |
| Bare `Function` beans resolved by name, `.toolNames("x")` | Register a `ToolCallback` bean (`FunctionToolCallback.builder(...)`) and pass it with `.tools(...)` |
| `internalToolExecutionEnabled(false)` | Removed; use `AdvisorParams.toolCallingAdvisorAutoRegister(false)` (chapter 10) |
| `ToolCallAdvisor` | Renamed `ToolCallingAdvisor` |
| Tool loop private to each chat model | Tool loop is an advisor in the chain, so it is observable and composable |


---

# Part 3: RAG and Vector Databases

## 8. Embeddings and Vector Stores

Part 4 of the series explained why embeddings let you search by meaning. This chapter is the Spring AI API for it.

### 8.1 `EmbeddingModel`

```java
@Service
class EmbeddingDemo {

    private final EmbeddingModel embeddingModel;

    EmbeddingDemo(EmbeddingModel embeddingModel) { this.embeddingModel = embeddingModel; }

    int dimensions() {
        float[] vector = embeddingModel.embed("cancel my order");
        return vector.length;       // 768 for nomic-embed-text
    }
}
```

Configure the embedding model next to the chat model. For local Ollama:

```bash
ollama pull nomic-embed-text
```

```yaml
spring:
  ai:
    ollama:
      embedding:
        options:
          model: nomic-embed-text
```

Rules that carry over from the series:

- Use the **same embedding model** to index documents and to embed queries.
- A different model means different vector sizes and meanings, so changing it requires **re-indexing** everything.

### 8.2 `VectorStore`

`VectorStore` is the portable interface; PGvector, Chroma, Redis, Qdrant, Milvus, Cassandra, Oracle, and many others implement it.

| Method | Purpose |
| --- | --- |
| `add(List<Document>)` | Embeds each document and stores text, metadata and vector |
| `similaritySearch(SearchRequest)` | Embeds the query and returns the closest documents |
| `delete(...)` | Removes documents by id or by filter |

A `Document` holds the text plus a metadata map you can filter on later.

### 8.3 Semantic search

```java
vectorStore.add(List.of(
        new Document("Refunds are accepted within 30 days of delivery.", Map.of("topic", "refund")),
        new Document("Standard shipping takes 5 to 7 business days.", Map.of("topic", "shipping"))));

List<Document> hits = vectorStore.similaritySearch(
        SearchRequest.builder()
                .query("How long do I have to send an item back?")
                .topK(2)
                .similarityThreshold(0.5)
                .build());
```

The query shares almost no words with the refund sentence, and it still comes back first. That is semantic search.

Filter by metadata with the portable expression syntax:

```java
SearchRequest.builder()
        .query("return window")
        .topK(4)
        .filterExpression("topic == 'refund'")
        .build();
```

### 8.4 PGvector

PGvector adds vector search to PostgreSQL, so you can keep documents, vectors and normal tables in one database you already operate.

**1. Run Postgres with the extension** (`compose.yaml`):

```yaml
services:
  pgvector:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_DB: ragdb
      POSTGRES_USER: rag
      POSTGRES_PASSWORD: ${DB_PASSWORD:-ragpass}     # default is for local development only
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

**2. Add dependencies:**

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-vector-store-pgvector</artifactId>
</dependency>
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

**3. Configure:**

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/ragdb
    username: rag
    password: ${DB_PASSWORD:ragpass}
  ai:
    vectorstore:
      pgvector:
        initialize-schema: true      # development only; manage the schema yourself in production
        dimensions: 768              # must match the embedding model
        distance-type: COSINE_DISTANCE
        index-type: HNSW
```

| Property | Meaning |
| --- | --- |
| `initialize-schema` | Creates the `vector_store` table and extension. Off by default; opt in for development |
| `dimensions` | Vector size; must equal the embedding model's output (768 for `nomic-embed-text`, 1536 for many OpenAI models) |
| `distance-type` | How closeness is measured; cosine is the usual choice for text |
| `index-type` | `HNSW` gives fast approximate search; no index means exact search |
| `table-name`, `schema-name` | Custom location; enable `schema-validation` if you change them |

The role Spring AI connects with must be allowed to create the `vector` extension when `initialize-schema` is true.

### 8.5 Choosing a vector store

| Option | Good for |
| --- | --- |
| PGvector | You already run PostgreSQL; moderate scale; transactions and SQL next to vectors |
| Chroma | Quick local experiments |
| Redis, Qdrant, Milvus, Elasticsearch | Dedicated or very large vector workloads |

Because `VectorStore` is an interface, you can start with one and change later by swapping the starter and its properties.

---

## 9. Document Ingestion and RAG

### 9.1 The pipeline

```
Document -> DocumentReader -> TextSplitter -> embed -> VectorStore        (ingestion, run once)
Question -> embed -> similaritySearch -> context + question -> LLM -> answer   (every request)
```

Spring AI calls the ingestion half the **ETL pipeline**: a `DocumentReader` extracts, a `DocumentTransformer` such as a splitter transforms, and a `DocumentWriter` (the `VectorStore`) loads.

### 9.2 Loading documents

| Source | Reader | Artifact |
| --- | --- | --- |
| PDF, page by page | `PagePdfDocumentReader` | `spring-ai-pdf-document-reader` |
| Markdown | `MarkdownDocumentReader` | `spring-ai-markdown-document-reader` |
| Word, HTML, many formats | `TikaDocumentReader` | `spring-ai-tika-document-reader` |
| Web pages | Jsoup reader | `spring-ai-jsoup-document-reader` |
| JSON, plain text | Built-in readers | in core |

`PagePdfDocumentReader` creates one `Document` per page and adds metadata such as the page number and file name, which you can use for citations.

### 9.3 Chunking

`TokenTextSplitter` splits documents into token-sized chunks:

```java
List<Document> chunks = TokenTextSplitter.builder().build().apply(pages);
```

Chunk size is a quality lever, as in the series: too large and retrieval is vague; too small and answers lose context. Start with the defaults, then test against real questions.

### 9.4 Ingest the Refund Policy PDF

```java
@Service
class IngestionService {

    private final VectorStore vectorStore;

    IngestionService(VectorStore vectorStore) { this.vectorStore = vectorStore; }

    int ingest(Resource pdf) {
        var reader = new PagePdfDocumentReader(pdf);                       // one Document per page
        List<Document> chunks = TokenTextSplitter.builder().build().apply(reader.get());
        vectorStore.add(chunks);                                           // embeds and stores
        return chunks.size();
    }
}
```

Run it once, from an upload endpoint or a startup runner guarded by a check, so restarts do not insert duplicates:

```java
@Bean
ApplicationRunner loadOnce(IngestionService ingestion, JdbcTemplate jdbc,
                           @Value("classpath:/docs/Amazon Refund policy.pdf") Resource pdf) {
    return args -> {
        Integer rows = jdbc.queryForObject("select count(*) from vector_store", Integer.class);
        if (rows != null && rows == 0) {
            System.out.println("Ingested " + ingestion.ingest(pdf) + " chunks");
        }
    };
}
```

### 9.5 Answer with RAG: `QuestionAnswerAdvisor`

The advisor searches the store with the user's question, adds the matching chunks to the prompt, and then calls the model.

```java
@Bean
ChatClient ragChatClient(ChatClient.Builder builder, VectorStore vectorStore) {
    return builder
            .defaultSystem("""
                    Answer only from the provided context, which comes from the Amazon refund policy.
                    If the context does not contain the answer, say you do not know.""")
            .defaultAdvisors(QuestionAnswerAdvisor.builder(vectorStore)
                    .searchRequest(SearchRequest.builder().topK(4).similarityThreshold(0.5).build())
                    .build())
            .build();
}
```

```java
String ask(String question) {
    return ragChatClient.prompt().user(question).call().content();
}
```

> **Compile error on `QuestionAnswerAdvisor`?** The vector store advisors live in their own module (`spring-ai-vector-store-advisor` in the 2.x line, previously `spring-ai-advisors-vector-store`). Add it if your starters did not bring it in.

Limit retrieval at runtime with a filter (use the metadata key your reader actually writes; print one chunk's metadata to check):

```java
ragChatClient.prompt()
        .user(question)
        .advisors(a -> a.param(QuestionAnswerAdvisor.FILTER_EXPRESSION, "file_name == 'Amazon Refund policy.pdf'"))
        .call().content();
```

### 9.6 More control: `RetrievalAugmentationAdvisor`

The modular RAG advisor (still marked incubating) lets you plug in each stage:

| Stage | Class | What it does |
| --- | --- | --- |
| Query transform | `RewriteQueryTransformer` | Rewrites a vague question into a better search query |
| Retrieve | `VectorStoreDocumentRetriever` | Searches the store with threshold, top-k and filters |
| Augment | `ContextualQueryAugmenter` | Builds the final prompt; can refuse when nothing is retrieved |

```java
Advisor rag = RetrievalAugmentationAdvisor.builder()
        .queryTransformers(RewriteQueryTransformer.builder()
                .chatClientBuilder(builder.clone()).build())
        .documentRetriever(VectorStoreDocumentRetriever.builder()
                .vectorStore(vectorStore).topK(4).similarityThreshold(0.5).build())
        .queryAugmenter(ContextualQueryAugmenter.builder().allowEmptyContext(false).build())
        .build();
```

`allowEmptyContext(false)` makes the model decline to answer when retrieval finds nothing, instead of guessing.

| Use | When |
| --- | --- |
| `QuestionAnswerAdvisor` | Straight question answering over one store |
| `RetrievalAugmentationAdvisor` | Query rewriting, multiple sources, strict "no context, no answer" behaviour |

### 9.7 Test it with real questions

Reuse the questions from the RAG lab and check each answer against the PDF:

1. Within how many days can most items be returned on Amazon.com? (30 days)
2. How are Pay on Delivery refunds handled on Amazon.in? (NEFT or Amazon Pay balance)
3. Can I get a cash refund on Amazon.in? (No)
4. What is the policy on returning pets? (Not in the document; the model should say it does not know)

The last question matters most: a good RAG app refuses instead of inventing an answer.

### 9.8 Showing sources

To return sources with the answer, run `vectorStore.similaritySearch(...)` yourself in the service and return the metadata (file name, page) next to the generated text.

---

# Part 4: Agents and MCP

## 10. Building AI Agents

### 10.1 What makes it an agent

Part 5 of the series: a chatbot answers; an **agent** decides, acts and loops until a goal is done. In Spring AI an agent is the sum of four things you already know:

| Ingredient | Spring AI piece |
| --- | --- |
| LLM that decides | `ChatClient` |
| Actions | `@Tool` methods and MCP tools (chapters 7, 11) |
| Memory | `ChatMemory` (chapter 6) |
| Loop | `ToolCallingAdvisor`, registered automatically |

In 2.x the model-calls-tool-calls-model loop is **an advisor in the chain**. It repeats until the model answers without requesting a tool.

### 10.2 The Goa trip agent

```java
@Bean
ChatClient tripAgent(ChatClient.Builder builder, ChatMemory memory) {
    return builder
            .defaultSystem("""
                    You are a travel-planning agent. Solve the goal by calling tools.
                    Plan:
                    1. searchFlights (best), note the price.
                    2. searchHotels (best), note the total price.
                    3. checkBudget with those two prices and the budget.
                    4. If over budget, search flights and hotels again with the cheapest option,
                       then checkBudget again with the NEW prices.
                    5. Reply with: Flight, Hotel, Total, and whether it is within budget.""")
            .defaultAdvisors(MessageChatMemoryAdvisor.builder(memory).build())
            .defaultTools(new FlightTools(serp), new HotelTools(serp), new BudgetTools())
            .build();
}
```

```java
String plan(String trip) {
    return tripAgent.prompt()
            .user("Plan a 3-day trip to Goa within Rs 13000. Fly HYD to GOX,GOI round trip on 2026-11-11, "
                + "returning 2026-11-14. Hotel in Goa for the same dates.")
            .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, trip))
            .call()
            .content();
}
```

The loop, tool execution and memory are handled by the framework. This is the same behaviour as the hand-written Python `run_agent()`.

### 10.3 Keeping agents on track

A small model may skip a step, as the Python lab showed (it never ran the cheaper hotel search). Defences, from cheapest to strongest:

| Defence | How |
| --- | --- |
| Clear plan in the system prompt | Numbered steps, as above |
| Let a tool do the maths | `checkBudget` computes the total; the model only reads the verdict |
| Verify the result in Java | Parse the final answer with `.entity(TripPlan.class)` and recompute the total in code |
| Control the loop yourself | See 10.4: you cap the steps and can insert approval |
| Use code for fixed workflows | See 10.5 |

### 10.4 Taking control of the loop

Turn the automatic loop off for one call, then execute tool calls yourself so you can limit steps, log each one, or ask for approval:

```java
ToolCallingManager toolManager = ToolCallingManager.builder().build();
ToolCallback[] tools = ToolCallbacks.from(new FlightTools(serp), new HotelTools(serp), new BudgetTools());
ChatOptions options = ToolCallingChatOptions.builder().toolCallbacks(tools).build();

String goal = "Plan a 3-day trip to Goa within Rs 13000 ...";
final int MAX_STEPS = 8;

ChatClientResponse response = chatClient.prompt()
        .user(goal)
        .options(options)
        .advisors(AdvisorParams.toolCallingAdvisorAutoRegister(false))   // no automatic loop
        .call()
        .chatClientResponse();

Prompt prompt = new Prompt(List.of(new UserMessage(goal)), options);

for (int step = 1; step <= MAX_STEPS
        && response.chatResponse() != null && response.chatResponse().hasToolCalls(); step++) {

    System.out.println("Step " + step + ": model requested tools");          // observe
    // Approval gate for risky tools could go here.
    ToolExecutionResult result = toolManager.executeToolCalls(prompt, response.chatResponse());

    prompt = new Prompt(result.conversationHistory(), options);
    response = chatClient.prompt()
            .messages(result.conversationHistory())
            .options(options)
            .advisors(AdvisorParams.toolCallingAdvisorAutoRegister(false))
            .call()
            .chatClientResponse();
}
String finalAnswer = response.chatResponse().getResult().getOutput().getText();
```

This is the Java equivalent of the Python loop's `max_steps` and per-step prints. (Imports omitted; all types live under `org.springframework.ai`.)

### 10.5 Use code where the steps are fixed

If the order of steps never changes, do not ask the model to follow it. Write the workflow in Java and use the LLM only where language is needed:

```java
TripResult plan(Trip trip) {
    int flight = travel.flightPrice(trip, Choice.BEST);
    int hotel  = travel.hotelTotal(trip, Choice.BEST);
    if (flight + hotel > trip.budget()) {                       // the "graph" is plain Java
        flight = travel.flightPrice(trip, Choice.CHEAPEST);
        hotel  = travel.hotelTotal(trip, Choice.CHEAPEST);
    }
    String summary = chatClient.prompt()
            .user("Write a friendly two-line summary: flight Rs %d, hotel Rs %d, budget Rs %d."
                    .formatted(flight, hotel, trip.budget()))
            .call().content();
    return new TripResult(flight, hotel, summary);
}
```

| Approach | Best when |
| --- | --- |
| Tool-calling agent | The path varies: the model decides which tool next |
| Controlled loop | You need step limits, approvals or detailed logging |
| Java workflow with an LLM step | The sequence is fixed and reliability matters most |

### 10.6 Agent safety basics

- Cap iterations, and set a timeout for the whole request.
- Give tools least privilege. A read-only search tool is low risk; "book" and "pay" tools need approval and audit logs (chapter 13).
- Log each tool call and its arguments.

---

## 11. Spring AI and MCP

Part 6 of the series: MCP is the standard way to connect models to tools and data. Spring AI supports both sides, as an **MCP client** that uses other servers' tools and as an **MCP server** that exposes yours.

### 11.1 Consuming an existing MCP server (client)

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-client</artifactId>
</dependency>
```

```yaml
spring:
  ai:
    mcp:
      client:
        stdio:
          connections:
            everything:
              command: npx
              args: "-y,@modelcontextprotocol/server-everything"
```

Auto-configuration starts the server, discovers its tools, and exposes them as a `SyncMcpToolCallbackProvider` bean. It is **not** attached to `ChatClient` automatically, because listing tools would call every server at startup. Wire it in yourself:

```java
@Bean
ChatClient mcpChatClient(ChatClient.Builder builder, SyncMcpToolCallbackProvider mcpTools) {
    return builder.defaultTools(mcpTools).build();
}
```

or per call: `chatClient.prompt().user("...").tools(mcpTools).call().content()`.

Start with this stdio example to prove your client wiring works, then point at your own server. Supported transports are STDIO, SSE and Streamable HTTP; the property block depends on the transport, so use the MCP client reference for the HTTP forms.

### 11.2 Exposing your Spring services as an MCP server

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server-webmvc</artifactId>
</dependency>
```

```java
@Component
class TravelMcpTools {

    @McpTool(description = "Add flight and hotel prices and say whether the total fits the budget")
    public String checkBudget(
            @McpToolParam(description = "Flight price in rupees") int flightPrice,
            @McpToolParam(description = "Hotel total in rupees") int hotelTotal,
            @McpToolParam(description = "Budget in rupees") int budget) {
        int total = flightPrice + hotelTotal;
        return total <= budget ? "WITHIN budget, Rs " + (budget - total) + " left"
                               : "OVER budget by Rs " + (total - budget);
    }
}
```

The server scans for `@McpTool` beans, generates schemas and registers them. Any MCP client can now use them, such as Claude Desktop, an IDE, or another Spring AI app. Choose the transport with the server properties (see the MCP server reference).

### 11.3 Tool discovery, mixing local and remote tools

Local `@Tool` methods and remote MCP tools share one interface, so you can combine them:

```java
chatClient.prompt()
        .user("Plan my trip")
        .tools(new LocalTools(), mcpTools)
        .call().content();
```

| Concern | What to do |
| --- | --- |
| Name clashes between servers | Spring AI prefixes duplicate names across MCP servers automatically |
| Clash between a local tool and an MCP tool | Rename one yourself, or filter the MCP one out |
| Untrusted or noisy servers | Register an `McpToolFilter` bean to allow only the tools you want |
| Hundreds of tools | Use the tool-search advisor (`spring.ai.chat.client.tool-search-advisor.enabled=true`) so the model discovers tools on demand instead of receiving all definitions every call |

### 11.4 Security reminder

MCP tools come from outside your code. Treat their names, descriptions and outputs as untrusted input, allow-list what you expose, and see chapter 13.


---

# Part 5: Production-Ready Spring AI

## 12. Advisors and Advanced Capabilities

### 12.1 The Advisors API

An **advisor** wraps a `ChatClient` call. It can change the request before the model sees it and change the response before you do. If you know servlet filters or AOP, this is the same idea.

```
request -> [Memory advisor] -> [RAG advisor] -> [Tool-calling advisor] -> model
response <-  ...             <-  ...          <-  ...                  <-
```

Memory, RAG, tool calling, structured-output validation and logging are all advisors. They run in a fixed order set by each advisor's `getOrder()`; the lower number runs first (outermost).

| Advisor | Purpose |
| --- | --- |
| `MessageChatMemoryAdvisor` | Load and save conversation history |
| `QuestionAnswerAdvisor`, `RetrievalAugmentationAdvisor` | RAG |
| `ToolCallingAdvisor` | The tool loop (auto-registered in 2.x) |
| `StructuredOutputValidationAdvisor` | Schema validation and retry |
| `SimpleLoggerAdvisor` | Log requests and responses |

### 12.2 Logging with `SimpleLoggerAdvisor`

```java
builder.defaultAdvisors(new SimpleLoggerAdvisor());
```

```yaml
logging:
  level:
    org.springframework.ai.chat.client.advisor: DEBUG
```

Prompts can contain personal data, so enable this in development only.

### 12.3 Writing your own advisor

```java
class TimingAdvisor implements CallAdvisor {

    private static final Logger log = LoggerFactory.getLogger(TimingAdvisor.class);

    @Override public String getName() { return "TimingAdvisor"; }

    @Override public int getOrder() { return Ordered.HIGHEST_PRECEDENCE + 100; }   // outside memory and tools

    @Override
    public ChatClientResponse adviseCall(ChatClientRequest request, CallAdvisorChain chain) {
        long start = System.nanoTime();
        ChatClientResponse response = chain.nextCall(request);        // continue down the chain
        log.info("LLM call took {} ms", (System.nanoTime() - start) / 1_000_000);
        return response;
    }
}
```

Register it with `defaultAdvisors(new TimingAdvisor())`. Streaming needs a `StreamAdvisor` as well. Typical uses: timing, audit logs, input checks, PII masking, caching, guardrails.

> **Order matters.** In 2.x the memory advisor runs outside the tool loop (order `HIGHEST_PRECEDENCE + 200`) and the tool-calling advisor sits at `HIGHEST_PRECEDENCE + 300`. An advisor placed after the tool advisor sees every loop iteration; one placed before sees only the final result.

### 12.4 RAG advisors

Covered in chapter 9: `QuestionAnswerAdvisor` for the simple case, `RetrievalAugmentationAdvisor` for query rewriting and strict context rules.

### 12.5 Multimodal AI

Some models accept images (and audio) alongside text. Attach media to the user message:

```java
String description = chatClient.prompt()
        .user(u -> u.text("Describe what this receipt shows.")
                .media(MimeTypeUtils.IMAGE_PNG, new ClassPathResource("/images/receipt.png")))
        .call()
        .content();
```

Spring AI's model API also covers **image generation, audio transcription and text-to-speech**, using separate model interfaces and starters. Check that your chosen model and provider support the media type.

### 12.6 Model selection

| Need | Choose |
| --- | --- |
| Local development, offline, free | Ollama with a tool-capable model such as `llama3.1` |
| Best quality for hard reasoning | A large hosted model |
| Cheap and fast for simple tasks | A small hosted model |
| Reliable tool calling | A model documented to support tools; test with your real tools |
| Private data that cannot leave your network | Self-hosted model |

Override model and temperature **per call** with portable options:

```java
String answer = chatClient.prompt()
        .user(question)
        .options(ChatOptions.builder().model("<model-name>").temperature(0.0).build())
        .call()
        .content();
```

Use temperature near 0 for extraction and tool use, and higher only for creative text. Because the `ChatModel` API is portable, you can compare models by changing configuration and re-running the same tests (chapter 13).

---

## 13. Testing, Observability and Security

### 13.1 Testing AI responses

LLM output varies between runs, so exact-string assertions fail. Test in layers:

| Layer | What to test | How |
| --- | --- | --- |
| Pure Java | Tools, parsers, workflow code | Normal JUnit tests, no model needed (`checkBudget(8633, 5014, 13000)` returns "over budget") |
| Service with a stubbed model | Your logic around the model | Hide `ChatClient` behind your own interface and mock that |
| Integration with a real model | Prompts, RAG quality | Real call with a low temperature and flexible assertions |
| Evaluation | Is the answer relevant and grounded? | An `Evaluator` that uses an LLM as judge |

**Evaluators** ask a model to grade another model's answer:

```java
@SpringBootTest
class RefundRagEvalTest {

    @Autowired ChatClient.Builder builder;
    @Autowired VectorStore vectorStore;
    @Autowired RefundAssistant assistant;      // your service wrapping the RAG ChatClient

    @Test
    void answerIsSupportedByTheDocument() {
        String question = "Within how many days can most items be returned on Amazon.com?";
        String answer = assistant.ask(question);

        String context = vectorStore.similaritySearch(question).stream()
                .map(Document::getText).collect(Collectors.joining("\n"));

        var factChecker = new FactCheckingEvaluator(builder);
        EvaluationResponse result = factChecker.evaluate(
                new EvaluationRequest(context, Collections.emptyList(), answer));

        assertThat(result.isPass()).isTrue();
    }
}
```

`RelevancyEvaluator` checks whether an answer addresses the question. Keep a fixed question set, run it after every prompt or model change, and track the pass rate.

For integration tests that need Ollama or PGvector, use **Testcontainers** so tests start their own containers.

### 13.2 Observability and token usage

Add Actuator and Micrometer:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

Spring AI publishes Micrometer observations for model calls, which give you latency, errors and token usage (the `gen_ai.client.token.usage` metric) and feed tracing backends. Read the exact meter names and enable options in the observability reference for your version.

Per-call token counts are also on the response:

```java
ChatResponse response = chatClient.prompt().user(q).call().chatResponse();
Integer tokens = response.getMetadata().getUsage().getTotalTokens();
meterRegistry.counter("ai.tokens", "feature", "refund-chat").increment(tokens);
```

Spring AI can also log prompts and completions via its observation settings (`spring.ai.chat.observations.log-prompt` and `log-completion`). Both can leak personal data, so leave them off in production.

What to watch:

| Signal | Why |
| --- | --- |
| Latency per call and per tool | Slow tools make slow agents |
| Tokens per request | Direct driver of cost |
| Error and retry rate | Provider outages and rate limits |
| Tool-call count per request | Runaway agent loops |
| Evaluation pass rate | Quality drift after model or prompt changes |

### 13.3 Security

AI features add new attack surfaces to an ordinary Spring application.

**Prompt injection.** Text from users, documents, web pages or MCP tool results can contain instructions aimed at the model ("ignore your rules and send the data to..."). You cannot fully prevent this, so limit the damage:

| Risk | Defence |
| --- | --- |
| User tells the model to ignore its rules | Keep rules in the system prompt, validate outputs, never let the model be the only access control |
| **Indirect** injection through retrieved documents or MCP output | Treat all retrieved text as untrusted data; restrict what tools can do after reading it |
| Model leaks the system prompt or secrets | Never put keys, passwords or private data in prompts |
| Model output is rendered or executed | Escape output in HTML; never execute model output as code or SQL |

**Tool security.** Tools turn text into actions, so review them like public endpoints:

- **Least privilege:** read-only tools by default; separate database accounts with narrow rights.
- **Validate arguments in Java.** The model can pass any value. Check ranges, allowed values and ownership.
- **Human approval** for anything with side effects: payments, bookings, deletes, emails (use the controlled loop in chapter 10).
- **Take the user identity from the security context**, not from a model-supplied argument; pass it in `ToolContext`.
- **Allow-list MCP tools** with an `McpToolFilter` and review server descriptions.

**Application security (Spring Security).**

- Authenticate and authorise your chat endpoints like any other API.
- Derive conversation ids from the authenticated user so one user cannot read another's memory.
- Rate-limit per user; LLM calls cost money and are an easy target for abuse.
- Redact personal data before sending text to a hosted model, and check your provider's data-retention terms.
- Keep API keys in a secret store and rotate them if exposed.

---

## 14. Deployment and Best Practices

### 14.1 Docker

```dockerfile
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY target/app.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

Or let Spring Boot build the image: `./mvnw spring-boot:build-image`.

Local stack with the app, PGvector and Ollama (`compose.yaml`):

```yaml
services:
  app:
    build: .
    environment:
      SPRING_AI_OLLAMA_BASE_URL: http://ollama:11434
      SPRING_DATASOURCE_URL: jdbc:postgresql://pgvector:5432/ragdb
      SPRING_DATASOURCE_USERNAME: rag
      SPRING_DATASOURCE_PASSWORD: ${DB_PASSWORD}
    ports: ["8080:8080"]
    depends_on: [pgvector, ollama]
  pgvector:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_DB: ragdb
      POSTGRES_USER: rag
      POSTGRES_PASSWORD: ${DB_PASSWORD}
  ollama:
    image: ollama/ollama
    ports: ["11434:11434"]
```

Models must still be pulled inside the Ollama container (`docker exec ... ollama pull llama3.1`).

### 14.2 Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-app
spec:
  replicas: 2
  selector:
    matchLabels: { app: ai-app }
  template:
    metadata:
      labels: { app: ai-app }
    spec:
      containers:
        - name: ai-app
          image: registry.example.com/ai-app:1.0.0
          ports:
            - containerPort: 8080
          env:
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef: { name: ai-secrets, key: openai-api-key }
          readinessProbe:
            httpGet: { path: /actuator/health/readiness, port: 8080 }
          livenessProbe:
            httpGet: { path: /actuator/health/liveness, port: 8080 }
          resources:
            requests: { cpu: "500m", memory: "768Mi" }
            limits: { memory: "1Gi" }
```

Most production deployments call a hosted model API. Running a model yourself (Ollama or similar) needs GPU planning and its own Deployment.

### 14.3 Error handling and retries

Spring AI retries transient failures for you; tune it:

```yaml
spring:
  ai:
    retry:
      max-attempts: 3
      backoff:
        initial-interval: 2s
        multiplier: 2
        max-interval: 20s
```

Translate AI failures into clean HTTP errors:

```java
@RestControllerAdvice
class AiExceptionHandler {

    @ExceptionHandler(TransientAiException.class)       // org.springframework.ai.retry
    ResponseEntity<String> transientFailure(TransientAiException e) {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body("The AI service is busy. Try again shortly.");
    }

    @ExceptionHandler(NonTransientAiException.class)
    ResponseEntity<String> permanentFailure(NonTransientAiException e) {
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body("The AI service rejected the request.");
    }
}
```

Also set HTTP timeouts (for example `spring.http.client.read-timeout`), because model calls can be slow, and design a **fallback**: a cached answer, a smaller model, or a clear "try again" message.

### 14.4 Performance

| Technique | Effect |
| --- | --- |
| Stream responses | Users see text sooner |
| Virtual threads (`spring.threads.virtual.enabled=true`) | Many concurrent slow LLM calls without a big thread pool |
| Smaller `topK` and tighter chunks | Less context, faster and cheaper calls |
| Cache repeated answers (Spring Cache) | Skips the model entirely for common questions |
| Batch embeddings during ingestion | Faster indexing |
| HNSW index in PGvector | Fast similarity search at scale |
| Parallel independent calls | Run unrelated LLM calls at the same time |

### 14.5 Cost optimisation

Cost is driven by **tokens in plus tokens out**.

| Lever | How |
| --- | --- |
| Smaller models for simple tasks | Route easy requests to a cheap model |
| Shorter prompts | Trim the system prompt; avoid pasting whole documents |
| Smaller memory window | Fewer old messages resent each call |
| Fewer retrieved chunks | `topK` 3 to 4 is often enough |
| Cap output | Set `max-tokens` |
| Return short tool results | Do not feed whole API payloads back into the context |
| Cache | Same question, same answer, no call |
| Track usage per feature | Token metrics with alerts (chapter 13) |

### 14.6 Best-practices checklist

- [ ] Model and temperature chosen per task; temperature near 0 for tools and extraction
- [ ] Prompts stored in files and versioned
- [ ] Answers grounded in retrieved context; "I do not know" is allowed
- [ ] Tools have clear descriptions, validated arguments and least privilege
- [ ] Loops capped by step count and timeout
- [ ] Conversation ids tied to authenticated users
- [ ] Keys in a secret store; prompt logging off in production
- [ ] Retries, timeouts and a fallback configured
- [ ] Token usage and latency monitored
- [ ] A fixed question set runs as an evaluation after every change

---

# Hands-On Projects

## Project 1: AI Chat REST API

**Goal:** a Spring Boot service with a chat endpoint, streaming, and per-conversation memory.

**You will use:** chapters 2 to 6.

**Build steps**

1. Create the project (Spring Web, Ollama) and the configuration from chapter 2.
2. Define the `ChatClient` bean with a default system prompt and the memory advisor (chapter 6).
3. Add the controller:

```java
record ChatRequest(String conversationId, String message) {}
record ChatReply(String conversationId, String reply) {}

@RestController
@RequestMapping("/api/chat")
class ChatController {

    private final ChatClient chatClient;

    ChatController(ChatClient chatClient) { this.chatClient = chatClient; }

    @PostMapping
    ChatReply chat(@RequestBody ChatRequest req) {
        String id = req.conversationId() != null ? req.conversationId() : UUID.randomUUID().toString();
        String reply = chatClient.prompt()
                .user(req.message())
                .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, id))
                .call()
                .content();
        return new ChatReply(id, reply);
    }

    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    Flux<String> stream(@RequestBody ChatRequest req) {
        String id = req.conversationId() != null ? req.conversationId() : UUID.randomUUID().toString();
        return chatClient.prompt()
                .user(req.message())
                .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, id))
                .stream()
                .content();
    }
}
```

4. Add the exception handler from chapter 14 and a request size limit.
5. Test multi-turn memory:

```bash
curl -s -X POST localhost:8080/api/chat -H 'Content-Type: application/json' \
     -d '{"conversationId":"t1","message":"Plan Goa within Rs 13000"}'
curl -s -X POST localhost:8080/api/chat -H 'Content-Type: application/json' \
     -d '{"conversationId":"t1","message":"Make it 4 nights"}'
```

**Done when**

- [ ] The second call remembers the city and the budget
- [ ] A different `conversationId` starts fresh
- [ ] `/stream` returns tokens progressively
- [ ] A stopped Ollama returns a clean 5xx message, not a stack trace

**Stretch:** persist memory with the JDBC repository; return a typed `TripPlan` with `.entity(...)`.

## Project 2: Chat with PDF Documents (Spring AI and PGvector)

**Goal:** upload a PDF, then ask questions that are answered only from it. Use the Amazon refund policy PDF.

**You will use:** chapters 8 and 9.

**Build steps**

1. Start PGvector with the `compose.yaml` from chapter 8 and add the PGvector and datasource configuration (dimensions 768 for `nomic-embed-text`).
2. Pull the models: `ollama pull llama3.1` and `ollama pull nomic-embed-text`.
3. Add the `IngestionService` from chapter 9 and an upload endpoint:

```java
@PostMapping("/api/docs")
Map<String, Integer> upload(@RequestParam("file") MultipartFile file) {
    return Map.of("chunks", ingestion.ingest(file.getResource()));
}
```

4. Add the RAG `ChatClient` with `QuestionAnswerAdvisor` and an `/api/ask` endpoint.
5. Run the four test questions from section 9.7 and check each answer against the PDF.
6. Write an evaluation test (chapter 13) over 10 questions.

**Done when**

- [ ] Answers match the PDF (30 days, NEFT or Amazon Pay balance, no cash refunds)
- [ ] The "returning pets" question gets "I do not know"
- [ ] Restarting the app does not duplicate chunks
- [ ] The evaluation test passes and runs in the build

**Stretch:** return sources (file and page) with each answer; compare `QuestionAnswerAdvisor` with `RetrievalAugmentationAdvisor` using query rewriting.

## Project 3: AI Agent with Java Tools and MCP

**Goal:** the Goa trip agent in Java, with its tools also available over MCP.

**You will use:** chapters 7, 10 and 11.

**Build steps**

1. Create the tool beans `FlightTools`, `HotelTools` and `BudgetTools` (chapter 7), using SerpApi with the key in `SERPAPI_KEY`.
2. Build the `tripAgent` client from chapter 10 with the plan in the system prompt and the memory advisor. Test with a Rs 15,000 budget, then Rs 13,000.
3. Switch to the controlled loop (10.4) to cap steps and log each tool call.
4. Move the tools into a second Spring Boot app with `spring-ai-starter-mcp-server-webmvc` and `@McpTool` (chapter 11).
5. In the agent app, add `spring-ai-starter-mcp-client`, point it at your server (first prove the client works with the `server-everything` example), and register the provider with `defaultTools(mcpTools)`.
6. Add an `McpToolFilter` so the agent can only use the tools you intended.

**Done when**

- [ ] With a tight budget the agent searches the cheapest hotel and flight before giving a final answer
- [ ] The final total is recomputed in Java and matches the answer
- [ ] The run stops after at most 8 tool rounds
- [ ] The same tools work from the MCP server when the agent app uses them remotely

**Stretch:** add an approval step before any "book" tool; try the Java workflow version (10.5) and compare reliability with the model-driven version.

---

## Appendix: Cheat sheet

| Task | Code |
| --- | --- |
| Simple call | `chatClient.prompt().user(q).call().content()` |
| System prompt | `.system("...")` or `builder.defaultSystem("...")` |
| Template | `.user(u -> u.text("... {x}").param("x", v))` |
| Typed output | `.call().entity(MyRecord.class)` |
| Stream | `.stream().content()` returns `Flux<String>` |
| Memory | `defaultAdvisors(MessageChatMemoryAdvisor.builder(memory).build())` and `.advisors(a -> a.param(ChatMemory.CONVERSATION_ID, id))` |
| Tool | `@Tool(description="...")` on a method, then `.tools(bean)` |
| Embed | `embeddingModel.embed("text")` |
| Store | `vectorStore.add(docs)` |
| Search | `vectorStore.similaritySearch(SearchRequest.builder().query(q).topK(4).build())` |
| RAG | `QuestionAnswerAdvisor.builder(vectorStore).build()` |
| Ingest | `PagePdfDocumentReader`, then `TokenTextSplitter.builder().build().apply(...)`, then `vectorStore.add(...)` |
| MCP client | `spring-ai-starter-mcp-client`, then `defaultTools(mcpToolCallbackProvider)` |
| MCP server | `spring-ai-starter-mcp-server-webmvc` and `@McpTool` |
| Step-limited agent loop | `AdvisorParams.toolCallingAdvisorAutoRegister(false)` and `ToolCallingManager` |
| Token usage | `response.getMetadata().getUsage().getTotalTokens()` |
| Evaluate | `new FactCheckingEvaluator(builder).evaluate(new EvaluationRequest(context, List.of(), answer))` |

**Where to confirm details:** this handbook was written against Spring AI 2.0.x. Spring AI changes quickly, so check the [Spring AI reference](https://docs.spring.io/spring-ai/reference/) for your exact version when a class or property name differs, especially around tool calling, memory repositories and MCP transports.

