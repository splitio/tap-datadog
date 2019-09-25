# tap-datadog

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [Datadog](https://docs.datadoghq.com/api/?lang=python#overview)
- Extracts the following resources:
  - [Hourly usage for hosts and containers](https://docs.datadoghq.com/api/?lang=python#get-hourly-usage-for-hosts-and-containers)
  - [Hourly usage for logs](https://docs.datadoghq.com/api/?lang=python#get-hourly-usage-for-logs)
  - [Hourly usage for custom metrics](https://docs.datadoghq.com/api/?lang=python#get-hourly-usage-for-custom-metrics)
  - [Hourly usage for Trace Search](https://docs.datadoghq.com/api/?lang=python#get-hourly-usage-for-custom-metrics)
  - [Hourly usage for Synthetics](https://docs.datadoghq.com/api/?lang=python#get-hourly-usage-for-synthetics)
  - [Hourly usage for Fargate](https://docs.datadoghq.com/api/?lang=python#get-hourly-usage-for-fargate)
  - [Top 500 custom metrcis by hourly average](https://docs.datadoghq.com/api/?lang=python#get-top-500-custom-metrics-by-hourly-average)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

## Config

*config.json*
```json
{
  "start_month":"2019-07",
  "start_hour":"2019-06-17T12",
  "api_token":"DATADOG_API_KEY",
  "application_key":"DATADOG_APPLICATION_KEY"}

```
