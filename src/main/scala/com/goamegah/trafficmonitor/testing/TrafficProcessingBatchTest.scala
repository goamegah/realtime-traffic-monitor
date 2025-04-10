package com.goamegah.trafficmonitor.testing

import org.apache.spark.sql.SparkSession
import com.goamegah.trafficmonitor.streaming.TrafficTransformer
import com.goamegah.trafficmonitor.processing.TrafficStatsAggregator

object TrafficProcessingBatchTest {

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("TrafficProcessingBatchTest")
      .master("local[*]")
      .getOrCreate()

    import spark.implicits._

    // 👉 Choisis un fichier JSON réel
    val inputPath = "services/orchestrator/data/raw/20250409010002792155.json"
    val df = spark.read
      .option("multiLine", true)
      .json(inputPath)

    println("📥 JSON brut chargé :")
    df.printSchema()
    df.show(2, truncate = false)

    // 👉 Étape 1 : Transformation
    val transformed = TrafficTransformer.transform(df)(spark)
    println("🧼 Données transformées :")
    transformed.printSchema()
    transformed.show(5, truncate = false)

    // 👉 Étape 2 : Agrégation par tronçon
    val aggregated = TrafficStatsAggregator.aggregate(transformed)
    println("📊 Agrégation simple par tronçon :")
    aggregated.show(5, truncate = false)

    // 👉 Étape 3 : Agrégation par minute
    val aggregatedByMinute = TrafficStatsAggregator.aggregateByMinute(transformed)
    println("⏱ Agrégation par minute :")
    aggregatedByMinute.show(5, truncate = false)

    spark.stop()
  }
}
