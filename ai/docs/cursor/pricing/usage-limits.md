# Usage and limits

> Source: https://cursor.com/help/models-and-usage/usage-limits — mirrored 2026-11-11.

How much you can use depends on whether you're on [The X Subscription](https://cursor.com/help/the-x-subscription/overview.md) or a [legacy Cursor plan](https://cursor.com/docs/account/pricing/legacy-cursor-plans.md).

**The X Subscription (Free, Plus, Premium, Super, Ultra, and Teams seats):** every paid plan includes one weekly pool of usage for Cursor models (Grok 4.7, Grok 4.6, Grok 4.5, and Composer 2.5), shared across Cursor, Grok Bot, and the Grok apps. Third-party models aren't included. On Premium and above they're billed at API list price from your prepaid credit.

**Legacy Cursor plans (Hobby, Start, Pro, Pro+, Ultra, and Teams Standard and Premium seats):** included usage is split into two monthly pools:

- **Cursor Models**: Grok 4.7, Grok 4.6, Grok 4.5, and Composer 2.5
- **Other Models**: Third-party models, charged at model provider prices

Pro, Pro+, Ultra, and Teams include both pools. Start covers the Cursor Models pool only. See [Cursor Start](https://cursor.com/help/account-and-billing/cursor-start.md) for India plan details.

On either kind of plan, your model selection affects how quickly your included usage is consumed.

Current plans don't include Max Mode. On legacy request-based plans, [Max Mode](https://cursor.com/help/ai-features/max-mode.md) is billed at the model's API rate plus 20%.

## How do I check my usage?

- **The X Subscription:** open **Usage** at [grok.com/dashboard](https://grok.com/dashboard). It shows how much of your weekly pool you've used, the next reset date, and your prepaid credit. Your editor settings show the same remaining usage.
- **Legacy Cursor plans:** go to the [Spending](https://cursor.com/dashboard/spending) tab in your dashboard. It shows real-time usage for both pools, remaining allowance, and any on-demand charges.

## What happens when I hit my usage limit?

You'll see a notification in the editor.

- **The X Subscription:** keep working from your prepaid credit, wait for your weekly pool to reset, or upgrade to a higher plan. See [Usage-based charges](https://cursor.com/help/account-and-billing/overages.md) for how top-ups work.
- **Legacy Cursor plans:** enable on-demand usage (pay-as-you-go) or upgrade to a higher plan.

## When does my usage reset?

- **The X Subscription:** your included pool refreshes weekly. The next reset date is shown under **Usage** at [grok.com/dashboard](https://grok.com/dashboard). Prepaid credit doesn't reset with your weekly pool; each top-up stays available until used or until it expires (currently 365 days after purchase).
- **Legacy Cursor plans:** usage resets monthly with your billing cycle. The reset date is shown on the [Spending](https://cursor.com/dashboard/spending) tab. For teams, all members' usage resets at the same time based on the team billing cycle.

Unused included usage does not roll over on either kind of plan.

## How do I get more usage?

- **Use Cursor models**: Grok 4.7, Grok 4.6, Grok 4.5, and Composer 2.5 draw from your included pool
- **Add prepaid credit** (The X Subscription) or **enable on-demand usage** (legacy plans): Pay for additional requests at the same API rates
- **[Upgrade your plan](https://cursor.com/help/account-and-billing/pricing.md#how-do-i-change-plans-on-the-x-subscription)**: Higher-tier plans include more usage

## How does Cursor Router interact with my plan's usage and limits?

Cost mode (classic Auto) bills as a Cursor-model request and draws from your included pool whatever model serves it. On Teams and Enterprise with Cursor Router on, Balance and Intelligence bill at the routed model's list price: a route to a Cursor model draws from your included pool, and a route to a third-party model bills as third-party usage, from prepaid credit on The X Subscription or from the Other Models pool on a legacy plan. Individual plans have Cost mode only.

- **Composer 2.5** requests carry no [Cursor Token Rate](https://cursor.com/help/models-and-usage/token-rate.md) on any plan
- Eligible third-party routes from Balance or Intelligence also incur the Cursor Token Rate on Teams and Enterprise. Cost mode requests are exempt. Third-party models are also exempt when their [cache-read price is strictly below $0.10 per million tokens across every pricing tier](https://cursor.com/docs/models-and-pricing.md#cursor-token-rate)

Check your usage dashboard for request-level cost details. See [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md) for mode details.

## Can Auto usage bill as third-party usage?

In Cost mode, no: the request bills as a Cursor-model request from your included pool. In Balance or Intelligence (Teams and Enterprise with Cursor Router on), a third-party route bills as third-party usage at that model's list price.

Subagents can also run a named third-party model while the picker still shows Auto, Grok, or Composer. Those requests bill as third-party usage at that model's list price.

See [parent model and usage pools](https://cursor.com/docs/subagents.md#parent-model-and-usage-pools) and [Auto modes](https://cursor.com/docs/models-and-pricing.md#auto-modes).

## Do requests made with my own API key count toward my usage?

On individual plans, no. Your provider bills you directly for the model cost, and those requests don't draw from your included usage or prepaid credit.

On Teams and Enterprise plans, requests made with your own key still carry the [Cursor Token Rate](https://cursor.com/help/models-and-usage/token-rate.md) of $0.25 per million tokens when the model includes it. Third-party models are exempt, including when you use your own key, if their [cache-read price is strictly below $0.10 per million tokens across every pricing tier](https://cursor.com/docs/models-and-pricing.md#cursor-token-rate). On The X Subscription that charge comes out of the team's prepaid credit. On a legacy Teams plan it appears under **Other Models** and draws from that allowance; when the allowance runs out, it's billed as on-demand usage if on-demand usage is enabled, and requests stop until the next billing cycle if it's turned off.

See [Bring your own API key](https://cursor.com/help/models-and-usage/api-keys.md#does-using-my-own-api-key-count-against-my-included-usage) for details.

## Related

- [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md)
- [Pricing and plans](https://cursor.com/help/account-and-billing/pricing.md)
- [Usage-based charges](https://cursor.com/help/account-and-billing/overages.md)
- [Available models](https://cursor.com/help/models-and-usage/available-models.md)
- [API keys](https://cursor.com/help/models-and-usage/api-keys.md)
- [Pricing reference](https://cursor.com/docs/models-and-pricing.md)
- [Model pricing](https://cursor.com/docs/models-and-pricing.md#model-pricing)
- [Legacy Cursor plans](https://cursor.com/docs/account/pricing/legacy-cursor-plans.md)
- [Subagents](https://cursor.com/docs/subagents.md#parent-model-and-usage-pools)
