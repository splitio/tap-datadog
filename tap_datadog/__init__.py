#!/usr/bin/env python3
import os
import singer
import asyncio
import simplejson

from singer import utils, metadata

from tap_datadog.sync import DatadogAuthentication, DatadogClient, DatadogSync

REQUIRED_CONFIG_KEYS = ["start_month",
                        "start_hour",
                        "api_token",
                        "application_key"]
LOGGER = singer.get_logger()

SCHEMA_PRIMARY_KEYS = { 
    "custom_usage": ["hour"],
    "fargate": ["hour"],
    "hosts_and_containers": ["hour"],
    "logs": ["hour"],
    "synthetics": ["hour"],
    "top_average_metrics": ["month","metric_name"],
    "trace_search": ["hour"]
}


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

# Load schemas from schemas folder
def load_schemas():
    schemas = {}

    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = simplejson.load(file)

    return schemas



def load_schema(tap_stream_id):
    path = "schemas/{}.json".format(tap_stream_id)
    schema = utils.load_json(get_abs_path(path))
    refs = schema.pop("definitions", {})
    if refs:
        singer.resolve_schema_references(schema, refs)
    return schema

def generate_metadata(schema_name, schema): 
    pk_fields = SCHEMA_PRIMARY_KEYS[schema_name]
    mdata = metadata.new()
    mdata = metadata.write(mdata, (), 'table-key-properties', pk_fields)

    for field_name in schema['properties'].keys():
        if field_name in pk_fields:
            mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'automatic')
        else:
            mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'available')

    return metadata.to_list(mdata)


def discover():
    
    streams = []

    for schema_name in SCHEMA_PRIMARY_KEYS.keys():

        # TODO: populate any metadata and stream's key properties here..
        schema = load_schema(schema_name) 
        stream_metadata = generate_metadata(schema_name, schema)
        stream_key_properties = SCHEMA_PRIMARY_KEYS[schema_name]

        # create and add catalog entry
        catalog_entry = {
            'stream': schema_name,
            'tap_stream_id': schema_name,
            'schema': schema,
            'metadata' : stream_metadata,
            'key_properties': stream_key_properties
        }
        streams.append(catalog_entry)

    return {'streams': streams}

def get_selected_streams(catalog):
    '''
    Gets selected streams.  Checks schema's 'selected' first (legacy)
    and then checks metadata (current), looking for an empty breadcrumb
    and mdata with a 'selected' entry
    '''
    selected_streams = []
    for stream in catalog['streams']: 
        stream_metadata = metadata.to_map(stream['metadata'])
        if metadata.get(stream_metadata, (), "selected"):
            selected_streams.append(stream['tap_stream_id'])

    return selected_streams

def create_sync_tasks(config, state, catalog):
    auth = DatadogAuthentication(config["api_token"], config["application_key"])
    client = DatadogClient(auth)
    sync = DatadogSync(client, state, config)

    
    sync_tasks = (sync.sync(stream['tap_stream_id'], stream['schema'])
                  for stream in catalog['streams']
                
    )   

    return asyncio.gather(*sync_tasks)

def sync(config, state, catalog):
    loop = asyncio.get_event_loop()
    try:
        tasks = create_sync_tasks(config, state, catalog)
        loop.run_until_complete(tasks)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

@utils.handle_top_exception(LOGGER)
def main():
    # Parse command line arguments
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover()
        print(simplejson.dumps(catalog, indent=2))
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = discover()

        config = args.config
        state = {
            "bookmarks": {

            }
        }
        state.update(args.state)

        sync(config, state, catalog)

if __name__ == "__main__":
    main()
