package org.sjoblomj.wikipediastreetnamefilter.dbserver.service

import de.topobyte.osm4j.core.access.OsmHandler
import de.topobyte.osm4j.core.model.iface.OsmEntity
import de.topobyte.osm4j.core.model.iface.OsmNode
import de.topobyte.osm4j.core.model.iface.OsmRelation
import de.topobyte.osm4j.core.model.iface.OsmWay
import de.topobyte.osm4j.core.model.util.OsmModelUtil
import de.topobyte.osm4j.geometry.GeometryBuilder
import de.topobyte.osm4j.geometry.MissingEntitiesStrategy
import de.topobyte.osm4j.geometry.MissingWayNodeStrategy
import de.topobyte.osm4j.pbf.seq.PbfReader
import org.sjoblomj.wikipediastreetnamefilter.dbserver.db.CategoryRepository
import org.sjoblomj.wikipediastreetnamefilter.dbserver.db.GeometryRepository
import org.sjoblomj.wikipediastreetnamefilter.dbserver.db.NativeQueryRepository
import org.sjoblomj.wikipediastreetnamefilter.dbserver.db.TagRepository
import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.CategoryEntity
import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.GeoEntity
import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.Tag
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import java.io.FileInputStream
import kotlin.system.measureTimeMillis

@Service
class GeneratorService(
	private val featureExtractor: FeatureExtractorInterface,
	private val categoryRepository: CategoryRepository,
	private val tagRepo: TagRepository,
	private val geoRepo: GeometryRepository,
	private val nativeQueryRepository: NativeQueryRepository
) {
	private val logger = LoggerFactory.getLogger(javaClass)

	fun consumeFile(filename: String) {
		logger.info("Starting to consume $filename")

		extractFeatures(filename)

		saveCategoriesToDatabase()
		saveTagsToDatabase()
		saveGeoEntitiesToDatabase()
		performNativeQueries()

		logger.info("All done!")
	}

	private fun extractFeatures(filename: String) {
		for (i in 0..featureExtractor.maxConsumptionRounds()) {
			if (featureExtractor.shouldRunConsumptionRound()) {
				logger.info("Iteration $i at finding interesting features")

				featureExtractor.startConsumptionRound()
				readPbfFileWithHandler(filename, featureExtractor)
				featureExtractor.finishConsumptionRound()
			} else
				break
		}
		logger.info("Finished finding interesting features")
	}

	private fun saveCategoriesToDatabase() {
		val timeTaken = measureTimeMillis {
			val previouslySavedCategories = categoryRepository.findAll().map { it.name }
			featureExtractor.getCategoriesToBePersisted()
				.filter { !previouslySavedCategories.contains(it) }
				.forEach { categoryRepository.save(CategoryEntity(0, it)) }
		}
		logger.info("Saved categories to database in $timeTaken ms")
	}

	private fun saveTagsToDatabase() {
		fun saveTags(entities: Collection<OsmEntity>) {
			val tags = entities.flatMap { entity ->
				val tags = OsmModelUtil.getTagsAsMap(entity)
				tags.map { tag -> Tag(entity.id, tag.key, tag.value) }
			}
			tagRepo.saveAll(tags)
		}

		logger.info("About to save tags to database")
		val timeTaken = measureTimeMillis {
			saveTags(featureExtractor.getNodesAndCategoriesToBePersisted().keys)
			saveTags(featureExtractor.getWaysAndCategoriesToBePersisted().keys)
			saveTags(featureExtractor.getRelationsAndCategoriesToBePersisted().keys)
		}
		logger.info("Saved tags in $timeTaken ms")
	}


	private fun saveGeoEntitiesToDatabase() {
		logger.info("Creating GeoEntities")
		val geometryBuilder = GeometryBuilder().also {
			it.missingWayNodeStrategy = MissingWayNodeStrategy.OMIT_VERTEX_FROM_POLYLINE
			it.missingEntitiesStrategy = MissingEntitiesStrategy.BUILD_PARTIAL
		}

		val allCategories = categoryRepository.findAll()
		fun <T : OsmEntity> createGeoEntities(entities: Map<T, Collection<Category>>) = entities
			.map { (entity, categories) -> Triple(entity.id, buildGeometry(entity, geometryBuilder), categories) }
			.filter { it.second != null }
			.map { (id, geom, categories) ->
				GeoEntity(id, geom!!, categories.map { categoryName -> allCategories.first { it.name == categoryName }.categoryid })
			}

		logger.info("Saving GeoEntities to database")
		val dbTimeTaken = measureTimeMillis {
			geoRepo.saveAll(createGeoEntities(featureExtractor.getRelationsAndCategoriesToBePersisted()))
			geoRepo.saveAll(createGeoEntities(featureExtractor.getWaysAndCategoriesToBePersisted()))
			geoRepo.saveAll(createGeoEntities(featureExtractor.getNodesAndCategoriesToBePersisted()))
		}
		logger.info("Took $dbTimeTaken ms to save GeoEntities to database.")
	}

	private fun buildGeometry(entity: OsmEntity, geometryBuilder: GeometryBuilder) =
		when (entity) {
			is OsmNode     -> buildGeom(entity, geometryBuilder)
			is OsmWay      -> buildGeom(entity, geometryBuilder)
			is OsmRelation -> buildGeom(entity, geometryBuilder)
			else           -> null
		}


	private fun performNativeQueries() {
		val nativeQueryTime = measureTimeMillis {
			nativeQueryRepository.homogenizeAllGeoms()
			nativeQueryRepository.createGeoEntryCategoryIndex()
			nativeQueryRepository.createHideIdsTable()
		}
		logger.info("Took $nativeQueryTime ms to perform native queries.")
	}


	private fun buildGeom(entity: OsmNode, geometryBuilder: GeometryBuilder) =
		try {
			geometryBuilder.build(entity)
		} catch (e: Exception) {
			logger.error("Exception for ${entity::class.java.simpleName} ${entity.id}: $e")
			null
		}

	private fun buildGeom(entity: OsmWay, geometryBuilder: GeometryBuilder) =
		try {
			geometryBuilder.build(entity, featureExtractor)
		} catch (e: Exception) {
			logger.error("Exception for ${entity::class.java.simpleName} ${entity.id}: $e")
			null
		}

	private fun buildGeom(entity: OsmRelation, geometryBuilder: GeometryBuilder) =
		try {
			geometryBuilder.build(entity, featureExtractor)
		} catch (e: Exception) {
			logger.error("Exception for ${entity::class.java.simpleName} ${entity.id}: $e")
			null
		}

	private fun readPbfFileWithHandler(file: String, handler: OsmHandler) {
		FileInputStream(file).use {
			val reader = PbfReader(it, false)
			reader.setHandler(handler)
			reader.read()
		}
	}
}
