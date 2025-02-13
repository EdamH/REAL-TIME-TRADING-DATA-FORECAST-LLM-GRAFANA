from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.types import StructType, StructField, DoubleType, IntegerType, StringType
from pyspark.sql.functions import from_json, col, concat_ws

# Define the data schema
schema = StructType([
    StructField("c", DoubleType(), True),    # Clôture
    StructField("h", DoubleType(), True),    # Haut
    StructField("l", DoubleType(), True),    # Bas
    StructField("n", IntegerType(), True),   # Nombre
    StructField("o", DoubleType(), True),    # Ouverture
    StructField("t", StringType(), True),    # Timestamp
    StructField("v", DoubleType(), True),   # Volume
    StructField("vw", DoubleType(), True),   # Volume moyen pondéré
    StructField("symbol", StringType(), True) # Symbole (ex : BTC/USD)
])

# Spark configuration
spark_conf = SparkConf() \
    .setAppName("trading_consumer") \
    .setMaster("local") \
    .set("spark.executor.memory", "2g") \
    .set("spark.executor.cores", "2")

# Create SparkSession
spark = SparkSession.builder.config(conf=spark_conf).getOrCreate()

# Set log level to ERROR
spark.sparkContext.setLogLevel("ERROR")

# Read from the Kafka topic 'trading'
dataframe = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "trading") \
    .load()

# Parse JSON data and match schema
dataframe = dataframe.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("es_id", concat_ws("_", col("symbol"), col("t")))


# Writing to console
# query = dataframe \
#     .writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .start()


# WRITING INTO ELASTICSEARCH
query = dataframe.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .outputMode("update") \
    .option("es.mapping.id", "es_id") \
    .option("es.nodes", "elasticsearch") \
    .option("es.port", "9200") \
    .option("es.nodes.wan.only","true") \
    .option("checkpointLocation", "tmp/checkpoint2") \
    .option("es.resource", "trading")\
    .start()# WRITING INTO ELASTICSEARCH

query.awaitTermination()
