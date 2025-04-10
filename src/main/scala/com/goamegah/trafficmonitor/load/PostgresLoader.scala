package com.goamegah.trafficmonitor.load

import com.goamegah.trafficmonitor.config.AppConfig
import org.apache.spark.sql.{DataFrame, SaveMode, SparkSession}

object PostgresLoader {

  /** Charge un DataFrame dans une table PostgreSQL
   *
   * @param df        Le DataFrame à charger
   * @param tableName Nom de la table cible
   * @param mode      Mode de sauvegarde : "append", "overwrite", etc.
   */
  def load(df: DataFrame, tableName: String, mode: SaveMode = SaveMode.Append)(implicit spark: SparkSession): Unit = {
    val jdbcUrl = AppConfig.Postgres.jdbcUrl
    val properties = new java.util.Properties()
    properties.setProperty("user", AppConfig.Postgres.user)
    properties.setProperty("password", AppConfig.Postgres.password)
    properties.setProperty("driver", "org.postgresql.Driver")

    println(s"[=>] Insertion du DataFrame dans la table '$tableName'...")

    df.write
      .mode(mode)
      .jdbc(jdbcUrl, tableName, properties)

    println(s"[✔] Données insérées dans PostgreSQL -> table '$tableName'")
  }
}
