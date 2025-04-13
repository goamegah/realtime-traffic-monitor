import scala.util.{Try, Success, Failure}
import java.io.{PrintWriter, File}
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import scalaj.http._

object FetchTraffic {
  def main(args: Array[String]): Unit = {
    val apiUrl = "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel@parisdata/records?limit=100"
    val response = Try(Http(apiUrl).asString.body)

    response match {
      case Success(body) =>
        val timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmssSSS"))
        val dir = new File("/opt/airflow/data/transient")
        if (!dir.exists()) dir.mkdirs()
        val file = new File(dir, s"${timestamp}.json")
        val writer = new PrintWriter(file)
        writer.write(body)
        writer.close()
        println(s"Data saved to ${file.getAbsolutePath}")

      case Failure(exception) =>
        println(s"Error fetching data: ${exception.getMessage}")
    }
  }
}
