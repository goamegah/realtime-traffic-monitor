<<<<<<< HEAD:src/test/scala/com/goamegah/trafficmonitor/storage/S3StorageSpec.scala
26package com.goamegah.trafficmonitor.storage
=======
package com.goamegah.flowtrack.storage
>>>>>>> 9ef64451e790c267ec27f1da5ca3886fb5190246:src/test/scala/com/goamegah/flowtrack/storage/S3StorageSpec.scala


import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

class S3StorageSpec extends AnyFlatSpec with Matchers {

  "S3Storage" should "upload to the S3 curated folder" in {
    // println("[+++] Début du test d'envoi vers S3")
    val testJson =
      s"""{
         |  "test": "s3-storage",
         |  "source": "unit-test"
         |}""".stripMargin

    S3Storage.store(testJson, "curated")  // <= cette ligne doit déclencher les logs
    // Vérifiez que le fichier a été créé dans le dossier S3
    // Note: Vous devrez peut-être utiliser un client S3 pour vérifier cela

  }
}


