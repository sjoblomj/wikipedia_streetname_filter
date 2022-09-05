package org.sjoblomj.wikipediastreetnamefilter.dbserver.dto

import org.locationtech.jts.geom.Geometry
import javax.persistence.*

@Entity
@Table(name = "geoentries")
data class GeoEntity(
	@Id
	val id: Long,

	@Column(nullable = false)
	val geom: Geometry,

	@Column
	@ElementCollection
	val category: Collection<Int>
)
