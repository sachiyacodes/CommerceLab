# Data dictionary

The CSV contract is deliberately flat. It is the output of normalization from the nested GA4 export. Blank `item_id` or `item_name` means that value was unavailable; in the bundled demo, blank item fields indicate an event with no item record. Numeric price is in the row's `currency`; bundled demo data uses USD.

| Column | Type | Meaning |
|---|---|---|
| `event_date` | YYYY-MM-DD | GA4 event calendar date |
| `event_timestamp` | ISO 8601 UTC | Timestamp for the event occurrence |
| `event_name` | text | GA4 event name, such as `session_start`, `view_item`, `add_to_cart`, or `purchase` |
| `user_pseudo_id` | text | Pseudonymous device/browser identifier; not a person ID |
| `session_id` | text | User plus GA session id when available; local sample session key |
| `channel` | text | Broad attribution label derived from source/medium; demo values generated |
| `country` | text | Country from GA4 geo export |
| `device_category` | text | Device category |
| `transaction_id` | text | Ecommerce transaction ID, usually set on purchase |
| `item_id` | text | Item ID, blank when no item row exists |
| `item_name` | text | Item display name |
| `quantity` | integer | Event item quantity; zero when no item row exists |
| `price` | decimal | Unit price; zero when no item row exists |
| `currency` | text | Currency code from the GA4 event parameter when available; `Unknown` marks missing currency. Demo uses USD. |

Validation checks the required schema, parseable dates and UTC timestamps, finite nonnegative numeric prices/quantities, duplicate event signatures, and missing user IDs. Duplicate signatures are reported but do not automatically fail validation because one GA4 event may expand to multiple item rows.

## Known measurement caveats

The acquisition, product, and RFM SQL examples use a required `@currency` parameter for money-related measures. Supply one currency code such as `USD`, or `Unknown` to inspect rows missing a currency parameter.

The optional public export is obfuscated and should be treated as sample data. The local rows are simulated and should never be quoted as real business findings. Flat event-item rows require care to avoid double-counting event totals. Revenue is `quantity × price` on purchase rows; refunds, discounts, taxes, shipping, and currency conversion are outside this MVP.
