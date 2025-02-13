from elasticsearch import Elasticsearch

# Create an Elasticsearch client
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# Define the index name
index_name = "trading"

# Define the mapping for Elasticsearch index
mapping = {
  "mappings": {
    "properties": {
      "c": { "type": "float" },  
      "h": { "type": "float" },  
      "l": { "type": "float" },  
      "n": { "type": "integer" },  
      "o": { "type": "float" },  
      "t": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },  
      "v": { "type": "float" },  
      "vw": { "type": "float" },  
      "symbol": { "type": "keyword" }  
    }
  }
}



# Check if the Elasticsearch index exists
if es.indices.exists(index=index_name):
    # Delete the index
    es.indices.delete(index=index_name)
    print(f"Index '{index_name}' has been deleted.")
else:
    print(f"Index '{index_name}' does not exist.")

# Create the Elasticsearch index with the specified mapping of my data
es.indices.create(index=index_name, mappings=mapping["mappings"])
