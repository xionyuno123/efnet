package efnet.utils

import com.typesafe.scalalogging.Logger
import org.slf4j.LoggerFactory
import com.typesafe.scalalogging.LoggerImpl
import org.slf4j.Marker

object logger {
  private val _logging = Logger(LoggerFactory.getLogger("rtlbuild"))
  
  // Warn

  def warn(message: String): Unit = {
    _logging.warn(message)
  }

  def warn(message: String, cause: Throwable): Unit = {
    _logging.warn(message,cause)
  }

  def warn(message: String, args: Any*): Unit = {
    _logging.warn(message,args)
  }

  def warn(marker: Marker, message: String): Unit = {
    _logging.warn(marker,message)
  }

  def warn(marker: Marker, message: String, cause: Throwable): Unit = {
    _logging.warn(marker,message,cause)
  }

  def warn(marker: Marker, message: String, args: Any*): Unit = {
    _logging.warn(marker,message,args)
  }

  // Info

  def info(message: String): Unit = {
    _logging.info(message)
  }

  def info(message: String, cause: Throwable): Unit = {
    _logging.info(message,cause)
  }

  def info(message: String, args: Any*): Unit = {
    _logging.info(message,args)
  }

  def info(marker: Marker, message: String): Unit = {
    _logging.info(marker,message)
  }

  def info(marker: Marker, message: String, cause: Throwable): Unit = {
    _logging.info(marker,message,cause)
  }
  def info(marker: Marker, message: String, args: Any*): Unit = {
    _logging.info(marker,message,args)
  }

  // Error

  def error(message: String): Unit = {
    _logging.error(message)
  }

  def error(message: String, cause: Throwable): Unit = {
    _logging.error(message,cause)
  }

  def error(message: String, args: Any*): Unit = {
    _logging.error(message,args)
  }

  def error(marker: Marker, message: String): Unit = {
    _logging.error(marker,message)
  }

  def error(marker: Marker, message: String, cause: Throwable): Unit = {
    _logging.error(marker,message,cause)
  }

  def error(marker: Marker, message: String, args: Any*): Unit = {
    _logging.error(marker,message,args)
  }
}