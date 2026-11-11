# Cursor Token Rate

> Source: https://cursor.com/help/models-and-usage/token-rate — mirrored 2026-11-11.

Teams and Enterprise plan customers pay a Cursor Token Rate of $0.25 per million tokens on eligible third-party model requests. This includes when you pick a third-party model directly and when Cursor Router (Balance or Intelligence) routes to a third-party model.

Cost mode requests are exempt. First-party Cursor models, including Grok and Composer, are exempt. Individual plans don't pay the Cursor Token Rate.

Third-party models are also exempt when their cache-read price is strictly below $0.10 per million tokens across every pricing tier. This exemption also applies when you use your own API key.

On The X Subscription, the rate is charged on top of the model's API price and paid from the team's prepaid credit. On legacy Teams plans, it applies to included Other Models usage, on-demand usage, and BYOK usage alike.

## What does the Cursor Token Rate cover?

- Search infrastructure
- Custom model execution and routing
- Processing and infrastructure costs

## How is the Cursor Token Rate calculated?

For eligible third-party model requests, the rate applies to input tokens, output tokens, and cached tokens. The same requests made with your own API key include the rate, in addition to whatever you pay your API provider directly. Exempt models stay exempt when you use your own key.

## How do I avoid the Cursor Token Rate?

Use a first-party model, including Grok or Composer, or a third-party model whose [cache-read price is strictly below $0.10 per million tokens across every pricing tier](https://cursor.com/docs/models-and-pricing.md#cursor-token-rate).

## Related

- [API keys](https://cursor.com/help/models-and-usage/api-keys.md)
- [Available models](https://cursor.com/help/models-and-usage/available-models.md)
- [Models & Pricing](https://cursor.com/docs/models-and-pricing.md#cursor-token-rate)
