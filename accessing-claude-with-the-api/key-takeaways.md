# Key takeways

## The Five-Step Request Flow
Why is this important?
- Helps design secure architectures that protect your API keys
- Set appropriate token limits for your use case
- Handle different stop reasons in your application logic
- Debug issues by understanding where they might occur in the pipeline

### 1. Request to server
Requests to Anthropic should be made from a server under our control. This is a layer between the client and the Anthropic API that helps with Anthropic SDK and API Key security.

### 2. Request to Anthropic API
Official SDK recommended (python, typescript, javascript, go and ruby). Must provide
- API Key - Identifies your request to Anthropic
- Model - Name of the model to use (like "claude-3-sonnet")
- Messages - List containing the user's input text
- Max Tokens - Limit for how many tokens Claude can generate

### 3. Model Processing
Once Anthropic receives the request, Claude processes it through four main stages: tokenization, embedding, contextualization, and generation. This process is complex, high level overview below.

1. tokenization: messages or user input broken down into smaller chunks, also known as tokens
2. embedding: tokens are converted into an embedding, a number based definition of a given token
3. contextualization: used to refine an embedding into a single precise definition, adjusted based on other embeddings around it, helps highlight the meaning of each embedding that makes the most sense given its neighbors
4. generation: the contextualized embeddings pass through an output layer that calculates probabilities for each possible next word. Claude doesn't always pick the highest probability word, it uses a mix of probability and controlled randomness to create natural, varied responses. After selecting each word, Claude adds it to the sequence and repeats the entire process for the next word.
 

After each token, Claude checks several conditions to decide whether to continue:
- Max tokens reached - Has it hit the limit you specified?
- Natural ending - Did it generate an end-of-sequence token?
- Stop sequence - Did it encounter a predefined stop phrase?

### 4. Response to server

When generation completes, the API sends back a structured response containing:
- Message - The generated text
- Usage - Count of input and output tokens
- Stop Reason - Why generation ended

#### Stop Reasons
- `end_turn` - Natural completion
- `max_tokens` - Token limit reached
- `stop_sequence` - Predefined stop phrase encountered
- `tool_use` - Tool call requested (agentic loops)

### 5. Response to client
Your server receives this response and forwards the generated text back to your client application, where it appears in the user interface.
