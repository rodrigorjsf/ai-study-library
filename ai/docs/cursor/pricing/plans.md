# Pricing and plans

> Source: https://cursor.com/help/account-and-billing/pricing — mirrored 2026-11-11.

Cursor is part of [The X Subscription](https://cursor.com/help/the-x-subscription/overview.md), one subscription for Grok, Cursor, and X. New customers choose a plan on The X Subscription. If you subscribed to Cursor before it launched, you're on a legacy Cursor plan, and it keeps working as it is.

## What plans are available?

| Plan    | Price                          | Included usage          |
| ------- | ------------------------------ | ----------------------- |
| Free    | $0                             | Limited                 |
| Plus    | $8/mo                          | Base                    |
| Premium | $30/mo                         | 4x Plus                 |
| Super   | $100/mo                        | 15x Plus                |
| Ultra   | $200/mo                        | 50x Plus                |
| Teams   | $30, $100, or $200 per seat/mo | Matches the seat's tier |

Annual billing is $80/yr for Plus, $300/yr for Premium, $1,000/yr for Super, and $2,000/yr for Ultra. Prices exclude tax.

Every paid plan includes a weekly pool of usage for Cursor models (Grok 4.7, Grok 4.6, Grok 4.5, and Composer 2.5), shared across Cursor and Grok. Plus runs those models at fixed settings (Fast off, medium effort) without Auto, Cloud Agents, Automations, Bugbot, Origin, or third-party models. Premium and above add all of those, with third-party models at API list price paid from prepaid credit. See [Models & Pricing](https://cursor.com/docs/models-and-pricing.md) for what each tier includes and [cursor.com/pricing](https://cursor.com/pricing) for the full feature comparison, including Grok and X benefits.

**Enterprise** plans include pooled usage across Grok and Cursor, SCIM provisioning, audit logs, advanced admin controls, and invoice billing. [Contact sales](https://cursor.com/contact-sales?source=docs-help-pricing) to get started.

## What are the legacy Cursor plans?

Legacy Cursor plans are the plans Cursor sold before The X Subscription. They aren't available to new customers, but existing subscribers keep them until they switch or cancel.

| Legacy plan        | Price                  | Comparable plan on The X Subscription |
| ------------------ | ---------------------- | ------------------------------------- |
| Hobby              | Free                   | Free                                  |
| Start (India only) | ₹649/mo, tax inclusive | Plus                                  |
| Pro                | $20/mo                 | Premium                               |
| Pro+               | $60/mo                 | Super                                 |
| Ultra              | $200/mo                | Ultra                                 |
| Teams Standard     | $40/user/mo            | Teams, Premium seat                   |
| Teams Premium      | $120/user/mo           | Teams, Super seat                     |

Legacy plans include two monthly usage pools, Cursor Models and Other Models, and use on-demand usage for extra requests. See [Legacy Cursor plans](https://cursor.com/docs/account/pricing/legacy-cursor-plans.md) for the full comparison and [Cursor Start](https://cursor.com/help/account-and-billing/cursor-start.md) for the India plan.

## Do I have to switch to The X Subscription?

No. Switching is optional. Your legacy plan, price, and features continue unless you change or cancel. You can still move between legacy plans, for example from Pro to Pro+, without switching.

If you do switch, your Cursor subscription is cancelled with a prorated refund, you pick a plan on The X Subscription, and the change is permanent. See [What is The X Subscription?](https://cursor.com/help/the-x-subscription/overview.md) for eligibility and what happens to your old plans.

## What is Auto?

**Auto** balances intelligence, cost, and reliability through [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md). Cost mode (classic Auto) bills as a Cursor-model request and draws from your weekly pool whatever model serves it. On Teams and Enterprise with Cursor Router on, Balance and Intelligence bill at the routed model's list price: for example, if your request is routed to Opus 5, you are billed at Opus 5 pricing for that request as third-party usage paid from prepaid credit, plus the [Cursor Token Rate](https://cursor.com/help/models-and-usage/token-rate.md). A Balance or Intelligence route to a third-party model does not add that rate when its [cache-read price is strictly below $0.10 per million tokens across every pricing tier](https://cursor.com/docs/models-and-pricing.md#cursor-token-rate). Cost mode does not add it either. Individual plans have Cost mode only. See [Auto modes](https://cursor.com/docs/models-and-pricing.md#auto-modes) for current rates.

You can switch between Auto and specific models in the model picker. See [available models](https://cursor.com/help/models-and-usage/available-models.md) for details.

## Is Cursor Router available on my plan?

Cursor Router will launch for Teams and Enterprise plans. Enterprise teams start with Cursor Router off; an admin must opt in.

It is available across the Agents window, editor, CLI, Cursor SDK, and the iOS app. See [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md) for how routing and optimization modes work.

## Why is the old Auto mode now called Cost mode?

The old Auto mode was split into 3 new modes: **Cost**, **Balance** and **Intelligence**.

## What's included in the Free plan?

Free gives you access to Cursor's core features with limited usage. You can use Agent, Chat, and Tab completions with Cursor models (Grok and Composer), along with standard X. The legacy Hobby plan works the same way for Cursor.

## How do I change plans on The X Subscription?

1. Go to [grok.com/dashboard/billing](https://grok.com/dashboard/billing)
2. Open the options on the **Current plan** card and choose to change your plan
3. Choose a plan and follow the prompts to confirm

Upgrades apply right away. Downgrades apply at the end of your billing period. See [Managing The X Subscription](https://docs.x.ai/x-subscription/manage) for payment methods, invoices, and cancellation.

## How do I change plans on a legacy Cursor plan?

**To upgrade:**

1. Go to [cursor.com/dashboard/billing](https://cursor.com/dashboard/billing)
2. Find the tile with your current plan and click **Adjust plan**
3. Select the plan you want
4. Complete payment through Stripe checkout

The change takes effect immediately. Any credit for your previous plan is based on its unused included usage, not days remaining. See [Do I get a prorated refund when I upgrade my plan?](https://cursor.com/help/account-and-billing/refunds.md#do-i-get-a-prorated-refund-when-i-upgrade-my-plan)

**To downgrade:**

1. Go to [cursor.com/dashboard/billing](https://cursor.com/dashboard/billing)
2. Find the tile with your current plan and click **Adjust plan**
3. Select the plan you want
4. Confirm in the modal and click **Schedule Downgrade**

You keep your current plan until the end of your billing period. This applies to the legacy Pro, Pro+, and Ultra plans.

## Where do I manage my subscription?

- **The X Subscription:** [grok.com/dashboard/billing](https://grok.com/dashboard/billing) for plan changes, payment methods, invoices, top-ups, and cancellation.
- **Legacy Cursor plans:** [cursor.com/dashboard/billing](https://cursor.com/dashboard/billing) for plan changes, payment method updates, invoices, and cancellation. Click **Manage in Stripe** there to open the Stripe billing portal.

## What if I move from an individual plan to a Teams plan?

When you join a team, billing state can change based on the team setup flow. If your plan state looks wrong after joining, use [payment completed but plan not updated](https://cursor.com/help/account-and-billing/payment-not-applied.md) for troubleshooting steps.

## Can I switch between monthly and yearly billing?

On The X Subscription, choose monthly or annual when you change plans at [grok.com/dashboard/billing](https://grok.com/dashboard/billing).

On a legacy Cursor plan:

**To switch to yearly:**

1. Go to [cursor.com/dashboard/billing](https://cursor.com/dashboard/billing)
2. Click **Upgrade Now** on the green banner at the top

**To switch to monthly:**

There is no way to switch mid-plan. Use the [Adjust plan](https://cursor.com/help/account-and-billing/pricing.md#how-do-i-change-plans-on-a-legacy-cursor-plan) flow to schedule the switch at the end of your yearly billing period.

## Related

- [What is The X Subscription?](https://cursor.com/help/the-x-subscription/overview.md)
- [Billing and payments](https://cursor.com/help/account-and-billing/billing.md)
- [Cursor Start](https://cursor.com/help/account-and-billing/cursor-start.md)
- [Cancel your subscription](https://cursor.com/help/account-and-billing/cancel.md)
- [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md)
- [Usage and limits](https://cursor.com/help/models-and-usage/usage-limits.md)
- [Payment completed but plan not updated](https://cursor.com/help/account-and-billing/payment-not-applied.md)
- [Pricing reference](https://cursor.com/docs/models-and-pricing.md)
- [Legacy Cursor plans](https://cursor.com/docs/account/pricing/legacy-cursor-plans.md)
