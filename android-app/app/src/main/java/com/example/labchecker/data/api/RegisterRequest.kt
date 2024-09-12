package com.example.labchecker.data.api

data class RegisterRequest(
    val name: String,
    val surname: String,
    val patronymic: String,
    val github: String,
)