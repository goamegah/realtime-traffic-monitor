package com.goamegah.trafficmonitor.db

import java.nio.file.{Files, Paths}
import scala.io.Source
import java.sql.DriverManager
import com.goamegah.trafficmonitor.config.AppConfig

object DBSchemaManager {

  def executeSqlFile(filePath: String): Unit = {
    val sql = Source.fromFile(filePath).getLines().mkString("\n")
    val conn = DriverManager.getConnection(
      AppConfig.Postgres.jdbcUrl,
      AppConfig.Postgres.user,
      AppConfig.Postgres.password
    )

    try {
      val stmt = conn.createStatement()
      stmt.execute(sql)
      println(s"[✔] Script exécuté : $filePath")
    } catch {
      case ex: Exception =>
        println(s"[❌] Erreur d’exécution pour $filePath : ${ex.getMessage}")
    } finally {
      conn.close()
    }
  }

  def init(): Unit = {
    println("[🛠] Initialisation du schéma PostgreSQL...")

    executeSqlFile("ddl/tables/create_traffic_stream.sql")
    executeSqlFile("ddl/views/create_view_traffic_status_latest.sql")

    println("[✅] Schéma PostgreSQL initialisé avec succès.")
  }
}

