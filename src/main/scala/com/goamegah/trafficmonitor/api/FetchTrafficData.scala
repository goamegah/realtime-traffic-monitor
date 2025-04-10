package com.goamegah.trafficmonitor.api

import com.goamegah.trafficmonitor.config.AppConfig
import scalaj.http._
import scala.util.{Try, Success, Failure}

/** Client API pour récupérer les données de trafic */
object FetchTrafficData {

  /** Récupère les données JSON depuis un endpoint.
   * Si aucun endpoint n'est fourni, utilise celui de la config.
   *
   * @param endpoint URL à appeler (optionnel)
   * @return Option[String] contenant le JSON ou None en cas d'échec
   */
  def fetchData(endpoint: Option[String] = None): Option[String] = {
    val url = endpoint.getOrElse(AppConfig.API.endpoint)

    //println(s"[INFO] Appel API vers : $url")

    Try(Http(url).timeout(5000, 10000).asString) match {
      case Success(response) if response.is2xx =>
        //println(s"[DEBUG] OK Données reçues (${response.body.length} caractères)")
        Some(response.body)

      case Success(response) =>
        //println(s"[DEBUG] /!\\ Échec API (${response.code}) : ${response.body}")
        None

      case Failure(ex) =>
        //println(s"[DEBUG] /!\\ Exception lors de l’appel API : ${ex.getMessage}")
        None
    }
  }
}
