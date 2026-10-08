from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("IND320-Cassandra-Test")
    .master("local[*]")
    .config(
        "spark.jars.packages",
        "com.datastax.spark:spark-cassandra-connector_2.12:3.5.1"
    )
    .config("spark.cassandra.connection.host", "127.0.0.1")
    .config("spark.cassandra.connection.port", "9042")
    .getOrCreate()
)

df = (
    spark.read
    .format("org.apache.spark.sql.cassandra")
    .options(
        table="connection_test",
        keyspace="ind320_test"
    )
    .load()
)

df.show()

spark.stop()