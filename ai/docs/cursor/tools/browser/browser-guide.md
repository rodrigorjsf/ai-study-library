# Browser

Agent can control a web browser to test applications, visually edit layouts and styles, audit accessibility, convert designs into code, and more. With full access to console logs and network traffic, Agent can debug issues and automate comprehensive testing workflows.

> For enterprise customers, browser controls are governed by MCP allowlist or denylist.

## Native integration

Agent displays browser actions like screenshots and actions in the chat, as well as the browser window itself either in a separate window or an inline pane.

The browser tools are optimized for efficiency and reduced token usage:

- **Efficient log handling**
- **Visual feedback with images**
- **Smart prompting**
- **Development server awareness**

You can use Browser without installing or configuring any external tools.

## Browser capabilities

Agent has access to the following browser tools:

### Navigate

Visit URLs and browse web pages. Agent can navigate anywhere on the web by visiting URLs, following links, going back and forward in history, and refreshing pages.

### Click

Interact with buttons, links, and form elements. Agent can identify and interact with page elements, performing click, double-click, right-click, and hover actions on any visible element.

### Type

Enter text into input fields and forms. Agent can fill out forms, submit data, and interact with form fields, search boxes, and text areas.

### Scroll

Navigate through long pages and content. Agent can scroll to reveal additional content, find specific elements, and explore lengthy documents.

### Screenshot

Capture visual representations of web pages. Screenshots help Agent understand page layout, verify visual elements, and provide you with confirmation of browser actions.

### Console Output

Read browser console messages, errors, and logs. Agent can monitor JavaScript errors, debugging output, and network warnings to troubleshoot issues and verify page behavior.

### Network Traffic

Monitor HTTP requests and responses made by the page. Agent can track API calls, analyze request payloads, check response status codes, and diagnose network-related issues.

## Design sidebar

The browser includes a design sidebar for modifying your site directly in Cursor. Design and code simultaneously with real-time visual adjustments.

### Visual editing capabilities

The sidebar provides powerful visual editing controls:

- **Position and layout**
- **Dimensions**
- **Colors**
- **Appearance**
- **Theme testing**

### Applying changes

When your visual adjustments match your vision, click the apply button to trigger an agent that updates your codebase. The agent translates your visual changes into the appropriate code modifications.

You can also select multiple elements across your site and describe changes in text. Agents kick off in parallel, and your changes appear live on the page after hot-reload.

## Session persistence

Browser state persists between Agent sessions based on your workspace. This means:

- **Cookies** — Preserved across sessions
- **Local Storage** (`localStorage`, `sessionStorage`, `IndexedDB`) — Preserved across sessions

The browser context is isolated per workspace, ensuring that different projects maintain separate storage and cookie states.

## Use cases

### Web development workflow

Agent can automate end-to-end development workflows: navigate to your local dev server, interact with UI elements, inspect console errors, and suggest code fixes — all in one loop.

### Accessibility improvements

Agent can audit and improve web accessibility to meet WCAG compliance standards.

### Automated testing

Agent can execute comprehensive test suites and capture screenshots for visual regression testing.

### Design to code

Agent can convert designs into working code with responsive layouts.

### Adjusting UI design from screenshots

Agent can refine existing interfaces by identifying visual discrepancies and updating component styles.

## Security

Browser runs as a secure web view and is controlled using an MCP server running as an extension. Multiple layers protect you from unauthorized access and malicious actions. Cursor's Browser integrations have been reviewed by multiple external security auditors.

### Authentication and isolation

The browser implements several security measures:

- **Token authentication**
- **Tab isolation**
- **Session-based security**

### Tool approval

Browser tools require your approval by default. Review each action before Agent executes it. This prevents unexpected navigation, data submission, or script execution.

You can configure approval settings in Agent Settings. Available modes:

| Mode | Description |
|---|---|
| Manual approval | Review and approve each browser action individually (recommended) |
| Allow-listed actions | Actions matching your allow list run automatically; others require approval |
| Auto-run | All browser actions execute immediately without approval (use with caution) |

### Allow and block lists

Configure via **Cursor Settings > Auto-Run**:

- **Allow list** — Domains/actions approved to run automatically
- **Block list** — Domains/actions that are always blocked (security guardrails)

> ⚠️ The allow/block list system provides best-effort protection. AI behavior can be unpredictable due to prompt injection and other issues. Review auto-approved actions regularly.
>
> ⚠️ **Never use auto-run mode with untrusted code or unfamiliar websites.** Agent could execute malicious scripts or submit sensitive data without your knowledge.

## Browser context

The browser opens as a pane within Cursor, giving Agent full control through MCP tools.

## Recommended models

We recommend using Sonnet 4.5, GPT-5, and Auto for the best performance.

## Enterprise usage

For enterprise customers, browser functionality is managed through toggling availability under MCP controls. Admins have granular controls over each MCP server, as well as over browser access.

### Enabling browser for enterprise

To enable browser capabilities for your enterprise team:

1. Go to **Settings Dashboard > MCP Configuration**
2. Toggle the browser MCP server on

Once configured, users in your organization will have access to browser tools based on your MCP allowlist or denylist settings.

### Origin allowlist

Enterprise administrators can configure an origin allowlist that restricts which sites the agent can automatically navigate to and where MCP tools can run. This provides granular control over browser access for security and compliance.

> The Browser Origin Allowlist feature must be enabled for your organization before it appears in your dashboard. Contact your Cursor account team to request access.

#### Configuration

To configure the origin allowlist:

1. Go to **Admin Dashboard**
2. Enable **Browser Automation Features** (v2.0+)
3. Enable **Browser Origin Allowlist** (v2.1+)
4. Click **Add Origin** to add allowed origins

> Leave the allowlist empty to allow all origins. Each origin should be added separately using the Add Origin button.

#### Behavior

When an origin allowlist is configured:

| Scenario | Behavior |
|---|---|
| Automatic navigation (`browser_navigate`) | Restricted to allowlisted origins |
| MCP tool execution | Only runs on allowlisted origins |
| Manual navigation | Not restricted (user-initiated) |
| Tool restrictions | MCP tools blocked on non-allowlisted origins |

#### Edge cases

> ⚠️ The origin allowlist provides best-effort protection. Be aware of these behaviors:
>
> - **Link navigation** — Following links may lead to non-allowlisted origins
> - **Redirects** — Server-side redirects may bypass origin checks
> - **JavaScript navigation** (`window.location`) — May bypass allowlist in some cases
>
> The origin allowlist restricts automatic agent navigation but cannot prevent all navigation paths. Review your allowlist regularly and consider the security implications of allowing access to domains that may redirect or link to external sites.
