package org.sjoblomj.wikipediastreetnamefilter.dbserver.service

import de.topobyte.osm4j.core.access.OsmHandler
import de.topobyte.osm4j.core.model.iface.OsmBounds
import de.topobyte.osm4j.core.model.iface.OsmNode
import de.topobyte.osm4j.core.model.iface.OsmRelation
import de.topobyte.osm4j.core.model.iface.OsmWay
import de.topobyte.osm4j.core.resolve.OsmEntityProvider

interface FeatureExtractorInterface : OsmHandler, OsmEntityProvider {
	fun maxConsumptionRounds(): Int = 10

	fun shouldRunConsumptionRound(): Boolean
	fun startConsumptionRound() {}
	fun finishConsumptionRound() {}

	fun getCategoriesToBePersisted(): Collection<Category>
	fun getNodesAndCategoriesToBePersisted(): Map<OsmNode, Collection<Category>>
	fun getWaysAndCategoriesToBePersisted(): Map<OsmWay, Collection<Category>>
	fun getRelationsAndCategoriesToBePersisted(): Map<OsmRelation, Collection<Category>>


	/**
	 * Default empty implementation of function from [OsmHandler]
	 */
	override fun handle(bounds: OsmBounds) {}

	/**
	 * Default empty implementation of function from [OsmHandler]
	 */
	override fun complete() {}
}

typealias Category = String
