package org.sjoblomj.wikipediastreetnamefilter.dbserver.db

import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.Tag
import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.TagId
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository

@Repository
interface TagRepository : JpaRepository<Tag, TagId> {

	@Query("SELECT * FROM tags WHERE (key = 'name' OR key = 'alt_name') AND LOWER(value) = LOWER(:name)",
		nativeQuery = true)
	fun findAllByName(@Param("name") name: String): List<Tag>

	@Query("SELECT * FROM tags WHERE id = :id", nativeQuery = true)
	fun findAllById(@Param("id") id: Long): List<Tag>
}
