package org.sjoblomj.wikipediastreetnamefilter.dbserver.db

import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.GeoEntity
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.CrudRepository
import org.springframework.stereotype.Repository
import org.springframework.transaction.annotation.Transactional

@Repository
interface NativeQueryRepository : CrudRepository<GeoEntity, Long> {

	@Transactional
	@Modifying
	@Query("UPDATE geoentries g SET id = g.id, geom = ST_CollectionHomogenize(g.geom);", nativeQuery = true)
	fun homogenizeAllGeoms()

	@Transactional
	@Modifying
	@Query("CREATE INDEX IF NOT EXISTS geo_entity_category_index ON geo_entity_category(geo_entity_id);", nativeQuery = true)
	fun createGeoEntryCategoryIndex()

	@Transactional
	@Modifying
	@Query("CREATE TABLE IF NOT EXISTS hide_ids(id bigint);", nativeQuery = true)
	fun createHideIdsTable()
}
