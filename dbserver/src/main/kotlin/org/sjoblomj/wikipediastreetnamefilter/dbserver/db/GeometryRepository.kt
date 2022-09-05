package org.sjoblomj.wikipediastreetnamefilter.dbserver.db

import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.GeoEntity
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface GeometryRepository : JpaRepository<GeoEntity, Long>
