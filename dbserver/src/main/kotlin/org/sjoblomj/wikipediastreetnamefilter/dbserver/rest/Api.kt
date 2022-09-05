package org.sjoblomj.wikipediastreetnamefilter.dbserver.rest

import org.locationtech.jts.geom.Coordinate
import org.sjoblomj.wikipediastreetnamefilter.dbserver.db.CategoryRepository
import org.sjoblomj.wikipediastreetnamefilter.dbserver.db.GeometryRepository
import org.sjoblomj.wikipediastreetnamefilter.dbserver.db.TagRepository
import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.GeoEntity
import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.RequestResponse
import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.Tag
import org.sjoblomj.wikipediastreetnamefilter.dbserver.service.GeneratorService
import org.slf4j.LoggerFactory
import org.springframework.util.MimeTypeUtils.APPLICATION_JSON_VALUE
import org.springframework.web.bind.annotation.*

@CrossOrigin
@RestController
class Api(
	private val generatorService: GeneratorService,
	private val health: Health,
	private val geometryRepository: GeometryRepository,
	private val tagRepository: TagRepository,
	private val categoryRepository: CategoryRepository
) {
	private val logger = LoggerFactory.getLogger(javaClass)

	@PostMapping("/consume")
	fun consume(@RequestParam filename: String) {
		logger.info("Will consume $filename")
		health.isReady = false
		generatorService.consumeFile(filename)
		health.isReady = true
	}


	// Call with curl localhost:7171/search\?q=Avinguda%20de%20Fran%C3%A7ois%20Mitterrand
	@GetMapping("/search", produces = [APPLICATION_JSON_VALUE])
	fun getFeatures(@RequestParam("q") name: String): List<RequestResponse> {

		return try {
			val tags = tagRepository.findAllByName(name)
			val allTagsForId = tags.map { tagRepository.findAllById(it.id) }
			val geoEntriesAndTags = allTagsForId
				.map { geometryRepository.findById(it[0].id) to it }
				.filter { it.first.isPresent }
				.map { it.first.get() to it.second }

			geoEntriesAndTags.map { createResponses(it) }
		} catch (e: Exception) {
			logger.error("Failed to getFeatures", e)
			emptyList()
		}
	}

	private fun createResponses(data: Pair<GeoEntity, List<Tag>>): RequestResponse {
		val geom = data.first.geom
		val tags = data.second

		val klass = getClass(tags)
		val type = getType(tags, klass)
		val osmType = getOsmType(data.first.category)

		return RequestResponse(
			osmId = data.first.id,
			boundingbox = processCoordinates(geom.coordinates),
			lat = geom.coordinate.y.toString(),
			lon = geom.coordinate.x.toString(),
			displayName = tags.first { it.key == "name" }.value + ", Sverige",
			klass = klass,
			type = type,
			osmType = osmType,
		)
	}

	private fun getOsmType(category: Collection<Int>): String {
		val list = mutableListOf<Int>()
		val iterator = category.iterator()
		while (iterator.hasNext())
			list.add(iterator.next())

		val categories = categoryRepository.findAll()
			.filter { list.contains(it.categoryid) }
			.map { it.name }

		if (categories.size != 1)
			logger.warn("Found too many/no categories: $categories")
		return categories.first()
	}

	private fun processCoordinates(coords: Array<Coordinate>) =
		listOf(coords.minOf { it.y }, coords.maxOf { it.y }, coords.minOf { it.x }, coords.maxOf { it.x } )
			.map { it.toString() }

	private fun getClass(tags: List<Tag>): String {
		val keywords = listOf("place", "building", "landuse", "leisure", "natural", "man_made", "bridge", "highway")
		for (key in keywords)
			if (tags.hasKey(key))
				return key

		return "unknown"
	}

	private fun List<Tag>.hasKey(key: String) = this.any { it.key == key }

	private fun getType(tags: List<Tag>, key: String) = tags.firstOrNull { it.key == key } ?. value ?: ""
}
