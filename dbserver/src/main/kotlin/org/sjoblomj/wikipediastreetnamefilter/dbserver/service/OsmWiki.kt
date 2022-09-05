package org.sjoblomj.wikipediastreetnamefilter.dbserver.service

import de.topobyte.osm4j.core.model.iface.OsmEntity
import de.topobyte.osm4j.core.model.iface.OsmNode
import de.topobyte.osm4j.core.model.iface.OsmRelation
import de.topobyte.osm4j.core.model.iface.OsmWay
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service

@Service
class OsmWiki : FeatureExtractorInterface {
	private val logger = LoggerFactory.getLogger(javaClass)

	private val nodeCategory: Category = "node"
	private val wayCategory: Category = "way"
	private val relationCategory: Category = "relation"
	private val minLon = 11.6000
	private val maxLon = 12.3000
	private val minLat = 57.5000
	private val maxLat = 57.9000

	private var shouldRun = true

	private val nodes = hashMapOf<Long, OsmNode>()
	private val ways = hashMapOf<Long, OsmWay>()
	private val relations = hashMapOf<Long, OsmRelation>()

	override fun shouldRunConsumptionRound() = shouldRun
	override fun finishConsumptionRound() {
		shouldRun = false
	}

	override fun getCategoriesToBePersisted(): Collection<Category> = listOf(nodeCategory, wayCategory, relationCategory)

	override fun getNodesAndCategoriesToBePersisted(): Map<OsmNode, Collection<Category>> = associateWithCategories(nodes.values, nodeCategory)
	override fun getWaysAndCategoriesToBePersisted(): Map<OsmWay, Collection<Category>> = associateWithCategories(ways.values, wayCategory)
	override fun getRelationsAndCategoriesToBePersisted(): Map<OsmRelation, Collection<Category>> = associateWithCategories(relations.values, relationCategory)
	private fun <T : OsmEntity> associateWithCategories(entities: MutableCollection<T>, category: Category) =
		entities.associateWith { setOf(category) }


	override fun handle(entity: OsmNode) {
		if (entity.latitude in minLat..maxLat && entity.longitude in minLon..maxLon) {
			logger.debug("Adding node ${entity.id}")
			nodes[entity.id] = entity
		}
	}

	override fun handle(entity: OsmWay) {
		val nodeIds = (0 until entity.numberOfNodes).map { entity.getNodeId(it) }
		if (nodeIds.any { nodes.keys.contains(it) } ) {
			logger.debug("Adding way ${entity.id}")
			ways[entity.id] = entity
		}
	}

	override fun handle(entity: OsmRelation) {
		relations[entity.id] = entity
	}


	override fun getNode(id: Long) = getEntity(id, nodes)
	override fun getWay(id: Long) = getEntity(id, ways)
	override fun getRelation(id: Long) = getEntity(id, relations)

	private inline fun <reified T> getEntity(id: Long, map: Map<Long, T>): T? {
		val entity = map[id]
		if (entity == null)
			logger.warn("Found no ${T::class.java.simpleName} with id $id")
		return entity
	}
}
