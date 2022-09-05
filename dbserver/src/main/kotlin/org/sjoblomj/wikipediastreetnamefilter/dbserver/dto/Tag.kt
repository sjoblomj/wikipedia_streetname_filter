package org.sjoblomj.wikipediastreetnamefilter.dbserver.dto

import java.io.Serializable
import javax.persistence.*

@Entity
@IdClass(TagId::class)
@Table(name = "tags")
data class Tag(
	@Id
	val id: Long = 0,

	@Id
	val key: String = "",

	@Column(nullable = false)
	val value: String = ""
)

data class TagId(val id: Long = 0, val key: String = "") : Serializable
