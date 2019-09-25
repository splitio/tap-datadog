# tap-fastly

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [Fastly](http://fastly.com)
- Extracts the following resources:
  - [Billing](https://docs.fastly.com/api/account#billing)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

## Config

*config.json*
```json
{
  "api_token": "THISISATOKEN",
  "start_date": "2000-01-01T00:00:00Z"
}
```