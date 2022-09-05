package org.sjoblomj.wikipediastreetnamefilter.dbserver.dto

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.PropertyNamingStrategies
import com.fasterxml.jackson.databind.annotation.JsonNaming

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy::class)
data class RequestResponse(
	val placeId: Long = (0..999999999).random().toLong(),
	val license: String = "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
	val osmType: String = "way",
	val osmId: Long = 69856254,
	val boundingbox: List<String> = listOf("57.7364097", "57.7373341", "12.0241452", "12.0255203"),
	val lat: String = "57.7364778",
	val lon: String = "12.0245958",
	val displayName: String = "Alivallsgatan, Kviberg, Gamlestaden, \u00d6stra G\u00f6teborg, G\u00f6teborg, G\u00f6teborgs Stad, V\u00e4stra G\u00f6talands l\u00e4n, 415 28, Sverige",
	@JsonProperty("class")
	val klass: String = "highway",
	val type: String = "residential",
	val importance: Double = 0.71
)
