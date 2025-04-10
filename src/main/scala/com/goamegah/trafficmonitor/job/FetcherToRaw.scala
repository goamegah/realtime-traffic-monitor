package com.goamegah.trafficmonitor.job

import com.goamegah.trafficmonitor.api.FetchTrafficData
import com.goamegah.trafficmonitor.storage.LocalStorage

object FetcherToRaw {

  def main(args: Array[String]): Unit = {
    println("[...] Lancement de la collecte manuelle vers raw/ ...")

    val dataOpt = FetchTrafficData.fetchData()

    dataOpt match {
      case Some(json) =>
        // On stocke dans le dossier "raw" (pour être lu par readStream)
        LocalStorage.store(json, prefix = "raw")
        println("[OK] Données stockées dans raw/")
      case None =>
        println("[/!\\] Aucune donnée reçue de l'API.")
    }
  }
}
