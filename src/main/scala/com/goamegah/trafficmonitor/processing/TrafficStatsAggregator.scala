package com.goamegah.trafficmonitor.processing

import org.apache.spark.sql.{DataFrame, SparkSession, functions => F}
import com.goamegah.trafficmonitor.config.AppConfig

object TrafficStatsAggregator {

  /**
   * Applique une agrégation statistique sur les données de trafic transformées.
   * @param df Le DataFrame transformé avec une ligne par mesure de trafic
   * @return Un DataFrame agrégé avec des statistiques par tronçon ou zone
   */
  def aggregate(df: DataFrame): DataFrame = {
    df
      .filter(F.col("predefinedlocationreference").isNotNull)
      .groupBy("predefinedlocationreference")
      .agg(
        F.count("*").alias("nb_mesures"),
        F.avg("averagevehiclespeed").alias("vitesse_moyenne"),
        F.avg("traveltime").alias("temps_trajet_moyen"),
        F.first("denomination", ignoreNulls = true).alias("denomination"),
        F.first("hierarchie", ignoreNulls = true).alias("hierarchie"),
        F.first("vitesse_maxi", ignoreNulls = true).alias("vitesse_maxi"),
        F.first("lat", ignoreNulls = true).alias("lat"),
        F.first("lon", ignoreNulls = true).alias("lon"),
        F.first("trafficstatus", ignoreNulls = true).alias("statut_trafic")
      )
  }

  def aggregateByMinute(df: DataFrame): DataFrame = {
    df
      .withColumn("timestamp", F.to_timestamp(F.col("datetime")))
      .withColumn("minute", F.date_trunc("minute", F.col("timestamp")))
      .filter(F.col("predefinedlocationreference").isNotNull)
      .groupBy("minute", "predefinedlocationreference")
      .agg(
        F.count("*").alias("nb_mesures"),
        F.avg("averagevehiclespeed").alias("vitesse_moyenne"),
        F.avg("traveltime").alias("temps_trajet_moyen"),
        F.first("denomination", ignoreNulls = true).alias("denomination"),
        F.first("hierarchie", ignoreNulls = true).alias("hierarchie"),
        F.first("vitesse_maxi", ignoreNulls = true).alias("vitesse_maxi"),
        F.first("lat", ignoreNulls = true).alias("lat"),
        F.first("lon", ignoreNulls = true).alias("lon"),
        F.first("trafficstatus", ignoreNulls = true).alias("statut_trafic")
      )
  }

  /**
   * Agrège les données par fenêtre glissante.
   * Ici, on utilise une fenêtre de 5 minutes avec un glissement de 1 minute.
   *
   * @param df Le DataFrame transformé avec une ligne par mesure de trafic.
   * @return Un DataFrame agrégé par tranche de temps et par tronçon.
   */

  def aggregateBySlidingWindow(df: DataFrame)(implicit spark: SparkSession): DataFrame = {
    val windowDuration = AppConfig.Streaming.slidingWindowDuration
    val slideDuration = AppConfig.Streaming.slidingWindowSlide

    df
      .withColumn("timestamp", F.to_timestamp(F.col("datetime")))
      .groupBy(
        F.window(F.col("timestamp"), windowDuration, slideDuration),
        F.col("predefinedlocationreference")
      )
      .agg(
        F.count("*").alias("nb_mesures"),
        F.avg("averagevehiclespeed").alias("vitesse_moyenne"),
        F.avg("traveltime").alias("temps_trajet_moyen"),
        F.first("denomination", ignoreNulls = true).alias("denomination"),
        F.first("hierarchie", ignoreNulls = true).alias("hierarchie"),
        F.first("vitesse_maxi", ignoreNulls = true).alias("vitesse_maxi"),
        F.first("lat", ignoreNulls = true).alias("lat"),
        F.first("lon", ignoreNulls = true).alias("lon"),
        F.first("trafficstatus", ignoreNulls = true).alias("statut_trafic")
      )
      .withColumn("window_start", F.col("window.start"))
      .withColumn("window_end", F.col("window.end"))
      .drop("window")
  }

  //  def aggregateBySlidingWindow(df: DataFrame): DataFrame = {
  //    df
  //      .withColumn("timestamp", F.to_timestamp(F.col("datetime")))
  //      .groupBy(
//        F.window(F.col("timestamp"), "5 minutes", "1 minute"),
//        F.col("predefinedlocationreference")
//      )
//      .agg(
//        F.count("*").alias("nb_mesures"),
//        F.avg("averagevehiclespeed").alias("vitesse_moyenne"),
//        F.avg("traveltime").alias("temps_trajet_moyen"),
//        F.first("denomination", ignoreNulls = true).alias("denomination"),
//        F.first("hierarchie", ignoreNulls = true).alias("hierarchie"),
//        F.first("vitesse_maxi", ignoreNulls = true).alias("vitesse_maxi"),
//        F.first("lat", ignoreNulls = true).alias("lat"),
//        F.first("lon", ignoreNulls = true).alias("lon"),
//        F.first("trafficstatus", ignoreNulls = true).alias("statut_trafic")
//      )
//      .withColumn("window_start", F.col("window.start"))
//      .withColumn("window_end", F.col("window.end"))
//      .drop("window")
//  }

}
