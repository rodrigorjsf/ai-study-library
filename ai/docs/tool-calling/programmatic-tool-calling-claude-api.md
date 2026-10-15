# Programmatic tool calling

> Source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling.md — mirrored 2026-10-11 (previous capture ~2026-05-01). The previous capture of this file was a condensed summary of the tool use overview page (`https://docs.anthropic.com/en/docs/build-with-claude/tool-use`, which on 2026-10-11 redirects to `https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview`), not of the dedicated programmatic tool calling page. This file now mirrors both, verbatim: Part 1 is the dedicated programmatic tool calling page; Part 2 (appended at the end, under its own H1) is the tool use overview that the previous capture named as its source.

**Category:** Programmatic Tool Calling

**Related documentation**: tool search has its own page, not mirrored here: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool>. Strict tool use is mirrored at [../structured-outputs/anthropic-strict-tool-use.md](../structured-outputs/anthropic-strict-tool-use.md).

Page frontmatter as served (verbatim):

```yaml
title: Programmatic tool calling
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling
description: Let Claude call your tools from code in the code execution container, cutting model round trips and token use in multi-tool workflows.
featureMetadata:
  status: ga
  zdr: not-eligible
  supportedModels:
    - claude-fable-5-1
    - claude-mythos-5-1
    - claude-fable-5
    - claude-mythos-5
    - claude-opus-5-5
    - claude-opus-5
    - claude-opus-4-8
    - claude-opus-4-7
    - claude-opus-4-6
    - claude-opus-4-5-20251101
    - claude-sonnet-5-5
    - claude-sonnet-5
    - claude-sonnet-4-6
    - claude-sonnet-4-5-20250929
    - claude-haiku-5-5
  supportedPlatforms:
    Claude API: ga
    Claude Platform on AWS: ga
    Microsoft Foundry:
      availability: ga
      note: On [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), programmatic tool calling requires a [Hosted on Anthropic deployment](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure).
  details:
    - Programmatic tool calling requires the code execution tool with the `code_execution_20260120` or later [tool version](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#tool-versions).
    - Claude Haiku 4.5 accepts the `code_execution_20260120` and later tool versions but doesn't support programmatic tool calling.
```

---

Programmatic tool calling allows Claude to write code that calls your tools programmatically within a [code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) container, rather than requiring round trips through the model for each tool invocation. This reduces latency for multi-tool workflows and decreases token consumption by allowing Claude to filter or process data before it reaches the model's context window. On agentic search benchmarks like [BrowseComp](https://arxiv.org/abs/2504.12516) and [DeepSearchQA](https://github.com/google-deepmind/deepsearchqa), which test multistep web research and complex information retrieval, adding programmatic tool calling on top of basic search tools improved performance by an average of 11% while using 24% fewer input tokens (see [Improved web search with dynamic filtering](https://claude.com/blog/improved-web-search-with-dynamic-filtering)).

Consider checking budget compliance across 20 employees: the traditional approach requires 20 separate model round-trips, pulling thousands of expense line items into the context along the way. With programmatic tool calling, a single script runs all 20 lookups, filters the results, and returns only the employees who exceeded their limits, shrinking what Claude needs to reason over from hundreds of kilobytes down to a handful of lines.

<Tip>
  For a deeper look at the inference and context costs that programmatic tool calling addresses, see [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use).
</Tip>

Programmatic tool calling requires the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) with tool version `code_execution_20260120` or later. To check whether a model supports programmatic tool calling before you send a request, read its `capabilities.code_execution.supported` value from the Models API. [Using the Models API](https://platform.claude.com/docs/en/models/overview#using-the-models-api) describes the field.

## Quick start

Here's an example where Claude programmatically queries a database multiple times and aggregates results. Adding `allowed_callers: ["code_execution_20260120"]` to a tool definition is what makes that tool callable from within code execution (see [The `allowed_callers` field](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#the-allowed-callers-field)):

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --data '{
          "model": "claude-opus-5-5",
          "max_tokens": 4096,
          "messages": [
              {
                  "role": "user",
                  "content": "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue"
              }
          ],
          "tools": [
              {
                  "type": "code_execution_20260120",
                  "name": "code_execution"
              },
              {
                  "name": "query_database",
                  "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "sql": {
                              "type": "string",
                              "description": "SQL query to execute"
                          }
                      },
                      "required": ["sql"]
                  },
                  "allowed_callers": ["code_execution_20260120"]
              }
          ]
      }'
  ```

  ```bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5-5
  max_tokens: 4096
  messages:
    - role: user
      content: >-
        Query sales data for the West, East, and Central regions, then
        tell me which region had the highest revenue
  tools:
    - type: code_execution_20260120
      name: code_execution
    - name: query_database
      description: >-
        Execute a SQL query against the sales database. Returns a list
        of rows as JSON objects.
      input_schema:
        type: object
        properties:
          sql:
            type: string
            description: SQL query to execute
        required:
          - sql
      allowed_callers:
        - code_execution_20260120
  YAML
  ```

  ```python Python
  client = anthropic.Anthropic()

  response = client.messages.create(
      model="claude-opus-5-5",
      max_tokens=4096,
      messages=[
          {
              "role": "user",
              "content": "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue",
          }
      ],
      tools=[
          {"type": "code_execution_20260120", "name": "code_execution"},
          {
              "name": "query_database",
              "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "sql": {"type": "string", "description": "SQL query to execute"}
                  },
                  "required": ["sql"],
              },
              "allowed_callers": ["code_execution_20260120"],
          },
      ],
  )

  print(response)
  ```

  ```typescript TypeScript
  const client = new Anthropic();

  const response = await client.messages.create({
    model: "claude-opus-5-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content:
          "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue"
      }
    ],
    tools: [
      {
        type: "code_execution_20260120",
        name: "code_execution"
      },
      {
        name: "query_database",
        description:
          "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
        input_schema: {
          type: "object" as const,
          properties: {
            sql: {
              type: "string",
              description: "SQL query to execute"
            }
          },
          required: ["sql"]
        },
        allowed_callers: ["code_execution_20260120"]
      }
    ]
  });

  console.log(response);
  ```

  ```csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5_5,
      MaxTokens = 4096,
      Messages = [
          new() {
              Role = Role.User,
              Content = "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue"
          }
      ],
      Tools = [
          new CodeExecutionTool20260120(),
          new ToolUnion(new Tool()
          {
              Name = "query_database",
              Description = "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["sql"] = JsonSerializer.SerializeToElement(new { type = "string", description = "SQL query to execute" }),
                  },
                  Required = ["sql"],
              },
              AllowedCallers = ["code_execution_20260120"]
          }),
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);
  ```

  ```go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5_5,
  	MaxTokens: 4096,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20260120: &anthropic.CodeExecutionTool20260120Param{}},
  		{OfTool: &anthropic.ToolParam{
  			Name:        "query_database",
  			Description: anthropic.String("Execute a SQL query against the sales database. Returns a list of rows as JSON objects."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"sql": map[string]any{
  						"type":        "string",
  						"description": "SQL query to execute",
  					},
  				},
  				Required: []string{"sql"},
  			},
  			AllowedCallers: []string{"code_execution_20260120"},
  		}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())
  ```

  ```java Java
  import com.anthropic.models.messages.CodeExecutionTool20260120;
  // ...

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5_5)
          .maxTokens(4096L)
          .addUserMessage("Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue")
          .addTool(CodeExecutionTool20260120.builder().build())
          .addTool(Tool.builder()
              .name("query_database")
              .description("Execute a SQL query against the sales database. Returns a list of rows as JSON objects.")
              .inputSchema(InputSchema.builder()
                  .properties(JsonValue.from(Map.of(
                      "sql", Map.of(
                          "type", "string",
                          "description", "SQL query to execute"
                      )
                  )))
                  .putAdditionalProperty("required", JsonValue.from(List.of("sql")))
                  .build())
              .allowedCallers(List.of(Tool.AllowedCaller.of("code_execution_20260120")))
              .build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }
  ```

  ```php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          ['role' => 'user', 'content' => 'Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue'],
      ],
      model: 'claude-opus-5-5',
      tools: [
          [
              'type' => 'code_execution_20260120',
              'name' => 'code_execution',
          ],
          [
              'name' => 'query_database',
              'description' => 'Execute a SQL query against the sales database. Returns a list of rows as JSON objects.',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'sql' => [
                          'type' => 'string',
                          'description' => 'SQL query to execute',
                      ],
                  ],
                  'required' => ['sql'],
              ],
              'allowed_callers' => ['code_execution_20260120'],
          ],
      ],
  );

  echo $message;
  ```

  ```ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5-5",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue"
      }
    ],
    tools: [
      {
        type: "code_execution_20260120",
        name: "code_execution"
      },
      {
        name: "query_database",
        description: "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
        input_schema: {
          type: "object",
          properties: {
            sql: {
              type: "string",
              description: "SQL query to execute"
            }
          },
          required: ["sql"]
        },
        allowed_callers: ["code_execution_20260120"]
      }
    ]
  )

  puts message
  ```
</CodeGroup>

The response stops with `stop_reason: "tool_use"`, a `container` ID, and a `tool_use` block for `query_database` whose `caller` field identifies the code execution run that called it. Return the result as shown in [Step 3 of the example workflow](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#step-3-provide-tool-result) so the code can finish.

## How programmatic tool calling works

When you configure a tool to be callable from code execution and Claude determines that tool is needed:

1. Claude writes Python code that invokes the tool as a function, potentially including multiple tool calls and pre/post-processing logic
2. Claude runs this code in a sandboxed container through code execution
3. When a tool function is called, code execution pauses and the API returns a `tool_use` block
4. You provide the tool result, and code execution continues (intermediate results are not loaded into Claude's context window)
5. Once all code execution completes, Claude receives the final output and continues working on the task

This approach is particularly useful for:

* **Large data processing:** Filter or aggregate tool results before they reach Claude's context
* **Multistep workflows:** Save tokens and latency by calling tools serially or in a loop without sampling Claude in-between tool calls
* **Conditional logic:** Make decisions based on intermediate tool results

<Note>
  Tools that allow a code execution caller are exposed to Claude's code as async Python functions, so Claude can run them in parallel with `asyncio.gather`. Each function takes a single dict of arguments and returns a string: the text of the `tool_result` you send back. Claude's code awaits these functions with top-level `await` and parses results that it needs as structured data, for example `rows = json.loads(await query_database({"sql": "<sql>"}))`.
</Note>

## Core concepts

### The `allowed_callers` field

The `allowed_callers` field specifies which contexts can invoke a tool:

```json
{
  "name": "query_database",
  "description": "Execute a SQL query against the database",
  "input_schema": {
    // ...
  },
  "allowed_callers": ["code_execution_20260120"]
}
```

**Possible values:**

* `["direct"]` - Claude is guided to call this tool directly (default if omitted)
* `["code_execution_20260120"]` - Claude is guided to call this tool only from within code execution
* `["direct", "code_execution_20260120"]` - Claude may call this tool directly or from within code execution

Both `"code_execution_20260120"` and `"code_execution_20260521"` are accepted in `allowed_callers` and are interchangeable: a request using either code-execution tool version satisfies tools that list either caller. Response blocks always tag the caller as `code_execution_20260120` regardless of which version the request declared.

<Tip>
  Choose either `["direct"]` or `["code_execution_20260120"]` for each tool rather than enabling both, as this provides clearer guidance to Claude for how best to use the tool.
</Tip>

<Note>
  `allowed_callers` controls how the tool is presented to Claude and is validated against `tool_choice`, but it is not a hard API-level block on direct invocation. Claude is strongly guided to respect it, but your client should still be prepared to handle a direct `tool_use` for any tool it defines. Do not rely on `allowed_callers` as a security boundary.
</Note>

### The `caller` field in responses

Every tool use block includes a `caller` field indicating how it was invoked:

**Direct invocation (traditional tool use):**

```json
{
  "type": "tool_use",
  "id": "toolu_abc123",
  "name": "query_database",
  "input": { "sql": "<sql>" },
  "caller": { "type": "direct" }
}
```

**Programmatic invocation:**

```json
{
  "type": "tool_use",
  "id": "toolu_xyz789",
  "name": "query_database",
  "input": { "sql": "<sql>" },
  "caller": {
    "type": "code_execution_20260120",
    "tool_id": "srvtoolu_abc123"
  }
}
```

The `tool_id` is the `id` of the code execution `server_tool_use` block that made the call, so you can match each programmatic `tool_use` to the code execution run that produced it.

### Container lifecycle

Programmatic tool calling uses the same containers as code execution:

* **Container creation:** A new container is created for each request unless you reuse an existing one
* **Container ID:** Returned in responses in the `container` field, along with an `expires_at` timestamp
* **Reuse:** Pass the container ID back on the next request to keep state. While a programmatic tool call is waiting for your result, the container ID is required on that request, not optional: the API rejects the request without it.
* **Expiration:** `expires_at` tells you how long the container has left. Idle containers are currently reclaimed after about 5 minutes, and no container can be reused more than 30 days after it was created.

<Warning>
  While Claude's code is waiting for a programmatic tool result, the pending call times out after about 4 minutes and raises a `TimeoutError` inside the code. Return each tool result well before the `expires_at` timestamp on the paused response. See [Container expiration during tool call](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#container-expiration-during-tool-call).
</Warning>

## Example workflow

Here's how a complete programmatic tool calling flow works:

### Step 1: Initial request

Send a request with code execution and a tool that allows programmatic calling. To enable programmatic calling, add the `allowed_callers` field to your tool definition.

<Note>
  Provide detailed descriptions of your tool's output format in the tool description. If you specify that the tool returns JSON, Claude attempts to deserialize and process the result in code. The more detail you provide about the output schema, the better Claude can handle the response programmatically.
</Note>

The request shape is identical to the [Quick start](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#quick-start) example: include `code_execution` in your tools list, add `allowed_callers: ["code_execution_20260120"]` to any tool you want Claude to invoke from code, and send your user message. The remaining steps in this workflow use the user message `"Query customer purchase history from the last quarter and identify our top 5 customers by revenue"`.

### Step 2: API response with tool call

Claude writes code that calls your tool. The API pauses and returns:

```json Output
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "I'll query the purchase history and analyze the results."
    },
    {
      "type": "server_tool_use",
      "id": "srvtoolu_abc123",
      "name": "code_execution",
      "input": {
        "code": "import json\n\nrows = json.loads(await query_database({'sql': '<sql>'}))\ntop_customers = sorted(rows, key=lambda x: x['revenue'], reverse=True)[:5]\nprint(f'Top 5 customers: {top_customers}')"
      }
    },
    {
      "type": "tool_use",
      "id": "toolu_def456",
      "name": "query_database",
      "input": { "sql": "<sql>" },
      "caller": {
        "type": "code_execution_20260120",
        "tool_id": "srvtoolu_abc123"
      }
    }
  ],
  "container": {
    "id": "container_xyz789",
    "expires_at": "2026-01-20T14:30:00Z"
  },
  "stop_reason": "tool_use"
}
```

### Step 3: Provide tool result

Send the full conversation history plus your tool result. Three details matter on this request:

* The user message that carries your result can contain only `tool_result` blocks. See [Message formatting restrictions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#message-formatting-restrictions).
* Pass the `container` ID from the paused response. The API rejects a continuation that has pending programmatic tool calls but no container ID.
* Send the same `tools` array as the original request. The code execution tool must still be present for the paused code to resume, and the tools you send on this request are the definitions Claude and the running code can use for the rest of the turn.

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
      --header "x-api-key: $ANTHROPIC_API_KEY" \
      --header "anthropic-version: 2023-06-01" \
      --header "content-type: application/json" \
      --data '{
          "model": "claude-opus-5-5",
          "max_tokens": 4096,
          "container": "container_xyz789",
          "messages": [
              {
                  "role": "user",
                  "content": "Query customer purchase history from the last quarter and identify our top 5 customers by revenue"
              },
              {
                  "role": "assistant",
                  "content": [
                      {
                          "type": "text",
                          "text": "I'\''ll query the purchase history and analyze the results."
                      },
                      {
                          "type": "server_tool_use",
                          "id": "srvtoolu_abc123",
                          "name": "code_execution",
                          "input": {"code": "..."}
                      },
                      {
                          "type": "tool_use",
                          "id": "toolu_def456",
                          "name": "query_database",
                          "input": {"sql": "<sql>"},
                          "caller": {
                              "type": "code_execution_20260120",
                              "tool_id": "srvtoolu_abc123"
                          }
                      }
                  ]
              },
              {
                  "role": "user",
                  "content": [
                      {
                          "type": "tool_result",
                          "tool_use_id": "toolu_def456",
                          "content": "[{\"customer_id\": \"C1\", \"revenue\": 45000}, {\"customer_id\": \"C2\", \"revenue\": 38000}]"
                      }
                  ]
              }
          ],
          "tools": [
              {
                  "type": "code_execution_20260120",
                  "name": "code_execution"
              },
              {
                  "name": "query_database",
                  "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
                  "input_schema": {
                      "type": "object",
                      "properties": {
                          "sql": {
                              "type": "string",
                              "description": "SQL query to execute"
                          }
                      },
                      "required": ["sql"]
                  },
                  "allowed_callers": ["code_execution_20260120"]
              }
          ]
      }'
  ```

  ```bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5-5
  max_tokens: 4096
  container: container_xyz789
  messages:
    - role: user
      content: >-
        Query customer purchase history from the last quarter and identify our
        top 5 customers by revenue
    - role: assistant
      content:
        - type: text
          text: I'll query the purchase history and analyze the results.
        - type: server_tool_use
          id: srvtoolu_abc123
          name: code_execution
          input:
            code: "..."
        - type: tool_use
          id: toolu_def456
          name: query_database
          input:
            sql: "<sql>"
          caller:
            type: code_execution_20260120
            tool_id: srvtoolu_abc123
    - role: user
      content:
        - type: tool_result
          tool_use_id: toolu_def456
          content: >-
            [{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2",
            "revenue": 38000}, ...]
  # Same tools array as the original request
  tools:
    - type: code_execution_20260120
      name: code_execution
    - name: query_database
      description: >-
        Execute a SQL query against the sales database. Returns a list
        of rows as JSON objects.
      input_schema:
        type: object
        properties:
          sql:
            type: string
            description: SQL query to execute
        required:
          - sql
      allowed_callers:
        - code_execution_20260120
  YAML
  ```

  ```python Python
  response = client.messages.create(
      model="claude-opus-5-5",
      max_tokens=4096,
      container="container_xyz789",  # Reuse the container
      messages=[
          {
              "role": "user",
              "content": "Query customer purchase history from the last quarter and identify our top 5 customers by revenue",
          },
          {
              "role": "assistant",
              "content": [
                  {
                      "type": "text",
                      "text": "I'll query the purchase history and analyze the results.",
                  },
                  {
                      "type": "server_tool_use",
                      "id": "srvtoolu_abc123",
                      "name": "code_execution",
                      "input": {"code": "..."},
                  },
                  {
                      "type": "tool_use",
                      "id": "toolu_def456",
                      "name": "query_database",
                      "input": {"sql": "<sql>"},
                      "caller": {
                          "type": "code_execution_20260120",
                          "tool_id": "srvtoolu_abc123",
                      },
                  },
              ],
          },
          {
              "role": "user",
              "content": [
                  {
                      "type": "tool_result",
                      "tool_use_id": "toolu_def456",
                      "content": '[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]',
                  }
              ],
          },
      ],
      # Same tools array as the original request
      tools=[
          {"type": "code_execution_20260120", "name": "code_execution"},
          {
              "name": "query_database",
              "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
              "input_schema": {
                  "type": "object",
                  "properties": {
                      "sql": {"type": "string", "description": "SQL query to execute"}
                  },
                  "required": ["sql"],
              },
              "allowed_callers": ["code_execution_20260120"],
          },
      ],
  )

  print(response)
  ```

  ```typescript TypeScript
  const response = await client.messages.create({
    model: "claude-opus-5-5",
    max_tokens: 4096,
    container: "container_xyz789", // Reuse the container
    messages: [
      {
        role: "user",
        content:
          "Query customer purchase history from the last quarter and identify our top 5 customers by revenue"
      },
      {
        role: "assistant",
        content: [
          { type: "text", text: "I'll query the purchase history and analyze the results." },
          {
            type: "server_tool_use",
            id: "srvtoolu_abc123",
            name: "code_execution",
            input: { code: "..." }
          },
          {
            type: "tool_use",
            id: "toolu_def456",
            name: "query_database",
            input: { sql: "<sql>" },
            caller: {
              type: "code_execution_20260120",
              tool_id: "srvtoolu_abc123"
            }
          }
        ]
      },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: "toolu_def456",
            content:
              '[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]'
          }
        ]
      }
    ],
    // Same tools array as the original request
    tools: [
      {
        type: "code_execution_20260120",
        name: "code_execution"
      },
      {
        name: "query_database",
        description:
          "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
        input_schema: {
          type: "object" as const,
          properties: {
            sql: {
              type: "string",
              description: "SQL query to execute"
            }
          },
          required: ["sql"]
        },
        allowed_callers: ["code_execution_20260120"]
      }
    ]
  });

  console.log(response);
  ```

  ```csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5_5,
      MaxTokens = 4096,
      Container = "container_xyz789",
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = "Query customer purchase history from the last quarter and identify our top 5 customers by revenue"
          },
          new()
          {
              Role = Role.Assistant,
              Content = new ContentBlock[]
              {
                  new TextBlock { Text = "I'll query the purchase history and analyze the results." },
                  new ServerToolUseBlock
                  {
                      Id = "srvtoolu_abc123",
                      Name = "code_execution",
                      Input = new { code = "..." }
                  },
                  new ToolUseBlock
                  {
                      Id = "toolu_def456",
                      Name = "query_database",
                      Input = new { sql = "<sql>" },
                      Caller = new ToolCaller
                      {
                          Type = "code_execution_20260120",
                          ToolId = "srvtoolu_abc123"
                      }
                  }
              }
          },
          new()
          {
              Role = Role.User,
              Content = new ContentBlockParam[]
              {
                  new ToolResultBlockParam
                  {
                      ToolUseID = "toolu_def456",
                      Content = "[{\"customer_id\": \"C1\", \"revenue\": 45000}, {\"customer_id\": \"C2\", \"revenue\": 38000}, ...]"
                  }
              }
          }
      ],
      // Same tools array as the original request
      Tools = [
          new CodeExecutionTool20260120(),
          new ToolUnion(new Tool()
          {
              Name = "query_database",
              Description = "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
              InputSchema = new InputSchema()
              {
                  Properties = new Dictionary<string, JsonElement>
                  {
                      ["sql"] = JsonSerializer.SerializeToElement(new { type = "string", description = "SQL query to execute" }),
                  },
                  Required = ["sql"],
              },
              AllowedCallers = ["code_execution_20260120"]
          }),
      ]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message);
  ```

  ```go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5_5,
  	MaxTokens: 4096,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfString: anthropic.String("container_xyz789"),
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Query customer purchase history from the last quarter and identify our top 5 customers by revenue")),
  		{
  			Role: anthropic.MessageParamRoleAssistant,
  			Content: []anthropic.ContentBlockParamUnion{
  				anthropic.NewTextBlock("I'll query the purchase history and analyze the results."),
  				{OfServerToolUse: &anthropic.ServerToolUseBlockParam{
  					ID:    "srvtoolu_abc123",
  					Name:  anthropic.ServerToolUseBlockParamNameCodeExecution,
  					Input: map[string]any{"code": "..."},
  				}},
  				{OfToolUse: &anthropic.ToolUseBlockParam{
  					ID:    "toolu_def456",
  					Name:  "query_database",
  					Input: map[string]any{"sql": "<sql>"},
  					Caller: anthropic.ServerToolUseBlockParamCallerUnion{
  						OfCodeExecution20260120: &anthropic.ServerToolCaller20260120Param{
  							ToolID: "srvtoolu_abc123",
  						},
  					},
  				}},
  			},
  		},
  		{
  			Role: anthropic.MessageParamRoleUser,
  			Content: []anthropic.ContentBlockParamUnion{
  				{OfToolResult: &anthropic.ToolResultBlockParam{
  					ToolUseID: "toolu_def456",
  					Content: []anthropic.ToolResultBlockParamContentUnion{
  						{OfText: &anthropic.TextBlockParam{
  							Text: `[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]`,
  						}},
  					},
  				}},
  			},
  		},
  	},
  	// Same tools array as the original request
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20260120: &anthropic.CodeExecutionTool20260120Param{}},
  		{OfTool: &anthropic.ToolParam{
  			Name:        "query_database",
  			Description: anthropic.String("Execute a SQL query against the sales database. Returns a list of rows as JSON objects."),
  			InputSchema: anthropic.ToolInputSchemaParam{
  				Properties: map[string]any{
  					"sql": map[string]any{
  						"type":        "string",
  						"description": "SQL query to execute",
  					},
  				},
  				Required: []string{"sql"},
  			},
  			AllowedCallers: []string{"code_execution_20260120"},
  		}},
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.RawJSON())
  ```

  ```java Java
  import com.anthropic.models.messages.CodeExecutionTool20260120;
  // ...

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5_5)
          .maxTokens(4096L)
          .container("container_xyz789")
          .addUserMessage("Query customer purchase history from the last quarter and identify our top 5 customers by revenue")
          .addAssistantMessageOfBlockParams(List.of(
              ContentBlockParam.ofText(
                  TextBlockParam.builder()
                      .text("I'll query the purchase history and analyze the results.")
                      .build()),
              ContentBlockParam.ofServerToolUse(
                  ServerToolUseBlockParam.builder()
                      .id("srvtoolu_abc123")
                      .name("code_execution")
                      .input(JsonValue.from(Map.of("code", "...")))
                      .build()),
              ContentBlockParam.ofToolUse(
                  ToolUseBlockParam.builder()
                      .id("toolu_def456")
                      .name("query_database")
                      .input(JsonValue.from(Map.of("sql", "<sql>")))
                      .codeExecution20260120Caller("srvtoolu_abc123")
                      .build())
          ))
          .addUserMessageOfBlockParams(List.of(
              ContentBlockParam.ofToolResult(
                  ToolResultBlockParam.builder()
                      .toolUseId("toolu_def456")
                      .content("[{\"customer_id\": \"C1\", \"revenue\": 45000}, {\"customer_id\": \"C2\", \"revenue\": 38000}, ...]")
                      .build())
          ))
          // Same tools array as the original request
          .addTool(CodeExecutionTool20260120.builder().build())
          .addTool(Tool.builder()
              .name("query_database")
              .description("Execute a SQL query against the sales database. Returns a list of rows as JSON objects.")
              .inputSchema(InputSchema.builder()
                  .properties(JsonValue.from(Map.of(
                      "sql", Map.of(
                          "type", "string",
                          "description", "SQL query to execute"
                      )
                  )))
                  .putAdditionalProperty("required", JsonValue.from(List.of("sql")))
                  .build())
              .allowedCallers(List.of(Tool.AllowedCaller.of("code_execution_20260120")))
              .build())
          .build();

      Message response = client.messages().create(params);
      IO.println(response);
  }
  ```

  ```php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 4096,
      messages: [
          [
              'role' => 'user',
              'content' => 'Query customer purchase history from the last quarter and identify our top 5 customers by revenue',
          ],
          [
              'role' => 'assistant',
              'content' => [
                  [
                      'type' => 'text',
                      'text' => "I'll query the purchase history and analyze the results.",
                  ],
                  [
                      'type' => 'server_tool_use',
                      'id' => 'srvtoolu_abc123',
                      'name' => 'code_execution',
                      'input' => ['code' => '...'],
                  ],
                  [
                      'type' => 'tool_use',
                      'id' => 'toolu_def456',
                      'name' => 'query_database',
                      'input' => ['sql' => '<sql>'],
                      'caller' => [
                          'type' => 'code_execution_20260120',
                          'tool_id' => 'srvtoolu_abc123',
                      ],
                  ],
              ],
          ],
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'tool_result',
                      'tool_use_id' => 'toolu_def456',
                      'content' => '[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]',
                  ],
              ],
          ],
      ],
      model: 'claude-opus-5-5',
      container: 'container_xyz789',
      // Same tools array as the original request
      tools: [
          [
              'type' => 'code_execution_20260120',
              'name' => 'code_execution',
          ],
          [
              'name' => 'query_database',
              'description' => 'Execute a SQL query against the sales database. Returns a list of rows as JSON objects.',
              'input_schema' => [
                  'type' => 'object',
                  'properties' => [
                      'sql' => [
                          'type' => 'string',
                          'description' => 'SQL query to execute',
                      ],
                  ],
                  'required' => ['sql'],
              ],
              'allowed_callers' => ['code_execution_20260120'],
          ],
      ],
  );

  echo $message;
  ```

  ```ruby Ruby
  require "anthropic"

  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5-5",
    max_tokens: 4096,
    container: "container_xyz789",
    messages: [
      {
        role: "user",
        content: "Query customer purchase history from the last quarter and identify our top 5 customers by revenue"
      },
      {
        role: "assistant",
        content: [
          {
            type: "text",
            text: "I'll query the purchase history and analyze the results."
          },
          {
            type: "server_tool_use",
            id: "srvtoolu_abc123",
            name: "code_execution",
            input: { code: "..." }
          },
          {
            type: "tool_use",
            id: "toolu_def456",
            name: "query_database",
            input: { sql: "<sql>" },
            caller: {
              type: "code_execution_20260120",
              tool_id: "srvtoolu_abc123"
            }
          }
        ]
      },
      {
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: "toolu_def456",
            content: '[{"customer_id": "C1", "revenue": 45000}, {"customer_id": "C2", "revenue": 38000}, ...]'
          }
        ]
      }
    ],
    # Same tools array as the original request
    tools: [
      {
        type: "code_execution_20260120",
        name: "code_execution"
      },
      {
        name: "query_database",
        description: "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
        input_schema: {
          type: "object",
          properties: {
            sql: {
              type: "string",
              description: "SQL query to execute"
            }
          },
          required: ["sql"]
        },
        allowed_callers: ["code_execution_20260120"]
      }
    ]
  )

  puts message
  ```
</CodeGroup>

### Step 4: Next tool call or completion

The code picks up where it paused and processes your result. Each continuation response either pauses again with more programmatic `tool_use` blocks, or completes the code execution and lets Claude continue the turn (Step 5). Check `stop_reason` and each `tool_use` block's `caller` to tell the two apart: a response that pauses for you has `stop_reason: "tool_use"` and a `tool_use` block whose `caller` names a code execution version, and you repeat Step 3 with a `tool_result` for every pending programmatic call in one user message.

### Step 5: Final response

Once the code execution completes, Claude provides the final response:

```json Output
{
  "content": [
    {
      "type": "code_execution_tool_result",
      "tool_use_id": "srvtoolu_abc123",
      "content": {
        "type": "code_execution_result",
        "stdout": "Top 5 customers: [{'customer_id': 'C1', 'revenue': 45000}, {'customer_id': 'C2', 'revenue': 38000}, {'customer_id': 'C5', 'revenue': 32000}, {'customer_id': 'C8', 'revenue': 28500}, {'customer_id': 'C3', 'revenue': 24000}]",
        "stderr": "",
        "return_code": 0,
        "content": []
      }
    },
    {
      "type": "text",
      "text": "I've analyzed the purchase history from last quarter. Your top 5 customers generated $167,500 in total revenue, with Customer C1 leading at $45,000."
    }
  ],
  "stop_reason": "end_turn"
}
```

## Advanced patterns

### Batch processing with loops

Claude can write code that processes multiple items efficiently:

```python
regions = ["West", "East", "Central", "North", "South"]
results = {}
for region in regions:
    rows = json.loads(await query_database({"sql": f"<sql for {region}>"}))
    results[region] = sum(row["revenue"] for row in rows)

# Process results programmatically
top_region = max(results.items(), key=lambda x: x[1])
print(f"Top region: {top_region[0]} with ${top_region[1]:,} in revenue")
```

This pattern:

* Reduces model round-trips from N (one per region) to 1
* Processes large result sets programmatically before returning to Claude
* Saves tokens by only returning aggregated conclusions instead of raw data

### Early termination

Claude can stop processing as soon as success criteria are met:

```python
endpoints = ["us-east", "eu-west", "apac"]
for endpoint in endpoints:
    status = await check_health({"endpoint": endpoint})
    if status == "healthy":
        print(f"Found healthy endpoint: {endpoint}")
        break  # Stop early, don't check remaining
```

### Conditional tool selection

```python
path = "/tmp/example.txt"
file_info = json.loads(await get_file_info({"path": path}))
if file_info["size"] < 10000:
    content = await read_full_file({"path": path})
else:
    content = await read_file_summary({"path": path})
print(content)
```

### Data filtering

```python
server_id = "srv-01"
log_text = await fetch_logs({"server_id": server_id})
errors = [line for line in log_text.splitlines() if "ERROR" in line]
print(f"Found {len(errors)} errors")
for error in errors[-10:]:  # Only return last 10 errors
    print(error)
```

## Response format

### Programmatic tool call

When code execution calls a tool:

```json
{
  "type": "tool_use",
  "id": "toolu_abc123",
  "name": "query_database",
  "input": { "sql": "<sql>" },
  "caller": {
    "type": "code_execution_20260120",
    "tool_id": "srvtoolu_xyz789"
  }
}
```

### Tool result handling

Your tool result is passed back to the running code:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_abc123",
      "content": "[{\"customer_id\": \"C1\", \"revenue\": 45000, \"orders\": 23}, {\"customer_id\": \"C2\", \"revenue\": 38000, \"orders\": 18}, ...]"
    }
  ]
}
```

### Code execution completion

When all tool calls are satisfied and code completes:

```json
{
  "type": "code_execution_tool_result",
  "tool_use_id": "srvtoolu_xyz789",
  "content": {
    "type": "code_execution_result",
    "stdout": "Analysis complete. Top 5 customers identified from 847 total records.",
    "stderr": "",
    "return_code": 0,
    "content": []
  }
}
```

## Error handling

### Common errors

| Error                                      | Where it appears                                                             | Description                                                                    | Solution                                                                                                                         |
| ------------------------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `invalid_tool_input`                       | `error_code` on the `code_execution_tool_result` error block in the response | Invalid parameters were passed to the code execution tool                      | See the [code execution tool errors](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#errors)   |
| `invalid_request_error` (on `tool_choice`) | HTTP 400 error response                                                      | `tool_choice` names a tool whose `allowed_callers` does not include `"direct"` | Either add `"direct"` to that tool's `allowed_callers`, or remove the tool from `tool_choice` and let Claude invoke it from code |

### Container expiration during tool call

If your tool result doesn't arrive within about 4 minutes, the pending call raises a `TimeoutError` inside Claude's running code. Claude sees the error in `stderr` and typically retries the call:

```json
{
  "type": "code_execution_tool_result",
  "tool_use_id": "srvtoolu_abc123",
  "content": {
    "type": "code_execution_result",
    "stdout": "",
    "stderr": "TimeoutError: Calling tool ['query_database'] timed out (no response after 270s).",
    "return_code": 0,
    "content": []
  }
}
```

To prevent timeouts:

* Monitor the `expires_at` field in responses
* Implement timeouts for your tool execution
* Consider breaking long operations into smaller chunks

### Tool execution errors

If your tool returns an error:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_abc123",
  "content": "Error: Query timeout - table lock exceeded 30 seconds"
}
```

Claude's code receives this error and can handle it appropriately.

## Constraints and limitations

### Feature incompatibilities

* **Structured outputs:** Tools with `strict: true` are not supported with programmatic calling
* **Tool choice:** You cannot force programmatic calling of a specific tool through `tool_choice`
* **Parallel tool use:** `disable_parallel_tool_use: true` is not supported with programmatic calling

### Input schema limitations

Custom tools whose `input_schema` contains a recursive `$ref` (a reference cycle, such as a schema that refers to itself) cannot be enabled for programmatic calling. Including a code execution tool version in `allowed_callers` for such a tool causes the request to fail with a `400 invalid_request_error` whose message contains `Circular $ref detected`. The same schema is accepted for direct tool calling.

To work around this, do one of the following:

* Keep the tool direct-only by omitting `allowed_callers` (or setting it to `["direct"]`). Other tools in the same request can still use programmatic calling.
* Remove the cycle from the schema. For example, unroll the recursion to a fixed depth and describe any deeper nesting in the `description` of the innermost level, or replace the recursive property with a plain `{"type": "object"}` whose `description` explains the expected shape.

### Tool restrictions

The following tools cannot be called programmatically:

* Tools provided by an [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
* The [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) toolsets (`computer_toolset_20260801` and `browser_toolset_20260801`), whose `allowed_callers` field accepts only `"direct"`

### Message formatting restrictions

When responding to programmatic tool calls, there are strict formatting requirements:

**Tool result only responses:** If there are pending programmatic tool calls waiting for results, your response message must contain **only** `tool_result` blocks. You cannot include any text content, even after the tool results.

Invalid - Cannot include text when responding to programmatic tool calls:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01",
      "content": "[{\"customer_id\": \"C1\", \"revenue\": 45000}]"
    },
    { "type": "text", "text": "What should I do next?" }
  ]
}
```

Valid - Only tool results when responding to programmatic tool calls:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01",
      "content": "[{\"customer_id\": \"C1\", \"revenue\": 45000}]"
    }
  ]
}
```

This restriction only applies when responding to programmatic (code execution) tool calls. For regular client-side tool calls, you can include text content after tool results.

**Text-only tool result content:** The `content` of each `tool_result` that answers a programmatic call must be a string or `text` blocks. Image, document, and other content block types are rejected.

### Rate limits

Programmatic tool calls are subject to the same rate limits as regular tool calls. Each tool call from code execution counts as a separate invocation.

### Validate tool results before use

When implementing user-defined tools that will be called programmatically:

* **Tool results are returned as strings:** They can contain any content, including code snippets or executable commands that may be processed by the execution environment.
* **Validate external tool results:** If your tool returns data from external sources or accepts user input, be aware of code injection risks if the output will be interpreted or executed as code.

## Token efficiency

Programmatic tool calling reduces token consumption in three ways:

* **Tool results from programmatic calls are not added to Claude's context** - only the final code output is
* **Intermediate processing happens in code** - filtering, aggregation, and other transformations don't consume model tokens
* **Multiple tool calls in one code execution** - reduces overhead compared to separate model turns

For example, calling 10 tools directly uses \~10x the tokens of calling them programmatically and returning a summary.

In Anthropic's internal evaluations on a production Claude model:

* On a 75-tool project-management agent benchmark, enabling programmatic tool calling reduced billed input tokens by roughly 38% with no change in task accuracy.
* On [τ²-bench](https://arxiv.org/abs/2506.07982) (airline, retail, and telecom domains), where each turn makes one or two sequential tool calls, programmatic tool calling left scores unchanged and cost roughly 8% more. Sequential single-call workflows do not benefit.
* Across production API traffic, requests whose `tools` array contains 10 to 49 tool definitions see typical token savings of 20% to 40% with programmatic tool calling enabled.

Actual savings vary with workload shape. See [When to use programmatic calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#when-to-use-programmatic-calling).

## Usage and pricing

Programmatic tool calling uses the same pricing as code execution. See the [code execution pricing](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#usage-and-pricing) for details.

<Note>
  Token counting for programmatic tool calls: Tool results from programmatic invocations do not count toward your input/output token usage. Only the final code execution result and Claude's response count.
</Note>

## Best practices

### Tool design

* **Provide detailed output descriptions:** Because Claude deserializes tool results in code, document the format (JSON structure and field types)
* **Return structured data:** JSON or other machine-readable formats work best for programmatic processing
* **Keep responses concise:** Return only necessary data to minimize processing overhead

### When to use programmatic calling

Programmatic tool calling trades a small fixed overhead (container startup, script generation) for large savings on tool-result tokens and model round-trips. Whether that trade pays off depends on workload shape.

**Strong fit:**

* Fan-out or parallel operations across many items (for example, checking 50 endpoints or looking up 20 records)
* Large tool results that can be filtered, aggregated, or summarized before reaching Claude's context
* Agentic search and retrieval, where iterative querying and result filtering dominate the workflow

**Weak fit:**

* Strictly sequential workflows where each call depends on Claude reasoning over the previous result, because the script cannot skip the model round-trip in that case
* A small number of tool calls with small responses, especially on the first turn of a conversation, where container and script overhead can exceed the savings
* Tools that require immediate user feedback between calls

If you are unsure, measure billed input tokens with and without `allowed_callers` on a representative sample of your traffic before enabling it broadly.

### Performance optimization

* **Reuse containers** when making multiple related requests to maintain state
* **Batch similar operations** in a single code execution when possible

## Troubleshooting

### Common issues

**`invalid_request_error` when setting `tool_choice`**

* `tool_choice` cannot name a tool whose `allowed_callers` omits `"direct"`. Either add `"direct"` to that tool's `allowed_callers`, or remove the tool from `tool_choice` and let Claude invoke it from code.

**Container expiration**

* Respond to each programmatic tool call well before the paused response's `expires_at` timestamp. Claude's code stops waiting for a result after about 4 minutes, and idle containers are currently reclaimed after about 5 minutes.
* Consider implementing faster tool execution

**Tool result not parsed correctly**

* Ensure your tool returns string data that Claude can deserialize
* Provide clear output format documentation in your tool description

### Debugging tips

1. **Log all tool calls and results** to track the flow
2. **Check the `caller` field** to confirm programmatic invocation
3. **Monitor container IDs** to ensure proper reuse
4. **Test tools independently** before enabling programmatic calling

## Why programmatic tool calling works

Claude is trained on large amounts of code, so presenting tools as callable Python functions lets it use that strength:

* **Tool composition:** Chained calls, loops, and conditionals are ordinary Python control flow instead of a series of model round trips
* **Result processing:** Claude's code filters and aggregates large tool outputs, or writes them to files, and only the final output enters the context window
* **Latency:** The model is not re-sampled between the tool calls inside one code execution

## Alternative implementations

Programmatic tool calling is a generalizable pattern that can also be implemented on your own infrastructure. Here's how the approaches compare:

### Client-side direct execution

Provide Claude with a code execution tool and describe what functions are available in that environment. When Claude invokes the tool with code, your application executes it locally where those functions are defined.

**Advantages:**

* Minimal re-architecting of your application
* Full control over the environment and instructions

**Disadvantages:**

* Executes untrusted code outside of a sandbox
* Tool invocations can be vectors for code injection

**Use when:** Your application can safely execute arbitrary code, you want the smallest implementation, and Anthropic's managed offering doesn't fit your needs.

### Self-managed sandboxed execution

Same approach from Claude's perspective, but code runs in a sandboxed container with security restrictions (for example, no network egress). If your tools require external resources, you'll need a protocol for executing tool calls outside the sandbox.

**Advantages:**

* Safe programmatic tool calling on your own infrastructure
* Full control over the execution environment

**Disadvantages:**

* Complex to build and maintain
* Requires managing both infrastructure and inter-process communication

**Use when:** Security is critical and Anthropic's managed solution doesn't fit your requirements.

### Anthropic-managed execution

Anthropic's programmatic tool calling is a managed version of sandboxed execution with an opinionated Python environment tuned for Claude. Anthropic handles container management, code execution, and secure tool invocation communication.

**Advantages:**

* Safe and secure by default
* Enabled with a tool definition, with no infrastructure to run
* Environment and instructions optimized for Claude

Consider using Anthropic's managed solution if you're using the Claude API, [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), or [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). On Microsoft Foundry, programmatic tool calling requires a [Hosted on Anthropic deployment](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure).

## Data retention

Programmatic tool calling is built on the code execution infrastructure and uses the same sandbox containers. Container data, including execution artifacts and outputs, is retained for up to 30 days.

For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).

## Next steps

<CardGroup cols={2}>
  <Card title="Fine-grained tool streaming" icon="bolt" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming">
    Stream tool inputs without server-side JSON buffering for latency-sensitive applications.
  </Card>

  <Card title="Code execution tool" icon="code" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool">
    Run Python and bash code in a sandboxed container to analyze data, generate files, and iterate on solutions.
  </Card>

  <Card title="Tool use with Claude" icon="wrench" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview">
    Connect Claude to external tools and APIs. See where tools execute, when Claude calls them, and which tool fits your task.
  </Card>

  <Card title="Define tools" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Specify tool schemas, write effective descriptions, and control when Claude calls your tools.
  </Card>
</CardGroup>

---

<!-- Part 2: appended verbatim mirror of the tool use overview page -->

# Tool use with Claude

> Source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview.md — mirrored 2026-10-11 (previous capture ~2026-05-01). Part 2 of this file: the tool use overview page named as the source of the previous capture.

Page frontmatter as served (verbatim):

```yaml
title: Tool use with Claude
url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
description: Connect Claude to external tools and APIs. See where tools execute, when Claude calls them, and which tool fits your task.
```

---

Tool use (also called function calling) lets Claude call functions that you define or that Anthropic provides. Claude determines when to call a tool based on the user's request and the tool's description. It then returns a structured call that your application executes (client tools) or that Anthropic executes (server tools).

Here's a minimal example using a server tool, the [Web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool), which Anthropic executes for you:

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5-5",
      "max_tokens": 1024,
      "tools": [{"type": "web_search_20260209", "name": "web_search"}],
      "messages": [{"role": "user", "content": "What'\''s the latest on the Mars rover?"}]
    }'
  ```

  ```bash CLI
  ant messages create --transform content --format yaml \
    --model claude-opus-5-5 \
    --max-tokens 1024 \
    --tool '{type: web_search_20260209, name: web_search}' \
    --message '{role: user, content: "What is the latest on the Mars rover?"}'
  ```

  ```python Python
  client = anthropic.Anthropic()
  response = client.messages.create(
      model="claude-opus-5-5",
      max_tokens=1024,
      tools=[{"type": "web_search_20260209", "name": "web_search"}],
      messages=[{"role": "user", "content": "What's the latest on the Mars rover?"}],
  )
  print(response.content)
  ```

  ```typescript TypeScript
  const client = new Anthropic();
  const response = await client.messages.create({
    model: "claude-opus-5-5",
    max_tokens: 1024,
    tools: [{ type: "web_search_20260209", name: "web_search" }],
    messages: [{ role: "user", content: "What's the latest on the Mars rover?" }]
  });
  console.log(response.content);
  ```

  ```csharp C#
  AnthropicClient client = new();

  var parameters = new MessageCreateParams
  {
      Model = Model.ClaudeOpus5_5,
      MaxTokens = 1024,
      Tools = [new ToolUnion(new WebSearchTool20260209())],
      Messages = [new() { Role = Role.User, Content = "What's the latest on the Mars rover?" }]
  };

  var message = await client.Messages.Create(parameters);
  Console.WriteLine(message.Content);
  ```

  ```go Go
  client := anthropic.NewClient()

  response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5_5,
  	MaxTokens: 1024,
  	Tools: []anthropic.ToolUnionParam{
  		{OfWebSearchTool20260209: &anthropic.WebSearchTool20260209Param{}},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("What's the latest on the Mars rover?")),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }
  fmt.Println(response.Content)
  ```

  ```java Java
  import com.anthropic.models.messages.WebSearchTool20260209;

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      MessageCreateParams params = MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5_5)
          .maxTokens(1024L)
          .addTool(WebSearchTool20260209.builder().build())
          .addUserMessage("What's the latest on the Mars rover?")
          .build();

      Message response = client.messages().create(params);
      IO.println(response.content());
  }
  ```

  ```php PHP
  $client = new Client();

  $message = $client->messages->create(
      model: 'claude-opus-5-5',
      maxTokens: 1024,
      tools: [
          ['type' => 'web_search_20260209', 'name' => 'web_search'],
      ],
      messages: [
          ['role' => 'user', 'content' => "What's the latest on the Mars rover?"],
      ],
  );

  echo $message;
  ```

  ```ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5-5",
    max_tokens: 1024,
    tools: [{ type: "web_search_20260209", name: "web_search" }],
    messages: [{ role: "user", content: "What's the latest on the Mars rover?" }]
  )
  puts message.content
  ```
</CodeGroup>

Claude runs the search on Anthropic's infrastructure and returns the cited results in the same response. To have Claude call a function that you define, pass a tool with an `input_schema`, then execute the call when Claude returns a `tool_use` block. [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#how-tool-use-works) shows that round trip end to end. Learn more about [defining tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) and [handling tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls).

## How tool use works

Tools differ primarily by where the code executes. **Client tools** (including user-defined tools and tools with Anthropic-defined schemas, such as `bash` and `text_editor`) run in your application. Claude responds with `stop_reason: "tool_use"` and one or more `tool_use` blocks. Your code executes the operation and sends back a `tool_result`. **Server tools** (such as `web_search`, `web_fetch`, `code_execution`, and `tool_search`) run on Anthropic's infrastructure: you see the results directly without handling execution, unless Claude calls the tool in the same group of parallel tool calls as one of your client tools (see [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons#tool-use)).

Here's that round trip in full for a client tool. The first request defines a `get_weather` tool, and Claude answers the question by calling it: the response carries a `tool_use` block, your code runs the lookup, and a second request sends the result back in a `tool_result` block so Claude can reply with the answer.

<CodeGroup>
  ```bash cURL
  # Claude replies with a tool_use block naming the tool and its arguments.
  TOOLS='[
    {
      "name": "get_weather",
      "description": "Get the current weather for a given location.",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "City and state, e.g. San Francisco, CA"}
        },
        "required": ["location"]
      }
    }
  ]'
  USER_MSG="What's the weather in San Francisco?"
  RESPONSE=$(curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "$(jq -n --argjson tools "$TOOLS" --arg msg "$USER_MSG" '{
      model: "claude-opus-5-5",
      max_tokens: 1024,
      tools: $tools,
      # Ask for at most one tool call per turn.
      tool_choice: {type: "auto", disable_parallel_tool_use: true},
      messages: [{role: "user", content: $msg}]
    }')")
  TOOL_USE=$(echo "$RESPONSE" | jq '.content[] | select(.type == "tool_use")')
  echo "Claude called $(echo "$TOOL_USE" | jq -r '.name') with $(echo "$TOOL_USE" | jq -c '.input')"

  # Run the tool, then send the result back in a tool_result block.
  # Claude uses the result to answer the original question.
  WEATHER="15 degrees Celsius, partly cloudy"
  curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "$(jq -n \
      --argjson tools "$TOOLS" \
      --arg msg "$USER_MSG" \
      --argjson assistant "$(echo "$RESPONSE" | jq '.content')" \
      --arg tool_use_id "$(echo "$TOOL_USE" | jq -r '.id')" \
      --arg weather "$WEATHER" \
      '{
        model: "claude-opus-5-5",
        max_tokens: 1024,
        tools: $tools,
        tool_choice: {type: "auto", disable_parallel_tool_use: true},
        messages: [
          {role: "user", content: $msg},
          {role: "assistant", content: $assistant},
          {role: "user", content: [
            {type: "tool_result", tool_use_id: $tool_use_id, content: $weather}
          ]}
        ]
      }')"
  ```

  ```bash CLI
  # ant reads the request body as YAML on stdin; jq carries the conversation
  # state into the second request.
  USER_MSG="What's the weather in San Francisco?"
  MESSAGES=$(jq -n --arg msg "$USER_MSG" '[{role: "user", content: $msg}]')
  call_api() {
    {
      cat <<'YAML'
  model: claude-opus-5-5
  max_tokens: 1024
  # Ask for at most one tool call per turn.
  tool_choice: {type: auto, disable_parallel_tool_use: true}
  tools:
    - name: get_weather
      description: Get the current weather for a given location.
      input_schema:
        type: object
        properties:
          location: {type: string, description: "City and state, e.g. San Francisco, CA"}
        required: [location]
  YAML
      printf 'messages: %s\n' "$MESSAGES"
    } | ant messages create --format json
  }

  # Claude replies with a tool_use block naming the tool and its arguments.
  RESPONSE=$(call_api)
  TOOL_USE=$(jq '.content[] | select(.type == "tool_use")' <<<"$RESPONSE")
  echo "Claude called $(jq -r '.name' <<<"$TOOL_USE") with $(jq -c '.input' <<<"$TOOL_USE")"

  # Run the tool, then send the result back in a tool_result block.
  WEATHER="15 degrees Celsius, partly cloudy"
  MESSAGES=$(jq \
    --argjson assistant "$(jq '.content' <<<"$RESPONSE")" \
    --arg tool_use_id "$(jq -r '.id' <<<"$TOOL_USE")" \
    --arg weather "$WEATHER" \
    '. + [
      {role: "assistant", content: $assistant},
      {role: "user", content: [
        {type: "tool_result", tool_use_id: $tool_use_id, content: $weather}
      ]}
    ]' <<<"$MESSAGES")

  # Claude uses the result to answer the original question.
  call_api
  ```

  ```python Python
  client = anthropic.Anthropic()

  tools = [
      {
          "name": "get_weather",
          "description": "Get the current weather for a given location.",
          "input_schema": {
              "type": "object",
              "properties": {
                  "location": {
                      "type": "string",
                      "description": "City and state, e.g. San Francisco, CA",
                  }
              },
              "required": ["location"],
          },
      }
  ]
  messages = [{"role": "user", "content": "What's the weather in San Francisco?"}]

  # Claude replies with a tool_use block naming the tool and its arguments.
  response = client.messages.create(
      model="claude-opus-5-5",
      max_tokens=1024,
      tools=tools,
      # Ask for at most one tool call per turn.
      tool_choice={"type": "auto", "disable_parallel_tool_use": True},
      messages=messages,
  )
  tool_use = next(block for block in response.content if block.type == "tool_use")
  print(f"Claude called {tool_use.name} with {json.dumps(tool_use.input)}")

  # Run the tool, then send the result back in a tool_result block.
  weather = "15 degrees Celsius, partly cloudy"  # your weather lookup goes here
  messages += [
      {"role": "assistant", "content": response.content},
      {
          "role": "user",
          "content": [
              {"type": "tool_result", "tool_use_id": tool_use.id, "content": weather}
          ],
      },
  ]
  followup = client.messages.create(
      model="claude-opus-5-5",
      max_tokens=1024,
      tools=tools,
      tool_choice={"type": "auto", "disable_parallel_tool_use": True},
      messages=messages,
  )

  # Claude uses the result to answer the original question.
  final_text = next(block for block in followup.content if block.type == "text")
  print(final_text.text)
  ```

  ```typescript TypeScript
  const client = new Anthropic();

  const tools: Anthropic.Tool[] = [
    {
      name: "get_weather",
      description: "Get the current weather for a given location.",
      input_schema: {
        type: "object",
        properties: {
          location: { type: "string", description: "City and state, e.g. San Francisco, CA" }
        },
        required: ["location"]
      }
    }
  ];
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: "What's the weather in San Francisco?" }
  ];

  // Claude replies with a tool_use block naming the tool and its arguments.
  const response = await client.messages.create({
    model: "claude-opus-5-5",
    max_tokens: 1024,
    tools,
    // Ask for at most one tool call per turn.
    tool_choice: { type: "auto", disable_parallel_tool_use: true },
    messages
  });
  const toolUse = response.content.find(
    (block): block is Anthropic.ToolUseBlock => block.type === "tool_use"
  )!;
  console.log(`Claude called ${toolUse.name} with ${JSON.stringify(toolUse.input)}`);

  // Run the tool, then send the result back in a tool_result block.
  const weather = "15 degrees Celsius, partly cloudy"; // your weather lookup goes here
  messages.push(
    { role: "assistant", content: response.content },
    {
      role: "user",
      content: [{ type: "tool_result", tool_use_id: toolUse.id, content: weather }]
    }
  );
  const followup = await client.messages.create({
    model: "claude-opus-5-5",
    max_tokens: 1024,
    tools,
    tool_choice: { type: "auto", disable_parallel_tool_use: true },
    messages
  });

  // Claude uses the result to answer the original question.
  const finalText = followup.content.find(
    (block): block is Anthropic.TextBlock => block.type === "text"
  )!;
  console.log(finalText.text);
  ```

  ```csharp C#
  AnthropicClient client = new();

  List<ToolUnion> tools =
  [
      new ToolUnion(new Tool()
      {
          Name = "get_weather",
          Description = "Get the current weather for a given location.",
          InputSchema = new InputSchema()
          {
              Properties = new Dictionary<string, JsonElement>
              {
                  ["location"] = JsonSerializer.SerializeToElement(new
                  {
                      type = "string",
                      description = "City and state, e.g. San Francisco, CA",
                  }),
              },
              Required = ["location"],
          },
      }),
  ];

  // Ask for at most one tool call per turn.
  var toolChoice = new ToolChoice(new ToolChoiceAuto { DisableParallelToolUse = true });

  const string userPrompt = "What's the weather in San Francisco?";

  // Claude replies with a tool_use block naming the tool and its arguments.
  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5_5,
      MaxTokens = 1024,
      Tools = tools,
      ToolChoice = toolChoice,
      Messages = [new() { Role = Role.User, Content = userPrompt }],
  });
  ToolUseBlock? toolUse = null;
  foreach (var block in response.Content)
  {
      if (block.TryPickToolUse(out var picked))
      {
          toolUse = picked;
          break;
      }
  }
  Console.WriteLine($"Claude called {toolUse!.Name} with {JsonSerializer.Serialize(toolUse.Input)}");

  // Run the tool, then send the result back in a tool_result block.
  var weather = "15 degrees Celsius, partly cloudy";
  List<ContentBlockParam> toolResults =
  [
      new ContentBlockParam(new ToolResultBlockParam()
      {
          ToolUseID = toolUse.ID,
          Content = weather,
      }),
  ];
  var followup = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5_5,
      MaxTokens = 1024,
      Tools = tools,
      ToolChoice = toolChoice,
      Messages =
      [
          new() { Role = Role.User, Content = userPrompt },
          new() { Role = Role.Assistant, Content = response.Content.Select(block => new ContentBlockParam(block.Json)).ToList() },
          new() { Role = Role.User, Content = new MessageParamContent(toolResults) },
      ],
  });

  // Claude uses the result to answer the original question.
  foreach (var block in followup.Content)
  {
      if (block.TryPickText(out var text))
      {
          Console.WriteLine(text.Text);
      }
  }
  ```

  ```go Go
  client := anthropic.NewClient()
  ctx := context.Background()

  tools := []anthropic.ToolUnionParam{
  	{OfTool: &anthropic.ToolParam{
  		Name:        "get_weather",
  		Description: anthropic.String("Get the current weather for a given location."),
  		InputSchema: anthropic.ToolInputSchemaParam{
  			Properties: map[string]any{
  				"location": map[string]any{
  					"type":        "string",
  					"description": "City and state, e.g. San Francisco, CA",
  				},
  			},
  			Required: []string{"location"},
  		},
  	}},
  }
  // Ask for at most one tool call per turn.
  toolChoice := anthropic.ToolChoiceUnionParam{
  	OfAuto: &anthropic.ToolChoiceAutoParam{DisableParallelToolUse: anthropic.Bool(true)},
  }
  messages := []anthropic.MessageParam{
  	anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather in San Francisco?")),
  }

  // Claude replies with a tool_use block naming the tool and its arguments.
  response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  	Model:      anthropic.ModelClaudeOpus5_5,
  	MaxTokens:  1024,
  	Tools:      tools,
  	ToolChoice: toolChoice,
  	Messages:   messages,
  })
  if err != nil {
  	log.Fatal(err)
  }
  var toolUse anthropic.ContentBlockUnion
  for _, block := range response.Content {
  	if block.Type == "tool_use" {
  		toolUse = block
  		break
  	}
  }
  fmt.Printf("Claude called %s with %s\n", toolUse.Name, string(toolUse.Input))

  // Run the tool, then send the result back in a tool_result block.
  weather := "15 degrees Celsius, partly cloudy"
  var assistantContent []anthropic.ContentBlockParamUnion
  for _, block := range response.Content {
  	assistantContent = append(assistantContent, block.ToParam())
  }
  messages = append(messages,
  	anthropic.NewAssistantMessage(assistantContent...),
  	anthropic.NewUserMessage(anthropic.NewToolResultBlock(toolUse.ID, weather, false)),
  )
  followup, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  	Model:      anthropic.ModelClaudeOpus5_5,
  	MaxTokens:  1024,
  	Tools:      tools,
  	ToolChoice: toolChoice,
  	Messages:   messages,
  })
  if err != nil {
  	log.Fatal(err)
  }

  // Claude uses the result to answer the original question.
  for _, block := range followup.Content {
  	if block.Type == "text" {
  		fmt.Println(block.Text)
  	}
  }
  ```

  ```java Java
  import com.anthropic.core.JsonValue;
  import com.anthropic.models.messages.ContentBlockParam;
  // ...
  import com.anthropic.models.messages.Tool;
  import com.anthropic.models.messages.Tool.InputSchema;
  import com.anthropic.models.messages.ToolChoiceAuto;
  import com.anthropic.models.messages.ToolResultBlockParam;
  import com.anthropic.models.messages.ToolUseBlock;
  // ...

  void main() {
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      Tool weatherTool = Tool.builder()
          .name("get_weather")
          .description("Get the current weather for a given location.")
          .inputSchema(InputSchema.builder()
              .properties(JsonValue.from(Map.of(
                  "location", Map.of(
                      "type", "string",
                      "description", "City and state, e.g. San Francisco, CA"
                  )
              )))
              .required(List.of("location"))
              .build())
          .build();

      // Ask for at most one tool call per turn.
      ToolChoiceAuto toolChoice = ToolChoiceAuto.builder()
          .disableParallelToolUse(true)
          .build();

      String userPrompt = "What's the weather in San Francisco?";

      // Claude replies with a tool_use block naming the tool and its arguments.
      Message response = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5_5)
          .maxTokens(1024L)
          .addTool(weatherTool)
          .toolChoice(toolChoice)
          .addUserMessage(userPrompt)
          .build());
      ToolUseBlock toolUse = response.content().stream()
          .flatMap(block -> block.toolUse().stream())
          .findFirst()
          .orElseThrow();
      IO.println("Claude called " + toolUse.name() + " with " + toolUse._input());

      // Run the tool, then send the result back in a tool_result block.
      String weather = "15 degrees Celsius, partly cloudy";
      Message followup = client.messages().create(MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5_5)
          .maxTokens(1024L)
          .addTool(weatherTool)
          .toolChoice(toolChoice)
          .addUserMessage(userPrompt)
          .addMessage(response)
          .addUserMessageOfBlockParams(List.of(ContentBlockParam.ofToolResult(
              ToolResultBlockParam.builder()
                  .toolUseId(toolUse.id())
                  .content(weather)
                  .build())))
          .build());

      // Claude uses the result to answer the original question.
      followup.content().stream()
          .flatMap(block -> block.text().stream())
          .forEach(textBlock -> IO.println(textBlock.text()));
  }
  ```

  ```php PHP
  use Anthropic\Messages\ToolChoiceAuto;

  $client = new Client();

  $tools = [
      [
          'name' => 'get_weather',
          'description' => 'Get the current weather for a given location.',
          'input_schema' => [
              'type' => 'object',
              'properties' => [
                  'location' => [
                      'type' => 'string',
                      'description' => 'City and state, e.g. San Francisco, CA',
                  ],
              ],
              'required' => ['location'],
          ],
      ],
  ];
  $userMessage = ['role' => 'user', 'content' => "What's the weather in San Francisco?"];

  // Ask for at most one tool call per turn.
  $toolChoice = ToolChoiceAuto::with(disableParallelToolUse: true);

  // Claude replies with a tool_use block naming the tool and its arguments.
  $response = $client->messages->create(
      model: 'claude-opus-5-5',
      maxTokens: 1024,
      tools: $tools,
      toolChoice: $toolChoice,
      messages: [$userMessage],
  );
  $toolUse = null;
  foreach ($response->content as $block) {
      if ($block->type === 'tool_use') {
          $toolUse = $block;
          break;
      }
  }
  printf("Claude called %s with %s\n", $toolUse->name, json_encode($toolUse->input));

  // Run the tool, then send the result back in a tool_result block.
  $weather = '15 degrees Celsius, partly cloudy';
  $followup = $client->messages->create(
      model: 'claude-opus-5-5',
      maxTokens: 1024,
      tools: $tools,
      toolChoice: $toolChoice,
      messages: [
          $userMessage,
          ['role' => 'assistant', 'content' => $response->content],
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'tool_result',
                      'tool_use_id' => $toolUse->id,
                      'content' => $weather,
                  ],
              ],
          ],
      ],
  );

  // Claude uses the result to answer the original question.
  foreach ($followup->content as $block) {
      if ($block->type === 'text') {
          echo $block->text, "\n";
      }
  }
  ```

  ```ruby Ruby
  client = Anthropic::Client.new

  tools = [
    {
      name: "get_weather",
      description: "Get the current weather for a given location.",
      input_schema: {
        type: "object",
        properties: {
          location: {type: "string", description: "City and state, e.g. San Francisco, CA"}
        },
        required: ["location"]
      }
    }
  ]
  messages = [{role: "user", content: "What's the weather in San Francisco?"}]

  # Claude replies with a tool_use block naming the tool and its arguments.
  response = client.messages.create(
    model: "claude-opus-5-5",
    max_tokens: 1024,
    tools: tools,
    # Ask for at most one tool call per turn.
    tool_choice: {type: "auto", disable_parallel_tool_use: true},
    messages: messages
  )
  tool_use = response.content.find { |block| block.type == :tool_use }
  puts "Claude called #{tool_use.name} with #{JSON.generate(tool_use.input)}"

  # Run the tool, then send the result back in a tool_result block.
  weather = "15 degrees Celsius, partly cloudy"
  messages += [
    {role: "assistant", content: response.content},
    {
      role: "user",
      content: [
        {type: "tool_result", tool_use_id: tool_use.id, content: weather}
      ]
    }
  ]
  followup = client.messages.create(
    model: "claude-opus-5-5",
    max_tokens: 1024,
    tools: tools,
    tool_choice: {type: "auto", disable_parallel_tool_use: true},
    messages: messages
  )

  # Claude uses the result to answer the original question.
  final_text = followup.content.find { |block| block.type == :text }
  puts final_text.text
  ```
</CodeGroup>

```text Output wrap
Claude called get_weather with {"location": "San Francisco, CA"}
The current weather in San Francisco is 15 degrees Celsius with partly cloudy skies.
```

[Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) covers each step in detail, including result formatting and error signaling; [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) covers responses that call several tools at once. To skip writing this round trip yourself, use [Tool Runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner): the SDK executes your tools and sends the results back automatically.

For the full conceptual model including the agentic loop and when to choose each approach, see [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works).

To connect to Model Context Protocol (MCP) servers, see the [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector). To build your own MCP client, see the Model Context Protocol guide to [building an MCP client](https://modelcontextprotocol.io/docs/develop/build-client).

## When Claude uses tools

With the default `tool_choice` of `{"type": "auto"}`, Claude determines on each turn whether to call a tool or respond directly. It calls a tool when the request maps to that tool's described capability and the answer isn't already in context. It responds directly for stable knowledge, creative tasks, and conversational turns.

This boundary is steerable through your system prompt. If Claude isn't calling tools when you expect, a light instruction such as `"Use the tools to investigate before responding."` increases tool use. A stronger form such as `"Always call a tool first before responding."` pushes further. Conversely, `"Use your judgment about whether to call a tool or respond directly."` keeps triggering behavior conservative.

To require a tool call rather than rely on prompting, set [`tool_choice`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#forcing-tool-use).

<Tip>
  **Guarantee schema conformance with strict tool use**

  Add `strict: true` to your custom tool definitions to ensure Claude's tool calls always match your schema exactly. See [Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use).
</Tip>

Each server tool's page describes its own trigger boundary in more detail.

<Accordion title="When required parameters are missing">
  If the user's prompt doesn't include enough information to fill all the required parameters for a tool, Claude Opus is much more likely to recognize that a parameter is missing and ask for it. Claude Sonnet might ask, especially when prompted to think before outputting a tool request. But it might also infer a reasonable value.

  For example, given a `get_weather` tool that requires a `location` parameter, if you ask Claude "What's the weather?" without specifying a location, Claude (particularly Claude Sonnet) might guess values you didn't supply:

  ```json JSON
  {
    "type": "tool_use",
    "id": "toolu_01A09q90qw90lq917835lq9",
    "name": "get_weather",
    "input": { "location": "New York, NY", "unit": "fahrenheit" }
  }
  ```

  This behavior is not guaranteed, especially for more ambiguous prompts and for less capable models.
</Accordion>

## Choose a tool

For `type` strings, versions, and beta headers, see [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference).

### Your own tools

For tools you define, you write the schema and your application executes each call.

<CardGroup cols={2}>
  <Card title="Define tools" icon="hammer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools">
    Specify tool schemas, write descriptions, and control when Claude calls your tools.
  </Card>

  <Card title="Handle tool calls" icon="arrows-left-right" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls">
    Parse `tool_use` blocks, format `tool_result` responses, and handle errors.
  </Card>
</CardGroup>

### Anthropic-schema client tools

Anthropic publishes the schema and trains Claude on it. Your application still executes each call and returns the `tool_result`.

<CardGroup cols={2}>
  <Card title="Memory tool" icon="brain" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool">
    Store and retrieve information across conversations in files you control.
  </Card>

  <Card title="Bash tool" icon="terminal" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool">
    Run shell commands in a persistent session that maintains state.
  </Card>

  <Card title="Text editor tool" icon="edit" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool">
    View and modify text files to debug, fix, and improve code.
  </Card>

  <Card title="Computer use tool" icon="computer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool">
    Take screenshots and control the mouse and keyboard in a desktop environment.
  </Card>

  <Card title="Browser use tool" icon="browser" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool">
    Navigate, read, and interact with webpages in your own browser environment.
  </Card>
</CardGroup>

### Server tools

Server tools run on Anthropic's infrastructure, with no handler code in your application. See [Server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools) for the mechanics they share.

<CardGroup cols={2}>
  <Card title="Web search tool" icon="magnifying-glass" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool">
    Search the web for information beyond the knowledge cutoff, with cited sources.
  </Card>

  <Card title="Web fetch tool" icon="download" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool">
    Retrieve the full content of specified web pages and PDF documents.
  </Card>

  <Card title="Code execution tool" icon="code" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool">
    Run Python and bash code in a sandboxed container to analyze data and generate files.
  </Card>

  <Card title="Advisor tool" icon="lightbulb" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool">
    Let a faster executor model consult a higher-intelligence advisor model mid-generation.
  </Card>

  <Card title="Tool search tool" icon="library" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool">
    Work with thousands of tools by discovering and loading them on demand.
  </Card>

  <Card title="MCP connector" icon="link" href="https://platform.claude.com/docs/en/agents-and-tools/mcp-connector">
    Connect to remote MCP servers from the Messages API without a separate MCP client.
  </Card>
</CardGroup>

<Note>
  [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) provides a built-in toolset that Claude uses autonomously within a session. For that toolset and the Managed Agents way to add custom tools, see its [Tools](https://platform.claude.com/docs/en/managed-agents/tools) page.
</Note>

## Pricing

Tool use requests are priced based on:

1. The total number of input tokens sent to the model (including in the `tools` parameter)
2. The number of output tokens generated
3. For server-side tools, additional usage-based pricing (for example, web search charges per search performed)

Client-side tools are priced the same as any other Claude API request, although server-side tools can incur additional charges based on their specific usage.

The additional tokens from tool use come from:

* The `tools` parameter in API requests (tool names, descriptions, and schemas)
* `tool_use` content blocks in API requests and responses
* `tool_result` content blocks in API requests

When you use `tools`, the API also automatically includes a special system prompt for the model that enables tool use. The number of tool use tokens required for each model is listed in the following table (excluding the additional tokens listed earlier). Note that the table assumes at least 1 tool is provided. If no `tools` are provided, then a tool choice of `none` uses 0 additional system prompt tokens.

| Model                                                                                                                                | Tool use system prompt tokens: auto, none | Tool use system prompt tokens: any, tool |
| :----------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------- | :--------------------------------------- |
| Claude Opus 5.5                                                                                                                      | 286 tokens                                |                                          |
| Claude Opus 5                                                                                                                        | 286 tokens                                | 406 tokens                               |
| Claude Opus 4.8                                                                                                                      | 290 tokens                                | 410 tokens                               |
| Claude Opus 4.7                                                                                                                      | 675 tokens                                | 804 tokens                               |
| Claude Opus 4.6                                                                                                                      | 497 tokens                                | 589 tokens                               |
| Claude Opus 4.5                                                                                                                      | 496 tokens                                | 588 tokens                               |
| Claude Opus 4.1 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)) | 313 tokens                                | 315 tokens                               |
| Claude Opus 4 ([retired, except on Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))               | 313 tokens                                | 315 tokens                               |
| Claude Sonnet 5.5                                                                                                                    | 286 tokens                                |                                          |
| Claude Sonnet 5                                                                                                                      | 354 tokens                                | 474 tokens                               |
| Claude Sonnet 4.6                                                                                                                    | 497 tokens                                | 589 tokens                               |
| Claude Sonnet 4.5                                                                                                                    | 496 tokens                                | 588 tokens                               |
| Claude Sonnet 4 ([retired, except on Bedrock and Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations)) | 313 tokens                                | 315 tokens                               |
| Claude Haiku 5.5                                                                                                                     | 286 tokens                                | 406 tokens                               |
| Claude Haiku 4.5                                                                                                                     | 496 tokens                                | 588 tokens                               |
| Claude Haiku 3.5 ([retired, except on Google Cloud](https://platform.claude.com/docs/en/about-claude/model-deprecations))            | 264 tokens                                | 355 tokens                               |

* **auto, none:** The count when tool\_choice is auto or none.
* **any, tool:** The count when tool\_choice is any or tool.
* **Retired:** May still be available on other cloud platforms. See [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) for more.

These token counts are added to your normal input and output tokens to calculate the total cost of a request.

See the [Models overview](https://platform.claude.com/docs/en/models/overview#latest-models-comparison) table for current per-model prices.

When you send a tool use prompt, like any other API request, the response includes both input and output token counts in the reported `usage` metrics.

Some server tools add usage-based charges on top of tokens: see [Web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool#usage-and-pricing) and [Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#usage-and-pricing) for their rates.

## Next steps

<CardGroup cols={3}>
  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works" title="How tool use works" icon="compass">
    Understand the tool use loop, where tools execute, and when to use tools instead of prose.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent" title="Tutorial: Build a tool-using agent" icon="graduation-cap">
    A guided walkthrough from a single tool call to a production-ready agentic loop.
  </Card>

  <Card href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference" title="Tool reference" icon="book">
    Directory of Anthropic-provided tools and reference for optional tool definition properties.
  </Card>
</CardGroup>
