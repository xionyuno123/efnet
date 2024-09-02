import mill._
import mill.define.Sources
import mill.modules.Util
import scalalib._
import mill.bsp._

object rtlbuild extends SbtModule {
  override def millSourcePath = os.pwd
  override def scalaVersion = "2.13.12"
  override def scalacOptions = Seq(
    "-language:reflectiveCalls",
    "-deprecation",
    "-feature",
    "-Xcheckinit"
  )

  override def ivyDeps = Agg(
    ivy"org.chipsalliance::chisel:6.4.0",
    ivy"com.typesafe.scala-logging::scala-logging:3.9.4",
    ivy"ch.qos.logback:logback-classic:1.4.0",
    ivy"org.slf4j:slf4j-api:1.7.25"
  )

  override def scalacPluginIvyDeps = Agg(
    ivy"org.chipsalliance:::chisel-plugin:6.4.0"
  )


}
