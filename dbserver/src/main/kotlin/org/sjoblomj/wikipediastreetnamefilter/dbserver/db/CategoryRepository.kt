package org.sjoblomj.wikipediastreetnamefilter.dbserver.db

import org.sjoblomj.wikipediastreetnamefilter.dbserver.dto.CategoryEntity
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface CategoryRepository : JpaRepository<CategoryEntity, Long>
