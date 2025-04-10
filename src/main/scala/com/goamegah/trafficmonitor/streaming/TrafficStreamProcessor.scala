package com.goamegah.trafficmonitor.streaming

import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger
import org.apache.spark.sql.types._
import org.apache.spark.sql.{DataFrame, SparkSession}
import com.goamegah.trafficmonitor.config.AppConfig
import com.goamegah.trafficmonitor.load.PostgresLoader
import com.goamegah.trafficmonitor.common.SparkSessionProvider.spark
import com.goamegah.trafficmonitor.processing.TrafficStatsAggregator
import scala.concurrent.duration._

object TrafficStreamProcessor {

  implicit val sparkSession: SparkSession = spark
  import spark.implicits._

  // Schéma statique pour le streaming
  val trafficSchema: StructType = new StructType()
    .add("results", ArrayType(new StructType()
      .add("datetime", StringType)
      .add("predefinedlocationreference", StringType)
      .add("averagevehiclespeed", IntegerType)
      .add("traveltime", IntegerType)
      .add("trafficstatus", StringType)
      .add("vehicleprobemeasurement", IntegerType)
      .add("geo_point_2d", new StructType()
        .add("lat", DoubleType)
        .add("lon", DoubleType)
      )
      .add("geo_shape", new StructType()
        .add("geometry", new StructType()
          .add("coordinates", ArrayType(ArrayType(DoubleType)))
          .add("type", StringType)
        )
      )
      .add("denomination", StringType)
      .add("vitesse_maxi", IntegerType)
      .add("hierarchie", StringType)
    ))

  def start(): Unit = {
    println("[...] Démarrage du streaming...")

    // Lecture des fichiers JSON depuis le répertoire configuré
    val rawStream: DataFrame = spark.readStream
      .schema(trafficSchema)
      .option("maxFilesPerTrigger", 1)
      .json(AppConfig.Local.rawDir)

    // Appliquer la transformation
    val transformed = TrafficTransformer.transform(rawStream)

    // Récupération des paramètres de trigger et du checkpoint depuis AppConfig
    val triggerInterval = AppConfig.Streaming.triggerInterval
    val checkpointPath = AppConfig.Streaming.checkpointDir
    val useSlidingWindow = AppConfig.Streaming.useSlidingWindow

    val query = transformed.writeStream
      .foreachBatch { (batchDF: DataFrame, batchId: Long) =>
        val count = batchDF.count()
        println(s"[<->] Batch $batchId - $count lignes")

        if (count == 0) {
          println(s"[/!\\] Batch $batchId vide - rien à insérer.")
        } else {
          println("[CHECK] Échantillon du batch reçu :")
          batchDF.show(5, truncate = false)

          try {
            // Insertion des données brutes dans la table "traffic_stream"
            PostgresLoader.load(batchDF, "traffic_stream")

            // Appliquer l'agrégation en fonction du mode choisi
            if (useSlidingWindow) {
              val slidingAggregated = TrafficStatsAggregator.aggregateBySlidingWindow(batchDF)
              PostgresLoader.load(slidingAggregated, "traffic_stats_sliding_window")
            } else {
              val aggregated = TrafficStatsAggregator.aggregateByMinute(batchDF)
              PostgresLoader.load(aggregated, "traffic_stats_by_minute")
            }
          } catch {
            case e: Exception =>
              println(s"[/!\\] Erreur lors du traitement du batch $batchId : ${e.getMessage}")
              e.printStackTrace()
          }
        }
      }
      .outputMode("update")
      .trigger(Trigger.ProcessingTime(triggerInterval))
      .option("checkpointLocation", checkpointPath)
      .start()

    query.awaitTermination()
  }
}
