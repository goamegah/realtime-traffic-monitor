package com.goamegah.trafficmonitor

import com.goamegah.trafficmonitor.db.DBSchemaManager
import com.goamegah.trafficmonitor.streaming.TrafficStreamProcessor

object MainApp {
  def main(args: Array[String]): Unit = {
    // Initialisation du schéma PostgreSQL
    DBSchemaManager.init()

    // Lancement du streaming des données
    TrafficStreamProcessor.start()
  }
}

