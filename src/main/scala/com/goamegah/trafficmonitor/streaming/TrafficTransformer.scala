package com.goamegah.trafficmonitor.streaming

import org.apache.spark.sql.functions._
import org.apache.spark.sql.{DataFrame, SparkSession}

object TrafficTransformer {

  def transform(inputDF: DataFrame)(implicit spark: SparkSession): DataFrame = {
    import spark.implicits._

    println("[🔧] Étape 1 - Données brutes (streaming)")
    inputDF.printSchema()
    // 🚫 .count() interdit en streaming
    // 🚫 .show() interdit en streaming

    // Étape 2 - Explosion du champ `results`
    val explodedDF = inputDF
      .filter(col("results").isNotNull && size(col("results")) > 0)
      .withColumn("result", explode(col("results")))

    println("[🧨] Étape 2 - Après explosion de 'results'")
    explodedDF.printSchema()

    // Étape 3 - Sélection des colonnes utiles
    val selectedDF = explodedDF.selectExpr("result.*")

    println("[📊] Étape 3 - Après sélection des champs")
    selectedDF.printSchema()

    // Étape 4 - Transformation : ajout lat/lon et filtrage
    val transformedDF = selectedDF
      .withColumn("lat", col("geo_point_2d.lat"))
      .withColumn("lon", col("geo_point_2d.lon"))
      .drop("geo_point_2d")
      .filter(col("datetime").isNotNull)

    println("[🧼] Étape 4 - Après nettoyage/filtrage final")
    transformedDF.printSchema()

    transformedDF
  }
}
