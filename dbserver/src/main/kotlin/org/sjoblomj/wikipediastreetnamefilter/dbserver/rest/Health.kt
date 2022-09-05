package org.sjoblomj.wikipediastreetnamefilter.dbserver.rest

import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.CrossOrigin
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController

@CrossOrigin
@RestController
class Health {

	var isReady = false

	@GetMapping("/isRunning")
	fun isRunning(): ResponseEntity<Unit> {
		return ResponseEntity(HttpStatus.OK)
	}

	@GetMapping("/isReady")
	fun isReady(): ResponseEntity<Unit> {
		if (!isReady)
			return ResponseEntity(HttpStatus.SERVICE_UNAVAILABLE)
		return ResponseEntity(HttpStatus.OK)
	}
}
