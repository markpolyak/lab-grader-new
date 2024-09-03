package com.example.labchecker.data.api

import com.example.labchecker.data.entity.Groups
import com.example.labchecker.data.entity.Labs
import com.example.labchecker.data.entity.Message
import com.example.labchecker.data.entity.Subject
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface CoursesService {
    @GET("courses/")
    suspend fun getSubjects(): List<Subject>

    @GET("courses/{course_id}/groups")
    suspend fun getGroups(@Path("course_id") courseId: String): Groups

    @GET("courses/{course_id}/groups/{group_id}/labs")
    suspend fun getLabs(@Path("course_id") courseId: String,
                        @Path("group_id") groupId: String): Labs

    @POST("courses/{course_id}/groups/{group_id}/labs/{lab_id}/grade")
    suspend fun grade(
        @Path("course_id") courseId: String,
        @Path("group_id") groupId: String,
        @Path("lab_id") labId: String,
        @Body request: GithubRequest
    ): Response<Message>

    @POST("courses/{course_id}/groups/{group_id}/register")
    suspend fun register(
        @Path("course_id") courseId: String,
        @Path("group_id") groupId: String,
        @Body request: RegisterRequest
    ): Response<Message>
}